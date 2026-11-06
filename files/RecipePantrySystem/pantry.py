
from datetime import date
from math import isfinite

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import current_user, login_required
from db import get_db

bp = Blueprint("pantry", __name__, url_prefix="/pantry")

def list_pantry_items(user_id):
    return get_db().execute(
        """SELECT p.pantry_item_id, p.quantity_on_hand, p.expiry_date,
                  i.ingredient_id, i.ingredient_name, i.unit
           FROM pantry_item p JOIN ingredient i ON i.ingredient_id = p.ingredient_id
           WHERE p.user_id = ?
           ORDER BY i.ingredient_name""",
        (user_id,),
    ).fetchall()


def find_ingredient_by_name(db, name):
    return db.execute(
        "SELECT * FROM ingredient WHERE ingredient_name = ? COLLATE NOCASE", (name,)
    ).fetchone()


def get_or_create_ingredient(db, name, unit):
    row = find_ingredient_by_name(db, name)
    if row is not None:
        return row["ingredient_id"]
    cur = db.execute(
        "INSERT INTO ingredient (ingredient_name, unit) VALUES (?, ?)", (name, unit)
    )
    return cur.lastrowid


def add_or_update_pantry_item(user_id, ingredient_name, quantity, unit, expiry_date=None):
    
    db = get_db()
    ingredient_id = get_or_create_ingredient(db, ingredient_name, unit)
    existing = db.execute(
        "SELECT * FROM pantry_item WHERE user_id = ? AND ingredient_id = ?",
        (user_id, ingredient_id),
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE pantry_item SET quantity_on_hand = ?, expiry_date = ? WHERE pantry_item_id = ?",
            (quantity, expiry_date, existing["pantry_item_id"]),
        )
    else:
        db.execute(
            """INSERT INTO pantry_item (user_id, ingredient_id, quantity_on_hand, expiry_date)
               VALUES (?, ?, ?, ?)""",
            (user_id, ingredient_id, quantity, expiry_date),
        )
    db.commit()


def delete_pantry_item(user_id, pantry_item_id):
    db = get_db()
    db.execute(
        "DELETE FROM pantry_item WHERE pantry_item_id = ? AND user_id = ?",
        (pantry_item_id, user_id),
    )
    db.commit()


def apply_cooking(user_id, flagged_requirements):
    
    db = get_db()
    changes, low = [], []
    for item in flagged_requirements:
        if item["pantry_item_id"] is None:
            continue
        row = db.execute(
            "SELECT * FROM pantry_item WHERE pantry_item_id = ?", (item["pantry_item_id"],)
        ).fetchone()
        before = row["quantity_on_hand"]
        after = max(0.0, round(before - item["have_used"], 3))
        db.execute(
            "UPDATE pantry_item SET quantity_on_hand = ? WHERE pantry_item_id = ?",
            (after, row["pantry_item_id"]),
        )
        changes.append({"name": item["ingredient_name"], "unit": item["unit"], "before": before, "after": after})

        if after <= 0 or after < item["have_used"]:
            low.append({"name": item["ingredient_name"], "unit": item["unit"], "quantity": after})
    db.commit()
    return changes, low


def receive_purchased(user_id, purchases):
    db = get_db()
    try:
        for purchase in purchases:
            quantity = float(purchase["quantity"])
            if quantity <= 0:
                continue
            ingredient_id = get_or_create_ingredient(
                db, purchase["ingredient_name"], purchase["unit"]
            )
            existing = db.execute(
                "SELECT pantry_item_id FROM pantry_item WHERE user_id = ? AND ingredient_id = ?",
                (user_id, ingredient_id),
            ).fetchone()
            if existing:
                db.execute(
                    "UPDATE pantry_item SET quantity_on_hand = quantity_on_hand + ? WHERE pantry_item_id = ?",
                    (quantity, existing["pantry_item_id"]),
                )
            else:
                db.execute(
                    "INSERT INTO pantry_item (user_id, ingredient_id, quantity_on_hand) VALUES (?, ?, ?)",
                    (user_id, ingredient_id, quantity),
                )
        db.commit()
    except Exception:
        db.rollback()
        raise

@bp.route("/")
@login_required
def list_view():
    user_id = current_user()["user_id"]
    items = list_pantry_items(user_id)


    from suggestions import build_dish_ideas
    return render_template("pantry.html", items=items, ideas=build_dish_ideas(user_id))


@bp.route("/<int:pantry_item_id>/delete", methods=["POST"])
@login_required
def delete(pantry_item_id):
    delete_pantry_item(current_user()["user_id"], pantry_item_id)
    flash("Ingredient deleted.", "ok")
    return redirect(url_for("pantry.list_view"))

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_item():
    if request.method == "GET":
        return render_template("pantry_form.html", values={})

    name = request.form.get("name", "").strip()
    qty_raw = request.form.get("quantity", "").strip()
    unit = request.form.get("unit", "").strip()
    expiry = request.form.get("expiry_date", "").strip() or None
    values = {"name": name, "quantity": qty_raw, "unit": unit, "expiry_date": expiry}

    errors = []
    try:
        quantity = float(qty_raw)
        if not isfinite(quantity) or quantity < 0:
            errors.append("Enter a quantity of 0 or more.")
    except ValueError:
        errors.append("Enter a quantity of 0 or more.")
        quantity = None
    if not name:
        errors.append("Enter the ingredient name.")
    if expiry:
        try:
            date.fromisoformat(expiry)
        except ValueError:
            errors.append("Enter a valid expiry date.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("pantry_form.html", values=values)

    add_or_update_pantry_item(current_user()["user_id"], name, quantity, unit, expiry)
    flash("Ingredient saved.", "ok")
    return redirect(url_for("pantry.list_view"))
