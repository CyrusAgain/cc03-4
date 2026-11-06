"""Checks that the project is Python-only and that the Python-generated pages/styles work."""
import os
import re
import tempfile

from app import create_app
from ui_styles import APP_CSS, ICON_CSS
from ui_templates import TEMPLATES

failures = 0


def ok(cond, label):
    global failures
    print(("ok   " if cond else "FAIL ") + label)
    if not cond:
        failures += 1


here = os.path.dirname(os.path.abspath(__file__))

# 1. no html / css / php / sql files anywhere in the project
banned = (".html", ".htm", ".css", ".php", ".sql")
found = []
for root, dirs, files in os.walk(here):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "venv") and "venv" not in d]
    found += [os.path.join(root, f) for f in files if f.lower().endswith(banned)]
ok(not found, "project has no .html/.css/.php/.sql files %s" % (found or ""))

# 2. every icon used by a page has a CSS rule
used = {m for t in TEMPLATES.values() for m in re.findall(r"\bfa-[a-z0-9-]+", t)}
missing = sorted(u for u in used if (".%s:before" % u) not in ICON_CSS)
ok(not missing, "every icon used in the pages is defined %s" % (missing or ""))

# 3. the app, with pages and CSS coming from Python
fd, path = tempfile.mkstemp()
os.close(fd)
app = create_app({"TESTING": True, "DATABASE": path})
c = app.test_client()

r = c.get("/theme.css")
ok(r.status_code == 200 and r.mimetype == "text/css", "/theme.css is served as CSS")
ok(b"Playfair Display" in r.data and b".fa-utensils:before" in r.data and b"fa-solid-900.woff2" in r.data,
   "/theme.css contains the app styles, icons and font link")
ok(r.headers["Cache-Control"] == "no-cache", "unversioned stylesheet is not cached")
page = c.get("/").get_data(as_text=True)
ver = re.search(r'/theme\.css\?v=([0-9a-f]+)', page)
ok(ver is not None, "pages link the stylesheet with a version")
r = c.get("/theme.css?v=" + ver.group(1))
ok("immutable" in r.headers["Cache-Control"], "versioned stylesheet is cached for a long time")
ok("PHP" not in page and "php" not in page.lower().replace("<!doctype", ""), "no PHP links left in the pages")
ok(c.get("/static/webfonts/fa-solid-900.woff2").status_code == 200, "icon font is served")
ok(c.get("/static/style.css").status_code == 404, "there is no style.css file")

# 4. friendly page when MySQL is not running (default backend is MySQL)
os.remove(path)
mysql_app = create_app({"TESTING": True, "DB_BACKEND": "mysql", "MYSQL_PORT": 1, "MYSQL_HOST": "127.0.0.1"})
r = mysql_app.test_client().post("/login", data={"email": "a@b.co", "password": "password1"})
ok(r.status_code == 503 and b"Database needed" in r.data and b"Start" in r.data, "MySQL offline -> friendly 503 page, not a crash")
ok(b"theme.css" in r.data, "the error page is styled too")

print("\nALL CHECKS PASSED" if not failures else "\n%d CHECK(S) FAILED" % failures)
raise SystemExit(1 if failures else 0)
