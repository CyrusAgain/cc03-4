
from datetime import date

from check import check_ingredient_availability
from pantry import list_pantry_items
from recipes import list_recipes

ALMOST_MAX_MISSING = 3
MIN_COVERED = 0.5
PICKS_NEED_MORE_THAN = 5
PICKS_COUNT = 3
ALMOST_SHOWN = 6
EXPIRY_WINDOW_DAYS = 7


def _days_left(expiry_text, today):
    
    if not expiry_text:
        return None
    try:
        return (date.fromisoformat(str(expiry_text)[:10]) - today).days
    except ValueError:
        return None


def _when(days):
    if days == 0:
        return "today"
    return "in %d day%s" % (days, "" if days == 1 else "s")


def _describe_dish(user_id, recipe_row, expiry_by_ingredient, today):
    recipe, report = check_ingredient_availability(
        recipe_row["recipe_id"], user_id, recipe_row["servings"]
    )
    rows = report["rows"]
    total = len(rows)
    missing = report["missing"]
    covered = total - len(missing)


    expiring = []
    for r in rows:
        days = _days_left(expiry_by_ingredient.get(r["ingredient_id"]), today)
        if r["have"] > 0 and days is not None and 0 <= days <= EXPIRY_WINDOW_DAYS:
            expiring.append({"name": r["ingredient_name"], "days": days})
    expiring.sort(key=lambda e: e["days"])

    fraction = covered / total if total else 0.0
    ready = not missing
    score = (100 if ready else 0) + fraction * 50 + 12 * len(expiring) - 6 * len(missing)

    if ready and expiring:
        reason = "You have everything, and it uses %s before it expires (%s)." % (
            expiring[0]["name"], _when(expiring[0]["days"]))
    elif ready:
        reason = "You have everything you need."
    else:
        reason = "You are only missing %s." % ", ".join(m["ingredient_name"] for m in missing)
        if expiring:
            reason += " It also uses %s, which expires %s." % (
                expiring[0]["name"], _when(expiring[0]["days"]))

    expiry_note = ""
    if expiring:
        expiry_note = "Uses %s, which expires %s." % (expiring[0]["name"], _when(expiring[0]["days"]))

    return {
        "recipe_id": recipe_row["recipe_id"],
        "name": recipe_row["recipe_name"],
        "servings": recipe_row["servings"],
        "key": "%d:%d" % (recipe_row["recipe_id"], recipe_row["servings"]),
        "total": total,
        "covered": covered,
        "percent": int(round(fraction * 100)),
        "ready": ready,
        "missing": [
            {"name": m["ingredient_name"], "shortage": m["shortage"], "unit": m["unit"]}
            for m in missing
        ],
        "expiring": expiring,
        "expiry_note": expiry_note,
        "reason": reason,
        "score": score,
    }


def build_dish_ideas(user_id, today=None):
    
    today = today or date.today()
    recipes = list_recipes(user_id)
    pantry = list_pantry_items(user_id)
    ideas = {
        "recipe_count": len(recipes),
        "pantry_count": len(pantry),
        "ready": [], "almost": [], "almost_hidden": 0, "any_close": False,
        "picks": None,
    }
    if not recipes or not pantry:
        return ideas

    expiry = {p["ingredient_id"]: p["expiry_date"] for p in pantry}
    dishes = [_describe_dish(user_id, r["row"], expiry, today) for r in recipes]

    close = [
        d for d in dishes
        if d["ready"] or (len(d["missing"]) <= ALMOST_MAX_MISSING and d["covered"] / d["total"] >= MIN_COVERED)
    ]

    picks = []
    if len(recipes) > PICKS_NEED_MORE_THAN:
        picks = sorted(close, key=lambda d: (-d["score"], d["name"].lower()))[:PICKS_COUNT]
        ideas["picks"] = picks

    picked_ids = {d["recipe_id"] for d in picks}
    rest = [d for d in close if d["recipe_id"] not in picked_ids]
    ideas["ready"] = sorted(
        (d for d in rest if d["ready"]), key=lambda d: (-len(d["expiring"]), d["name"].lower())
    )
    almost = sorted(
        (d for d in rest if not d["ready"]),
        key=lambda d: (len(d["missing"]), -d["percent"], d["name"].lower()),
    )
    ideas["almost"] = almost[:ALMOST_SHOWN]
    ideas["almost_hidden"] = max(0, len(almost) - ALMOST_SHOWN)
    ideas["any_close"] = bool(close)
    return ideas
