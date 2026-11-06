
from math import isfinite

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth import current_user, login_required
from db import get_db
from groups import (
    encode_pairs, get_group, group_pairs, picks_from_form, prefill_from_pairs,
    resolve_selection, select_page,
)
from pantry import apply_cooking, receive_purchased
from recipes import get_recipe_with_items, list_recipes

bp = Blueprint("check", __name__)

def get_recipe_requirements(recipe_id, user_id, servings_wanted):
    
    recipe, items = get_recipe_with_items(recipe_id, user_id)
    if recipe is None:
        return None, []
    factor = servings_wanted / recipe["servings"]
    requirements = [
        {
            "ingredient_id": i["ingredient_id"],
            "ingredient_name": i["ingredient_name"],
            "unit": i["unit"],
            "quantity_needed": round(i["quantity_needed"] * factor, 3),
        }
        for i in items
    ]
    return recipe, requirements

def match_ingredients(user_id, requirements):
    
    db = get_db()
    pairs = []
    for req in requirements:
        pantry_row = db.execute(
            "SELECT * FROM pantry_item WHERE user_id = ? AND ingredient_id = ?",
            (user_id, req["ingredient_id"]),
        ).fetchone()
        pairs.append((req, pantry_row))
    return pairs

def calculate_shortage(pairs):
    
    out = []
    for req, pantry_row in pairs:
        have = pantry_row["quantity_on_hand"] if pantry_row else 0.0
        shortage = round(req["quantity_needed"] - have, 3)
        out.append({**req, "have": have, "shortage": shortage,
                    "pantry_item_id": pantry_row["pantry_item_id"] if pantry_row else None})
    return out

def flag_each_ingredient(shortages):
    
    out = []
    for s in shortages:
        status = "short" if s["shortage"] > 1e-9 else "enough"
        out.append({**s, "status": status, "have_used": min(s["have"], s["quantity_needed"])})
    return out

def report_availability(flagged):
    missing = [f for f in flagged if f["status"] == "short"]
    return {"rows": flagged, "all_enough": len(missing) == 0, "missing": missing}


def check_ingredient_availability(recipe_id, user_id, servings_wanted):
    
    recipe, requirements = get_recipe_requirements(recipe_id, user_id, servings_wanted)
    if recipe is None:
        return None, None
    pairs = match_ingredients(user_id, requirements)
    shortages = calculate_shortage(pairs)
    flagged = flag_each_ingredient(shortages)
    return recipe, report_availability(flagged)

def check_selection(user_id, pairs):
    
    sections = []
    for recipe_id, servings in pairs:
        recipe, report = check_ingredient_availability(recipe_id, user_id, servings)
        if recipe is not None:
            sections.append({"recipe": recipe, "servings": servings, "report": report})
    return sections, combine_reports(sections)


def combine_reports(sections):
    
    merged = {}
    for sec in sections:
        name = sec["recipe"]["recipe_name"]
        for row in sec["report"]["rows"]:
            m = merged.get(row["ingredient_id"])
            if m is None:
                m = merged[row["ingredient_id"]] = {
                    "ingredient_id": row["ingredient_id"],
                    "ingredient_name": row["ingredient_name"],
                    "unit": row["unit"],
                    "quantity_needed": 0.0,
                    "have": row["have"],
                    "pantry_item_id": row["pantry_item_id"],
                    "used_by": [],
                    "short_alone": False,
                }
            m["quantity_needed"] += row["quantity_needed"]
            m["used_by"].append({"recipe": name, "quantity": row["quantity_needed"]})
            if row["status"] == "short":
                m["short_alone"] = True

    rows = []
    for m in merged.values():
        needed = round(m["quantity_needed"], 3)
        shortage = round(needed - m["have"], 3)
        status = "short" if shortage > 1e-9 else "enough"
        rows.append({
            **m, "quantity_needed": needed, "shortage": shortage, "status": status,
            "have_used": min(m["have"], needed),
            "only_together": status == "short" and not m["short_alone"],
        })
    if len(sections) > 1:
        rows.sort(key=lambda r: r["ingredient_name"].lower())
    report = report_availability(rows)
    report["only_together"] = [r for r in rows if r["only_together"]]
    return report


def selection_label(sections, group):
    if group is not None:
        return "%s (%d recipes)" % (group["row"]["group_name"], len(sections))
    if len(sections) == 1:
        n = sections[0]["servings"]
        return "%s, %d serving%s" % (sections[0]["recipe"]["recipe_name"], n, "" if n == 1 else "s")
    return "%d recipes" % len(sections)


def _pairs_of(sections):
    return [(s["recipe"]["recipe_id"], s["servings"]) for s in sections]

def generate_shopping_list(report, multi=False):
    
    return [
        {
            "ingredient_name": m["ingredient_name"],
            "unit": m["unit"],
            "quantity": m["shortage"],
            "needed_for": ", ".join(u["recipe"] for u in m["used_by"]) if multi else "",
        }
        for m in report["missing"]
    ]

