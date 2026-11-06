import re
from functools import wraps
import secrets
import time

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
RESET_CODE_TTL_MINUTES = 15


def hash_password(password):
    
    if current_app.config.get("DB_BACKEND", "mysql") == "mysql":
        import bcrypt
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("ascii")
        return hashed.replace("$2b$", "$2y$", 1)
    return generate_password_hash(password)


def verify_password(password, stored_hash):
    
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            import bcrypt
            bcrypt_hash = stored_hash.replace("$2y$", "$2b$", 1)
            return bcrypt.checkpw(password.encode("utf-8"), bcrypt_hash.encode("ascii"))
        except (ImportError, ValueError, TypeError):
            return False
    try:
        return check_password_hash(stored_hash, password)
    except (ValueError, TypeError):
        return False

def current_user():
    
    if "user" not in g:
        user_id = session.get("user_id")
        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                "SELECT * FROM user_account WHERE user_id = ?", (user_id,)
            ).fetchone()
    return g.user


def login_required(view):
    
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("auth.login", next=request.script_root + request.path))
        return view(*args, **kwargs)
    return wrapped

@bp.route("/")
def landing():
    if current_user() is not None:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", values={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")
    values = {"name": name, "email": email}

    errors = []
    if not name or not email or not password or not confirm:
        errors.append("Fill in every field.")
    else:
        if not EMAIL_RE.match(email):
            errors.append("Enter a valid email address.")
        if len(password) < 8:
            errors.append("Use a password with at least 8 characters.")
        if len(password.encode("utf-8")) > 72:
            errors.append("Use a password no longer than 72 bytes.")
        if password != confirm:
            errors.append("The passwords do not match.")

    db = get_db()
    if not errors and db.execute(
        "SELECT 1 FROM user_account WHERE email = ?", (email,)
    ).fetchone():
        errors.append("That email is already registered. Log in instead, or use a different email.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("signup.html", values=values)

    db.execute(
        "INSERT INTO user_account (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, hash_password(password)),
    )
    db.commit()
    flash("Account created successfully. Log in to get started.", "ok")
    return redirect(url_for("auth.login"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", values={})

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_db().execute(
        "SELECT * FROM user_account WHERE email = ?", (email,)
    ).fetchone()

    if user is None or not verify_password(password, user["password_hash"]):
        flash("Incorrect email or password.", "error")
        return render_template("login.html", values={"email": email})


    if current_app.config.get("DB_BACKEND", "mysql") == "mysql" and not user["password_hash"].startswith(("$2a$", "$2b$", "$2y$")):
        db = get_db()
        db.execute(
            "UPDATE user_account SET password_hash = ? WHERE user_id = ?",
            (hash_password(password), user["user_id"]),
        )
        db.commit()

    session.clear()
    session["user_id"] = user["user_id"]
    nxt = request.args.get("next", "")
    # only follow same-site relative paths (blocks //evil.com and http://evil.com)
    if not nxt.startswith("/") or nxt.startswith("//") or "\\" in nxt:
        nxt = url_for("dashboard")
    return redirect(nxt)

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html", step=1, values={})

    email = request.form.get("email", "").strip().lower()
    user = get_db().execute(
        "SELECT * FROM user_account WHERE email = ?", (email,)
    ).fetchone()
    if user is None:
        flash("We could not find an account with that email.", "error")
        return render_template("forgot_password.html", step=1, values={"email": email})


    code = "%06d" % secrets.randbelow(1_000_000)
    session["reset"] = {
        "email": email,
        "code": code,
        "expires": time.time() + RESET_CODE_TTL_MINUTES * 60,
    }
    flash("A reset code was generated.", "ok")
    return render_template("forgot_password.html", step=2, demo_code=code, values={})


@bp.route("/forgot-password/reset", methods=["POST"])
def forgot_password_reset():
    reset = session.get("reset")
    code = request.form.get("code", "").strip()
    password = request.form.get("password", "")

    valid = (
        reset is not None
        and secrets.compare_digest(code, str(reset.get("code", "")))
        and time.time() < float(reset.get("expires", 0))
        and len(password) >= 8
        and len(password.encode("utf-8")) <= 72
    )
    if not valid:
        flash("The code or password is not valid.", "error")
        return render_template("forgot_password.html", step=2, demo_code=(reset or {}).get("code"), values={})

    db = get_db()
    db.execute(
        "UPDATE user_account SET password_hash = ? WHERE email = ?",
        (hash_password(password), reset["email"]),
    )
    db.commit()
    session.pop("reset", None)
    flash("Password changed. Log in with your new password.", "ok")
    return redirect(url_for("auth.login"))

@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
