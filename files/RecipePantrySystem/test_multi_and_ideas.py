
import os
import re
import sqlite3
import tempfile
from datetime import date, timedelta

from app import create_app
import db as db_module


def ok(cond, msg):
    print("ok  " if cond else "FAIL", msg)
    if not cond:
        raise SystemExit(1)


def new_app():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    with app.app_context():
        db_module.init_db()
    return app, path


def signup_login(c, email="ana@example.com"):
    c.post("/signup", data={"name": "Ana Cruz", "email": email, "password": "password1", "confirm": "password1"})
    c.post("/login", data={"email": email, "password": "password1"})


def pantry(c, name, qty, unit="", expiry=""):
    c.post("/pantry/new", data={"name": name, "quantity": str(qty), "unit": unit, "expiry_date": expiry})


def recipe(c, name, servings, items):
    
    r = c.post("/recipes/new", data={
        "recipe_name": name, "servings": str(servings),
        "ingredient_name": [i[0] for i in items],
        "ingredient_quantity": [str(i[1]) for i in items],
        "ingredient_unit": [i[2] for i in items],
    }, follow_redirects=True)
    assert b"Recipe saved" in r.data, "could not save recipe %s" % name


def rid(path, name):
    return sqlite3.connect(path).execute("SELECT recipe_id FROM recipe WHERE recipe_name=?", (name,)).fetchone()[0]


def text(r):
    return r.get_data(as_text=True)

