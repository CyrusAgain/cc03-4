# Running the Recipe Pantry System in XAMPP

The whole app is Python. XAMPP provides **Apache** (the web server) and **MySQL** (the database,
visible in phpMyAdmin). You start and stop everything from the XAMPP Control Panel.

## One-time setup

1. Install **Python 3** (https://www.python.org/downloads/) and tick "Add python.exe to PATH".
   A folder without spaces, such as `C:\Python312`, is safest.
2. Copy this whole folder to `C:\xampp\htdocs\RecipePantrySystem`.
3. Double-click **setup_xampp.bat**. It points `app.cgi` at your Python, installs the packages
   (Flask, PyMySQL, bcrypt), checks Apache's modules and MySQL, and creates the database.
   Read any `[warn]` lines it prints.
4. In the **XAMPP Control Panel** press **Start** next to **Apache** and **MySQL**.
5. Open **http://localhost/RecipePantrySystem/**

## Day to day: start it from cmd

Open **cmd** in the project folder (or just double-click `run.bat`) and run:

    run.bat

(or `python run.py`). It starts XAMPP's **MySQL** and **Apache** if they are not already running, then opens
**http://localhost/RecipePantrySystem/** in your browser. Starting them from the XAMPP Control Panel still works too.

    run.bat --flask        run the app on its own at http://127.0.0.1:5000/ (no Apache; Ctrl+C stops it)
    run.bat --no-browser   start everything but do not open the browser

Apache and MySQL keep running in their own minimised windows; close those windows (or use the Control Panel) to stop them.

## What lives where

| What | Where |
|---|---|
| Pages (HTML) | `ui_templates.py` (Jinja pages stored as Python strings) |
| Styling (CSS) | `ui_styles.py`, served by the app at `/theme.css` |
| Database tables | `schema.py` (created automatically; no SQL import needed) |
| Data | XAMPP MySQL, database `recipe_pantry` (browse it in phpMyAdmin) |
| Login secret | `instance/secret.key` (blocked from the web by `.htaccess`) |
| Icon font | `static/webfonts/fa-solid-900.woff2` (binary, served by Apache) |

There are no `.html`, `.css`, `.php` or `.sql` files. `test_python_only.py` checks that.

## Settings (optional environment variables)

`RECIPEPANTRY_DB_HOST` (127.0.0.1), `RECIPEPANTRY_DB_PORT` (3306), `RECIPEPANTRY_DB_NAME` (recipe_pantry),
`RECIPEPANTRY_DB_USER` (root), `RECIPEPANTRY_DB_PASSWORD` (empty), and `RECIPEPANTRY_DB_BACKEND=sqlite`
to use a local SQLite file instead of MySQL.

## Limits

Apache runs `app.cgi` for every page (CGI), which works on a stock XAMPP but starts Python afresh each
time, so pages take a fraction of a second longer than `flask run`. The stylesheet is cached by the browser.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Database needed" page | Start **MySQL** in the XAMPP Control Panel and reload |
| "The Recipe Pantry app could not start" | Run `setup_xampp.bat` again; the page shows the Python error |
| Plain 500 error | The Python path in the first line of `app.cgi` is wrong or has spaces: reinstall Python to `C:\Python312`, rerun setup |
| 403 / 404 / source code shown | In `C:\xampp\apache\conf\httpd.conf` make sure `rewrite_module` and `cgi_module` are enabled and htdocs has `AllowOverride All`; restart Apache |
| No styling | Open `http://localhost/RecipePantrySystem/theme.css`; if that errors, see the first two rows |
| `run.bat` cannot start MySQL/Apache | Start them in the XAMPP Control Panel, then run `run.bat` again |
| Prefer plain Flask | `pip install -r requirements.txt` then `flask --app app run --debug` |

## Tests

    python smoke_test.py
    python test_multi_and_ideas.py
    python test_python_only.py
    python test_run.py
