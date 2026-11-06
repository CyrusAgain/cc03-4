import os
import tempfile

from app import create_app
import db as db_module


def make_client():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    with app.app_context():
        db_module.init_db()
    return app, path


def ok(cond, msg):
    status = "ok  " if cond else "FAIL"
    print(status, msg)
    if not cond:
        raise SystemExit(1)


def main():
    app, path = make_client()
    c = app.test_client()


    r = c.get("/")
    ok(r.status_code == 200 and b"Log in" in r.data, "landing page renders")
    ok(b"Not now" not in r.data, "landing page has no Not now option")


    r = c.post("/signup", data={"name": "", "email": "", "password": "", "confirm": ""}, follow_redirects=True)
    ok(b"Fill in every field" in r.data, "signup validation: empty fields")


    r = c.post("/signup", data={
        "name": "Ana Cruz", "email": "ana@example.com",
        "password": "password1", "confirm": "password1",
    }, follow_redirects=True)
    ok(b"Account created successfully" in r.data, "signup success -> redirected to login")


    r = c.post("/signup", data={
        "name": "Ana2", "email": "ANA@example.com",
        "password": "password1", "confirm": "password1",
    }, follow_redirects=True)
    ok(b"already registered" in r.data, "duplicate email rejected")


    r = c.post("/login", data={"email": "ana@example.com", "password": "nope"}, follow_redirects=True)
    ok(b"Incorrect email or password" in r.data, "wrong password rejected")


    r = c.post("/forgot-password", data={"email": "ghost@example.com"}, follow_redirects=True)
    ok(b"could not find" in r.data, "forgot-password: unknown email")


    r = c.post("/forgot-password", data={"email": "ana@example.com"})
    body = r.get_data(as_text=True)
    import re
    m = re.search(r"Demo code: <strong>(\d{6})</strong>", body)
    ok(m is not None, "forgot-password: demo code shown")
    code = m.group(1)
    r = c.post("/forgot-password/reset", data={"code": "000000", "password": "newpassword1"}, follow_redirects=True)
    ok(b"not valid" in r.data, "forgot-password: wrong code rejected")
    r = c.post("/forgot-password/reset", data={"code": code, "password": "newpassword1"}, follow_redirects=True)
    ok(b"Password changed" in r.data, "forgot-password: reset succeeds")


    r = c.post("/login", data={"email": "ana@example.com", "password": "password1"}, follow_redirects=True)
    ok(b"Incorrect" in r.data, "old password now rejected")
    r = c.post("/login", data={"email": "ana@example.com", "password": "newpassword1"}, follow_redirects=True)
    ok(b"Hello, Ana" in r.data, "login with new password -> dashboard")


    c.post("/pantry/new", data={"name": "Flour", "quantity": "1000", "unit": "g", "expiry_date": ""})
    c.post("/pantry/new", data={"name": "Eggs", "quantity": "6", "unit": "pcs", "expiry_date": ""})
    c.post("/pantry/new", data={"name": "Milk", "quantity": "300", "unit": "ml", "expiry_date": ""})
    r = c.get("/pantry/")
    ok(b"Flour" in r.data and b"Eggs" in r.data and b"Milk" in r.data, "pantry lists added ingredients")


    c.post("/pantry/new", data={"name": "flour", "quantity": "1500", "unit": "g", "expiry_date": ""})
    r = c.get("/pantry/")
    ok(r.data.count(b"Flour") <= 2, "duplicate ingredient name updates rather than duplicating")
    ok(b"1500.0 g" in r.data, "updated quantity shown")


    r = c.post("/recipes/new", data={
        "recipe_name": "", "servings": "0",
        "ingredient_name": [""], "ingredient_quantity": [""], "ingredient_unit": [""],
    }, follow_redirects=True)
    ok(b"Enter the recipe name" in r.data, "recipe validation: missing name")


    r = c.post("/recipes/new", data={
        "recipe_name": "Pancakes", "servings": "4",
        "ingredient_name": ["Flour", "Milk", "Eggs"],
        "ingredient_quantity": ["250", "400", "2"],
        "ingredient_unit": ["g", "ml", "pcs"],
    }, follow_redirects=True)
    ok(b"Recipe saved" in r.data, "recipe created")
    r = c.get("/recipes/")
    ok(b"Pancakes" in r.data, "recipe listed")


    import sqlite3
    conn = sqlite3.connect(path)
    recipe_id = conn.execute("SELECT recipe_id FROM recipe WHERE recipe_name='Pancakes'").fetchone()[0]


    r = c.get("/check/result?recipe_id=%d&servings=8" % recipe_id)
    body = r.get_data(as_text=True)
    ok("missing 1 of 3" in body, "ingredient check: correct shortage count (milk only)")
    ok("Short by 500.0 ml" in body, "ingredient check: correct shortage amount for milk")


    r = c.post("/check/shopping-list", data={"recipe_id": recipe_id, "servings": 8}, follow_redirects=True)
    ok(b"Shopping list" in r.data and b"Milk" in r.data, "shopping list generated with missing item")


    r = c.post("/shopping-list/purchase", data={"qty_0": "500"}, follow_redirects=True)
    ok(b"You have enough ingredients" in r.data, "after purchase, recipe is now fully available")


    r = c.post("/check/cook", data={"recipe_id": recipe_id, "servings": 8}, follow_redirects=True)
    ok(b"Pantry updated" in r.data, "cooking confirmation shown")
    r = c.get("/pantry/")
    ok(b"1000.0 g" in r.data, "flour correctly reduced after cooking (1500 - 500)")


    r = c.post("/pantry/new", data={"name": "Salt", "quantity": "5", "unit": "", "expiry_date": ""}, follow_redirects=True)
    ok(b"Ingredient saved" in r.data, "pantry item saves without a unit")
    r = c.post("/recipes/new", data={"recipe_name": "Plain", "servings": "1", "ingredient_name": ["Salt"],
                                     "ingredient_quantity": ["2"], "ingredient_unit": [""]}, follow_redirects=True)
    ok(b"Recipe saved" in r.data, "recipe ingredient saves without a unit")


    r = c.post("/logout", follow_redirects=True)
    ok(b"Welcome back" in r.data and b"logged out" not in r.data, "logout returns straight to log in")
    r = c.get("/dashboard", follow_redirects=True)
    ok(b"Log in" in r.data and b"Hello" not in r.data, "dashboard requires login again after logout")

    os.remove(path)
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