def test_multi_and_groups():
    app, path = new_app()
    c = app.test_client()
    signup_login(c)

    pantry(c, "Eggs", 6, "pcs")
    pantry(c, "Flour", 1000, "g")
    pantry(c, "Milk", 300, "ml")

    recipe(c, "Omelette", 2, [("Eggs", 4, "pcs")])
    recipe(c, "Custard", 2, [("Eggs", 4, "pcs"), ("Milk", 200, "ml")])
    recipe(c, "Bread", 4, [("Flour", 500, "g")])
    om, cu, br = rid(path, "Omelette"), rid(path, "Custard"), rid(path, "Bread")


    r = c.get("/check")
    ok(b'name="pick"' in r.data and b'name="servings_%d"' % om in r.data, "check page has tick boxes + servings per recipe")
    ok(b"Saved groups" not in r.data and b"Planning a feast?" in r.data, "no saved groups yet; group box shown")


    r = c.post("/check", data={}, follow_redirects=True)
    ok(b"Tick at least one recipe" in r.data, "nothing ticked is rejected")

    r = c.post("/check", data={"pick": [str(om)], "servings_%d" % om: "zero"}, follow_redirects=True)
    ok(b"whole number of 1 or more for Omelette" in r.data, "bad servings rejected with the recipe's name")
    ok(re.search(r'name="pick" value="%d"\s+checked' % om, text(r)) is not None, "ticked recipe stays ticked after an error")


    r = c.post("/check", data={"pick": [str(om)], "servings_%d" % om: "2"}, follow_redirects=True)
    body = text(r)
    ok("Recipe by recipe" not in body and "Everything together" not in body, "single recipe has no multi-recipe sections")
    ok("You have enough ingredients for this recipe" in body and "Yes, cook now" in body, "single recipe: unchanged ready + cook")


    r = c.post("/check", data={"pick": [str(om), str(cu)], "servings_%d" % om: "2", "servings_%d" % cu: "2"},
               follow_redirects=True)
    body = text(r)
    ok("Checking 2 recipes" in body, "multi: heading")
    ok("Recipe by recipe" in body and "Everything together" in body, "multi: separated sections")
    ok(body.count('class="card recipe-card"') == 2, "multi: one card per recipe")
    ok(body.count("pill ok\">Ready") == 2, "multi: each recipe is ready on its own")
    ok("Shared ingredients" in body and "<strong>Eggs</strong>" in body, "multi: warns eggs only run short when combined")
    ok("You are missing 1 of 2 ingredients across all the recipes together" in body, "multi: combined banner counts shortage")
    ok("Short by 2.0 pcs" in body and "only short when combined" in body, "multi: combined shortage = 8 needed - 6 have")
    ok("Yes, cook everything" not in body and "See shopping list" in body, "multi: offers shopping list, not cooking")


    pairs = {"r": ["%d:2" % om, "%d:2" % cu]}
    r = c.post("/check/shopping-list", data=pairs, follow_redirects=True)
    body = text(r)
    ok("For 2 recipes." in body and "Eggs" in body and "2.0 pcs" in body, "shopping list: combined amount")
    ok("for Omelette, Custard" in body, "shopping list: says which recipes need the item")


    r = c.post("/shopping-list/purchase", data={"qty_0": "2"}, follow_redirects=True)
    body = text(r)
    ok("Checking 2 recipes" in body and "enough ingredients for all 2 recipes together" in body, "after buying: all recipes ready together")
    ok("Yes, cook everything" in body, "after buying: cook-everything offered")

    r = c.post("/check/cook", data=pairs, follow_redirects=True)
    body = text(r)
    ok("Cooked Omelette, Custard" in body, "cooked page names the recipes")
    ok(sqlite3.connect(path).execute(
        "SELECT quantity_on_hand FROM pantry_item p JOIN ingredient i USING(ingredient_id) WHERE ingredient_name='Eggs'"
    ).fetchone()[0] == 0.0, "cooking used the combined 8 eggs (8 - 8 = 0)")
    ok(sqlite3.connect(path).execute(
        "SELECT quantity_on_hand FROM pantry_item p JOIN ingredient i USING(ingredient_id) WHERE ingredient_name='Milk'"
    ).fetchone()[0] == 100.0, "milk reduced by 200")


    pantry(c, "Eggs", 20, "pcs")
    pantry(c, "Milk", 1000, "ml")


    form = {"pick": [str(om), str(cu), str(br)], "servings_%d" % om: "2", "servings_%d" % cu: "2", "servings_%d" % br: "4"}
    r = c.post("/groups/save", data={**form, "group_name": ""}, follow_redirects=True)
    ok(b"Give the group a name" in r.data, "group: name required")
    r = c.post("/groups/save", data={"pick": [str(om)], "servings_%d" % om: "2", "group_name": "Solo"}, follow_redirects=True)
    ok(b"at least 2 recipes" in r.data, "group: needs two or more recipes")
    r = c.post("/groups/save", data={**form, "group_name": "x" * 61}, follow_redirects=True)
    ok(b"60 characters" in r.data, "group: name length limit")
    ok(sqlite3.connect(path).execute("SELECT COUNT(*) FROM recipe_group").fetchone()[0] == 0, "group: nothing saved on errors")

    r = c.post("/groups/save", data={**form, "group_name": "Sunday Feast"}, follow_redirects=True)
    body = text(r)
    ok("Sunday Feast&#34; saved" in body, "group: saved")
    ok("Saved groups" in body and "Sunday Feast" in body and "Omelette &times;2" in body, "group: listed with recipes and servings")
    gid = sqlite3.connect(path).execute("SELECT group_id FROM recipe_group").fetchone()[0]

    r = c.get("/check/result?group=%d" % gid)
    body = text(r)
    ok("Sunday Feast" in body and "Checking 3 recipes" not in body, "group: result is titled with the group name")
    ok(body.count('class="card recipe-card"') == 3 and "Everything together" in body, "group: three recipe cards + combined")

    r = c.get("/check?group=%d" % gid)
    body = text(r)
    ok('value="Sunday Feast"' in body, "group: edit loads the name")
    ok(len(re.findall(r'name="pick" value="\d+"\s+checked', body)) == 3, "group: edit ticks its recipes")
    ok('name="servings_%d" value="4"' % br in body, "group: edit loads each recipe's servings")


    r = c.post("/groups/save", data={"pick": [str(om), str(br)], "servings_%d" % om: "3", "servings_%d" % br: "8",
                                     "group_name": "sunday feast"}, follow_redirects=True)
    ok(b"updated" in r.data, "group: same name (any capitals) updates")
    conn = sqlite3.connect(path)
    ok(conn.execute("SELECT COUNT(*) FROM recipe_group").fetchone()[0] == 1, "group: still one group")
    ok(conn.execute("SELECT COUNT(*) FROM recipe_group_item").fetchone()[0] == 2, "group: members replaced (2 now)")


    pantry(c, "Flour", 100, "g")
    r = c.post("/check/shopping-list", data={"group": str(gid)}, follow_redirects=True)
    ok("sunday feast (2 recipes)" in text(r), "group: shopping list labelled with the group")
    r = c.post("/shopping-list/purchase", data={"qty_0": "900"}, follow_redirects=True)
    ok("sunday feast" in text(r) and "enough ingredients for all 2 recipes" in text(r), "group: purchase returns to the group's check")


    c.post("/recipes/%d/delete" % br)
    body = text(c.get("/check"))
    ok("Bread" not in body.split("Planning a feast?")[0].split("Saved groups")[1], "group: deleted recipe disappears from the group")
    ok(conn.execute("SELECT COUNT(*) FROM recipe_group").fetchone()[0] == 1, "group: survives a recipe deletion")


    r = c.post("/groups/%d/delete" % gid, follow_redirects=True)
    ok(b"Group deleted" in r.data and b"Saved groups" not in r.data, "group: deleted")
    ok(sqlite3.connect(path).execute("SELECT COUNT(*) FROM recipe_group_item").fetchone()[0] == 0, "group: members removed with it")


    c.post("/groups/save", data={"pick": [str(om), str(cu)], "servings_%d" % om: "1", "servings_%d" % cu: "1",
                                 "group_name": "Mine"})
    gid2 = sqlite3.connect(path).execute("SELECT group_id FROM recipe_group").fetchone()[0]
    c.post("/logout")
    c2 = app.test_client()
    signup_login(c2, "bob@example.com")
    r = c2.get("/check/result?group=%d" % gid2, follow_redirects=True)
    ok(b"could not be found" in r.data, "group: another user cannot open it")
    c2.post("/groups/%d/delete" % gid2)
    ok(sqlite3.connect(path).execute("SELECT COUNT(*) FROM recipe_group").fetchone()[0] == 1, "group: another user cannot delete it")


    with c2.session_transaction() as s:
        s["shopping_list"] = {"recipe_id": 1, "recipe_name": "Old", "servings": 2, "rows": []}
    r = c2.get("/shopping-list", follow_redirects=True)
    ok(r.status_code == 200 and b"no shopping list" in r.data, "old-format saved shopping list handled gracefully")
    os.remove(path)

