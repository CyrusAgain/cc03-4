
from math import isfinite

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import current_user, login_required
from db import get_db
from pantry import get_or_create_ingredient

bp = Blueprint("recipes", __name__, url_prefix="/recipes")

def list_recipes(user_id):
    db = get_db()
    recipes = db.execute(
        "SELECT * FROM recipe WHERE user_id = ? ORDER BY recipe_name", (user_id,)
    ).fetchall()
    out = []
    for r in recipes:
        items = db.execute(
            """SELECT i.ingredient_name FROM recipe_ingredient ri
               JOIN ingredient i ON i.ingredient_id = ri.ingredient_id
               WHERE ri.recipe_id = ? ORDER BY i.ingredient_name""",
            (r["recipe_id"],),
        ).fetchall()
        out.append({"row": r, "ingredient_names": [i["ingredient_name"] for i in items]})
    return out


def get_recipe_with_items(recipe_id, user_id):
    db = get_db()
    recipe = db.execute(
        "SELECT * FROM recipe WHERE recipe_id = ? AND user_id = ?", (recipe_id, user_id)
    ).fetchone()
    if recipe is None:
        return None, []
    items = db.execute(
        """SELECT ri.*, i.ingredient_name, i.unit FROM recipe_ingredient ri
           JOIN ingredient i ON i.ingredient_id = ri.ingredient_id
           WHERE ri.recipe_id = ? ORDER BY ri.recipe_ingredient_id""",
        (recipe_id,),
    ).fetchall()
    return recipe, items


def save_recipe(user_id, recipe_name, servings, items, recipe_id=None):
    
    db = get_db()
    try:
        if recipe_id is None:
            cur = db.execute(
                "INSERT INTO recipe (user_id, recipe_name, servings) VALUES (?, ?, ?)",
                (user_id, recipe_name, servings),
            )
            recipe_id = cur.lastrowid
        else:
            db.execute(
                "UPDATE recipe SET recipe_name = ?, servings = ? WHERE recipe_id = ? AND user_id = ?",
                (recipe_name, servings, recipe_id, user_id),
            )
            db.execute("DELETE FROM recipe_ingredient WHERE recipe_id = ?", (recipe_id,))

        for it in items:
            ingredient_id = get_or_create_ingredient(db, it["name"], it["unit"])
            db.execute(
                """INSERT INTO recipe_ingredient (recipe_id, ingredient_id, quantity_needed)
                   VALUES (?, ?, ?)""",
                (recipe_id, ingredient_id, it["quantity"]),
            )
        db.commit()
        return recipe_id
    except Exception:
        db.rollback()
        raise


def delete_recipe(user_id, recipe_id):
    db = get_db()
    db.execute("DELETE FROM recipe WHERE recipe_id = ? AND user_id = ?", (recipe_id, user_id))
    db.commit()

@bp.route("/")
@login_required
def list_view():
    return render_template("recipes.html", recipes=list_recipes(current_user()["user_id"]))


@bp.route("/<int:recipe_id>/delete", methods=["POST"])
@login_required
def delete(recipe_id):
    delete_recipe(current_user()["user_id"], recipe_id)
    flash("Recipe deleted.", "ok")
    return redirect(url_for("recipes.list_view"))

def _collect_items_from_form():
    names = request.form.getlist("ingredient_name")
    qtys = request.form.getlist("ingredient_quantity")
    units = request.form.getlist("ingredient_unit")
    items, errors = [], []
    for i, (name, qty_raw, unit) in enumerate(zip(names, qtys, units), start=1):
        name, unit = name.strip(), unit.strip()
        if not name and not qty_raw.strip():
            continue
        try:
            qty = float(qty_raw)
        except ValueError:
            qty = None
        if not name or qty is None or not isfinite(qty) or qty <= 0:
            errors.append("Ingredient %d needs a name and a quantity greater than 0." % i)
        else:
            items.append({"name": name, "quantity": qty, "unit": unit})
    return items, errors


def _form_to_values():
    return {
        "recipe_name": request.form.get("recipe_name", ""),
        "servings": request.form.get("servings", ""),
        "rows": list(zip(
            request.form.getlist("ingredient_name"),
            request.form.getlist("ingredient_quantity"),
            request.form.getlist("ingredient_unit"),
        )),
    }


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_recipe():
    if request.method == "GET":
        return render_template("recipe_form.html", recipe_id=None, values={"rows": [("", "", "")] * 3})
    return _save_from_form(recipe_id=None)


@bp.route("/<int:recipe_id>/edit", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    user_id = current_user()["user_id"]
    recipe, items = get_recipe_with_items(recipe_id, user_id)
    if recipe is None:
        flash("That recipe could not be found.", "error")
        return redirect(url_for("recipes.list_view"))

    if request.method == "GET":
        values = {
            "recipe_name": recipe["recipe_name"],
            "servings": str(recipe["servings"]),
            "rows": [(i["ingredient_name"], str(i["quantity_needed"]), i["unit"]) for i in items],
        }
        return render_template("recipe_form.html", recipe_id=recipe_id, values=values)
    return _save_from_form(recipe_id=recipe_id)


def _save_from_form(recipe_id):
    user_id = current_user()["user_id"]
    recipe_name = request.form.get("recipe_name", "").strip()
    servings_raw = request.form.get("servings", "").strip()
    items, errors = _collect_items_from_form()

    if not recipe_name:
        errors.append("Enter the recipe name.")
    try:
        servings = int(servings_raw)
        if servings < 1:
            raise ValueError
    except ValueError:
        errors.append("Enter servings as a whole number of 1 or more.")
        servings = None
    if not items and not errors:
        errors.append("Add at least one ingredient.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("recipe_form.html", recipe_id=recipe_id, values=_form_to_values())

    save_recipe(user_id, recipe_name, servings, items, recipe_id=recipe_id)
    flash("Recipe saved.", "ok")
    return redirect(url_for("recipes.list_view"))