@bp.route("/check", methods=["GET", "POST"])
@login_required
def select_recipe():
    user_id = current_user()["user_id"]
    recipes = list_recipes(user_id)
    if not recipes:
        flash("No recipes found. Create a recipe first.", "error")
        return render_template("check_select.html", recipes=[], groups=[], prefill={}, group_name="")

    if request.method == "GET":
        wanted = request.args.get("group", type=int)
        group = get_group(user_id, wanted)
        if wanted is not None and group is None:
            flash("That group could not be found.", "error")
        if group:
            return select_page(user_id, recipes, prefill_from_pairs(recipes, group_pairs(group)),
                               group_name=group["row"]["group_name"])
        return select_page(user_id, recipes, prefill_from_pairs(recipes, []))

    pairs, errors, prefill = picks_from_form(request.form, recipes)
    if not errors and not pairs:
        errors.append("Tick at least one recipe to check.")
    if errors:
        for e in errors:
            flash(e, "error")
        return select_page(user_id, recipes, prefill, group_name=request.form.get("group_name", ""))

    return redirect(url_for("check.result", r=encode_pairs(pairs)))

@bp.route("/check/result")
@login_required
def result():
    user_id = current_user()["user_id"]
    pairs, group, error = resolve_selection(user_id, request.args)
    if error:
        flash(error, "error")
        return redirect(url_for("check.select_recipe"))
    sections, combined = check_selection(user_id, pairs)
    if not sections:
        flash("Those recipes could not be found.", "error")
        return redirect(url_for("check.select_recipe"))
    return render_template(
        "check_result.html",
        sections=sections,
        report=combined,
        multi=len(sections) > 1,
        group=group,
        label=selection_label(sections, group),
        pairs=encode_pairs(_pairs_of(sections)),
    )


@bp.route("/check/cook", methods=["POST"])
@login_required
def cook():
    user_id = current_user()["user_id"]
    pairs, group, error = resolve_selection(user_id, request.form)
    sections, combined = ([], None) if error else check_selection(user_id, pairs)
    if not sections or not combined["all_enough"]:
        flash("That can no longer be cooked as-is; please check again.", "error")
        return redirect(url_for("check.select_recipe"))
    changes, low = apply_cooking(user_id, combined["rows"])
    cooked = [s["recipe"]["recipe_name"] for s in sections]
    return render_template("check_cooked.html", changes=changes, low=low, cooked=cooked)

@bp.route("/check/shopping-list", methods=["POST"])
@login_required
def to_shopping_list():
    user_id = current_user()["user_id"]
    pairs, group, error = resolve_selection(user_id, request.form)
    sections, combined = ([], None) if error else check_selection(user_id, pairs)
    if not sections:
        flash(error or "Those recipes could not be found.", "error")
        return redirect(url_for("check.select_recipe"))
    items = generate_shopping_list(combined, multi=len(sections) > 1)
    if not items:
        flash("You already have everything you need.", "ok")
        return redirect(url_for("check.result", r=encode_pairs(_pairs_of(sections))))

    session["shopping_list"] = {
        "label": selection_label(sections, group),
        "group_id": group["row"]["group_id"] if group else None,
        "pairs": [list(p) for p in _pairs_of(sections)],
        "rows": items,
    }
    return redirect(url_for("check.shopping_list"))


def _saved_list():
    
    data = session.get("shopping_list")
    if data and "pairs" not in data:
        session.pop("shopping_list", None)
        return None
    return data


@bp.route("/shopping-list")
@login_required
def shopping_list():
    data = _saved_list()
    if not data:
        flash("There is no shopping list saved right now.", "error")
        return redirect(url_for("dashboard"))
    return render_template("shopping_list.html", data=data)


@bp.route("/shopping-list/purchase", methods=["POST"])
@login_required
def purchase():
    data = _saved_list()
    if not data:
        return redirect(url_for("dashboard"))
    user_id = current_user()["user_id"]
    purchases = []
    errors = []
    for i, item in enumerate(data["rows"]):
        raw = request.form.get("qty_%d" % i, "").strip()
        try:
            qty = float(raw)
            if not isfinite(qty) or qty < 0:
                raise ValueError
        except ValueError:
            errors.append("Enter a quantity of 0 or more for %s." % item["ingredient_name"])
            continue
        purchases.append({"ingredient_name": item["ingredient_name"], "unit": item["unit"], "quantity": qty})

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("shopping_list.html", data=data)

    receive_purchased(user_id, purchases)
    session.pop("shopping_list", None)
    flash("Pantry updated. Checking again.", "ok")
    if data.get("group_id"):
        return redirect(url_for("check.result", group=data["group_id"]))
    return redirect(url_for("check.result", r=encode_pairs([tuple(p) for p in data["pairs"]])))