def test_ideas():
    app, path = new_app()
    c = app.test_client()
    signup_login(c)


    pantry(c, "Rice", 500, "g")
    body = text(c.get("/pantry/"))
    ok("What can I cook?" in body and "Save a few recipes" in body, "ideas: prompts to add recipes when there are none")


    app2, path2 = new_app()
    c2 = app2.test_client()
    signup_login(c2)
    recipe(c2, "Fried Rice", 2, [("Rice", 200, "g")])
    body = text(c2.get("/pantry/"))
    ok("Add some ingredients to your pantry" in body, "ideas: prompts to stock the pantry when it is empty")


    pantry(c, "Egg", 4, "pcs")
    pantry(c, "Soy sauce", 100, "ml")
    recipe(c, "Fried Rice", 2, [("Rice", 200, "g"), ("Egg", 2, "pcs"), ("Soy sauce", 30, "ml")])
    recipe(c, "Garlic Rice", 2, [("Rice", 200, "g"), ("Soy sauce", 10, "ml"), ("Garlic", 3, "pcs"), ("Butter", 20, "g")])
    recipe(c, "Beef Stew", 4, [("Beef", 500, "g"), ("Potato", 4, "pcs"), ("Carrot", 3, "pcs"), ("Onion", 2, "pcs")])
    recipe(c, "Thin Soup", 2, [("Rice", 50, "g"), ("Carrot", 1, "pcs"), ("Onion", 1, "pcs")])
    body = text(c.get("/pantry/"))
    ok("Ready to cook" in body and "Fried Rice" in body, "ideas: ready dish shown")
    ok("Almost there" in body and "Garlic Rice" in body, "ideas: dish missing a few ingredients shown")
    almost = body.split("Almost there")[1]
    ok("Garlic" in almost and "Butter" in almost, "ideas: names the missing ingredients")
    ok("Beef Stew" not in body, "ideas: a dish missing most ingredients is not suggested")
    ok("Thin Soup" not in body, "ideas: a dish with under half its ingredients covered is not suggested")
    ok("Suggested for you" not in body, "ideas: no top-picks block with 5 or fewer recipes")
    ok("/check/result?r=" in body, "ideas: dish links to the check page")


    recipe(c, "Egg Rice", 1, [("Rice", 100, "g"), ("Egg", 1, "pcs")])
    body = text(c.get("/pantry/"))
    ok("Suggested for you" not in body, "ideas: exactly 5 recipes -> still no picks block")
    recipe(c, "Soy Eggs", 2, [("Egg", 2, "pcs"), ("Soy sauce", 20, "ml")])
    recipe(c, "Rice Bowl", 1, [("Rice", 100, "g"), ("Soy sauce", 10, "ml")])
    body = text(c.get("/pantry/"))
    ok("Suggested for you" in body, "ideas: 6 recipes (more than 5) -> picks block appears")
    picks_html = body.split("Suggested for you")[1].split("Ready to cook")[0]
    ok(picks_html.count('class="dish ready pick"') + picks_html.count('class="dish almost pick"') == 3, "ideas: exactly 3 picks")
    ok("You have everything you need" in picks_html or "You have everything, and it uses" in picks_html, "ideas: picks explain why")

    rest = body.split("Suggested for you")[1].split("Ready to cook", 1)
    names = re.findall(r'class="dish ready pick">\s*<div class="dish-head">\s*<strong>([^<]+)', picks_html)
    ok(len(names) == 3 and all(("<strong>%s</strong>" % n) not in (rest[1] if len(rest) > 1 else "") for n in names),
       "ideas: picks are not repeated in the lists below")


    app3, path3 = new_app()
    c3 = app3.test_client()
    signup_login(c3)
    soon = (date.today() + timedelta(days=2)).isoformat()
    pantry(c3, "Milk", 1000, "ml", expiry=soon)
    pantry(c3, "Flour", 5000, "g")
    pantry(c3, "Sugar", 5000, "g")
    for i in range(5):
        recipe(c3, "Plain %d" % i, 1, [("Flour", 100, "g"), ("Sugar", 10, "g")])
    recipe(c3, "Milk Pudding", 1, [("Milk", 200, "ml"), ("Sugar", 10, "g")])
    body = text(c3.get("/pantry/"))
    picks_html = body.split("Suggested for you")[1].split("Ready to cook")[0]
    ok("Milk Pudding" in picks_html, "ideas: dish using an ingredient about to expire is picked")
    ok("before it expires (in 2 days)" in picks_html, "ideas: says what is about to expire")


    app4, path4 = new_app()
    c4 = app4.test_client()
    signup_login(c4)
    pantry(c4, "Salt", 5, "g")
    recipe(c4, "Beef Stew", 4, [("Beef", 500, "g"), ("Potato", 4, "pcs"), ("Carrot", 3, "pcs")])
    body = text(c4.get("/pantry/"))
    ok("within a few ingredients of your pantry yet" in body, "ideas: friendly message when nothing is close")


    rec = rid(path, "Garlic Rice")
    r = c.get("/check/result?r=%d:2" % rec)
    ok("You are missing 2 of 4 ingredients" in text(r), "ideas: 'missing 2' matches what the Check page says")
    for p in (path, path2, path3, path4):
        os.remove(p)

