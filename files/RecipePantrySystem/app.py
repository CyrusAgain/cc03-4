"""Recipe Pantry System -- Python (Flask) application.

Everything is Python: the pages live in ui_templates.py, the styling in ui_styles.py and the
database tables in schema.py. It runs inside XAMPP (Apache + MySQL) through app.cgi -- see
XAMPP_SETUP.md -- or on its own with:  flask --app app run --debug
"""
import os
import secrets

from flask import Flask, Response, render_template, request, url_for
from jinja2 import DictLoader

import db
from auth import bp as auth_bp, current_user, login_required
from pantry import bp as pantry_bp, list_pantry_items
from recipes import bp as recipes_bp, list_recipes
from ui_styles import CSS_VERSION, build_stylesheet
from ui_templates import TEMPLATES


def _secret_key(instance_path):
    """SECRET_KEY from the environment, else a random key saved in instance/secret.key.
    It must survive restarts: under XAMPP every request runs in a fresh Python process."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    path = os.path.join(instance_path, "secret.key")
    try:
        with open(path, "r", encoding="utf-8") as f:
            key = f.read().strip()
        if key:
            return key
    except OSError:
        pass
    key = secrets.token_hex(32)
    with open(path, "w", encoding="utf-8") as f:
        f.write(key)
    return key


def create_app(test_config=None):
    app = Flask(__name__)
    app.jinja_loader = DictLoader(TEMPLATES)          # pages come from ui_templates.py
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY="test-key" if test_config else _secret_key(app.instance_path),
        SESSION_COOKIE_NAME="recipe_pantry_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        DB_BACKEND=os.environ.get("RECIPEPANTRY_DB_BACKEND", "mysql"),
        MYSQL_HOST=os.environ.get("RECIPEPANTRY_DB_HOST", "127.0.0.1"),
        MYSQL_PORT=int(os.environ.get("RECIPEPANTRY_DB_PORT", "3306")),
        MYSQL_DATABASE=os.environ.get("RECIPEPANTRY_DB_NAME", "recipe_pantry"),
        MYSQL_USER=os.environ.get("RECIPEPANTRY_DB_USER", "root"),
        MYSQL_PASSWORD=os.environ.get("RECIPEPANTRY_DB_PASSWORD", ""),
        DATABASE=os.path.join(app.instance_path, "recipe_pantry.sqlite"),   # SQLite mode only
    )
    if test_config:
        app.config.update(test_config)
        if "DATABASE" in test_config and "DB_BACKEND" not in test_config:
            app.config["DB_BACKEND"] = "sqlite"

    db.init_app(app)

    @app.context_processor
    def inject_globals():
        try:
            logged_in = current_user() is not None
        except db.DatabaseUnavailable:
            logged_in = False
        return {"logged_in_nav": logged_in, "css_version": CSS_VERSION}

    @app.route("/theme.css")
    def stylesheet():
        """The whole stylesheet, generated from ui_styles.py."""
        css = build_stylesheet(url_for("static", filename="webfonts/fa-solid-900.woff2"))
        resp = Response(css, mimetype="text/css")
        if request.args.get("v") == CSS_VERSION:      # versioned URL -> safe to cache for a long time
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            resp.headers["Cache-Control"] = "no-cache"
        return resp

    @app.errorhandler(db.DatabaseUnavailable)
    def database_unavailable(error):
        return render_template("error_database.html", message=str(error)), 503

    app.register_blueprint(auth_bp)
    app.register_blueprint(pantry_bp)
    app.register_blueprint(recipes_bp)

    from check import bp as check_bp
    from groups import bp as groups_bp
    app.register_blueprint(check_bp)
    app.register_blueprint(groups_bp)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        pantry_items = list_pantry_items(user["user_id"])
        recipes = list_recipes(user["user_id"])
        return render_template(
            "dashboard.html",
            user=user,
            pantry_count=len(pantry_items),
            recipe_count=len(recipes),
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
