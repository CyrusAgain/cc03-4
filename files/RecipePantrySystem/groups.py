
from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import current_user, login_required
from db import get_db
from recipes import list_recipes

bp = Blueprint("groups", __name__, url_prefix="/groups")

MAX_GROUP_NAME = 60

def list_groups(user_id):
    
    db = get_db()
    groups = db.execute(
        "SELECT * FROM recipe_group WHERE user_id = ? ORDER BY group_name", (user_id,)
    ).fetchall()
    return [{"row": g, "members": _group_items(db, g["group_id"])} for g in groups]


def _group_items(db, group_id):
    return db.execute(
        """SELECT gi.recipe_id, gi.servings, r.recipe_name
           FROM recipe_group_item gi JOIN recipe r ON r.recipe_id = gi.recipe_id
           WHERE gi.group_id = ? ORDER BY r.recipe_name""",
        (group_id,),
    ).fetchall()


def get_group(user_id, group_id):
    if group_id is None:
        return None
    db = get_db()
    g = db.execute(
        "SELECT * FROM recipe_group WHERE group_id = ? AND user_id = ?", (group_id, user_id)
    ).fetchone()
    if g is None:
        return None
    return {"row": g, "members": _group_items(db, group_id)}


def group_pairs(group):
    return [(i["recipe_id"], i["servings"]) for i in group["members"]]


def save_group(user_id, name, pairs):
    
    db = get_db()
    try:
        existing = db.execute(
            "SELECT group_id FROM recipe_group WHERE user_id = ? AND group_name = ?", (user_id, name)
        ).fetchone()
        if existing:
            group_id, created = existing["group_id"], False
            db.execute("UPDATE recipe_group SET group_name = ? WHERE group_id = ?", (name, group_id))
            db.execute("DELETE FROM recipe_group_item WHERE group_id = ?", (group_id,))
        else:
            cur = db.execute(
                "INSERT INTO recipe_group (user_id, group_name) VALUES (?, ?)", (user_id, name)
            )
            group_id, created = cur.lastrowid, True
        for recipe_id, servings in pairs:
            db.execute(
                "INSERT INTO recipe_group_item (group_id, recipe_id, servings) VALUES (?, ?, ?)",
                (group_id, recipe_id, servings),
            )
        db.commit()
        return group_id, created
    except Exception:
        db.rollback()
        raise


def delete_group(user_id, group_id):
    db = get_db()
    db.execute("DELETE FROM recipe_group WHERE group_id = ? AND user_id = ?", (group_id, user_id))
    db.commit()

def encode_pairs(pairs):
    
    return ["%d:%d" % (rid, s) for rid, s in pairs]


def _dedupe(pairs):
    seen, out = set(), []
    for rid, s in pairs:
        if rid not in seen:
            seen.add(rid)
            out.append((rid, s))
    return out


def pairs_from_values(values):
    
    pairs = []
    for raw in values.getlist("r"):
        try:
            rid, s = raw.split(":")
            rid, s = int(rid), int(s)
        except ValueError:
            continue
        if s >= 1:
            pairs.append((rid, s))
    if not pairs:
        rid, s = values.get("recipe_id", type=int), values.get("servings", type=int)
        if rid and s and s >= 1:
            pairs.append((rid, s))
    return _dedupe(pairs)


def resolve_selection(user_id, values):
    
    group_id = values.get("group", type=int)
    if group_id is not None:
        group = get_group(user_id, group_id)
        if group is None:
            return [], None, "That group could not be found."
        pairs = group_pairs(group)
        if not pairs:
            return [], group, "That group has no recipes left in it."
        return pairs, group, None
    pairs = pairs_from_values(values)
    if not pairs:
        return [], None, "Choose at least one recipe."
    return pairs, None, None


def picks_from_form(form, recipes):
    
    picked = set(form.getlist("pick"))
    pairs, errors, prefill = [], [], {}
    for r in recipes:
        rid = r["row"]["recipe_id"]
        raw = form.get("servings_%d" % rid, "").strip() or str(r["row"]["servings"])
        is_picked = str(rid) in picked
        prefill[rid] = {"picked": is_picked, "servings": raw}
        if not is_picked:
            continue
        try:
            servings = int(raw)
            if servings < 1:
                raise ValueError
        except ValueError:
            errors.append("Enter servings as a whole number of 1 or more for %s." % r["row"]["recipe_name"])
            continue
        pairs.append((rid, servings))
    return pairs, errors, prefill


def prefill_from_pairs(recipes, pairs):
    chosen = dict(pairs)
    return {
        r["row"]["recipe_id"]: {
            "picked": r["row"]["recipe_id"] in chosen,
            "servings": str(chosen.get(r["row"]["recipe_id"], r["row"]["servings"])),
        }
        for r in recipes
    }


def select_page(user_id, recipes, prefill, group_name=""):
    
    return render_template(
        "check_select.html",
        recipes=recipes,
        groups=list_groups(user_id),
        prefill=prefill,
        group_name=group_name,
    )

@bp.route("/save", methods=["POST"])
@login_required
def save():
    user_id = current_user()["user_id"]
    recipes = list_recipes(user_id)
    pairs, errors, prefill = picks_from_form(request.form, recipes)
    name = request.form.get("group_name", "").strip()
    has_serving_errors = bool(errors)

    if not name:
        errors.append("Give the group a name.")
    elif len(name) > MAX_GROUP_NAME:
        errors.append("Keep the group name to %d characters or fewer." % MAX_GROUP_NAME)
    if len(pairs) < 2 and not has_serving_errors:
        errors.append("A group needs at least 2 recipes. Tick more recipes first.")

    if errors:
        for e in errors:
            flash(e, "error")
        return select_page(user_id, recipes, prefill, group_name=name)

    _, created = save_group(user_id, name, pairs)
    flash('Group "%s" %s.' % (name, "saved" if created else "updated"), "ok")
    return redirect(url_for("check.select_recipe"))


@bp.route("/<int:group_id>/delete", methods=["POST"])
@login_required
def delete(group_id):
    delete_group(current_user()["user_id"], group_id)
    flash("Group deleted.", "ok")
    return redirect(url_for("check.select_recipe"))