def test_upgrade_existing_db():
    
    fd, path = tempfile.mkstemp()
    os.close(fd)
    from schema import SQLITE_SCHEMA
    old_schema = SQLITE_SCHEMA.split("CREATE TABLE IF NOT EXISTS recipe_group (")[0]   # the tables before groups existed
    conn = sqlite3.connect(path)
    conn.executescript(old_schema)
    conn.execute("INSERT INTO user_account (name,email,password_hash) VALUES ('Old User','old@x.com','h')")
    conn.commit()
    ok(conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='recipe_group'").fetchone()[0] == 0, "upgrade: old db has no group tables")
    conn.close()

    app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    c = app.test_client()
    r = c.get("/signup")
    c.post("/login", data={"email": "old@x.com", "password": "x"})
    conn = sqlite3.connect(path)
    ok(conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='recipe_group'").fetchone()[0] == 1, "upgrade: group table added automatically")
    ok(conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='recipe_group_item'").fetchone()[0] == 1, "upgrade: group item table added automatically")
    ok(conn.execute("SELECT name FROM user_account").fetchone()[0] == "Old User", "upgrade: existing data untouched")
    conn.close()
    os.remove(path)


if __name__ == "__main__":
    test_multi_and_groups()
    test_ideas()
    test_upgrade_existing_db()
    print("\nALL CHECKS PASSED")
