"""One-time setup for running the Recipe Pantry System inside XAMPP.

Double-click setup_xampp.bat (or run: python setup_xampp.py). It:
  1. points app.cgi at the Python that is running this script,
  2. installs the Python packages (Flask, PyMySQL, bcrypt),
  3. checks the folder location and the Apache modules XAMPP needs,
  4. checks the MySQL connection and creates the database and tables,
  5. tells you the address to open.
Nothing is changed in XAMPP itself.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OK, WARN = "[ ok ]", "[warn]"


def find_xampp(path):
    """Returns (xampp_root, folder_name_under_htdocs) or (None, None)."""
    parts = []
    while True:
        parent = os.path.dirname(path)
        if os.path.basename(path).lower() == "htdocs":
            return parent, "/".join(reversed(parts))
        if parent == path:
            return None, None
        parts.append(os.path.basename(path))
        path = parent


def set_shebang():
    exe = sys.executable.replace("\\", "/")
    cgi = os.path.join(HERE, "app.cgi")
    with open(cgi, "r", encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    lines[0] = "#!" + exe
    with open(cgi, "w", encoding="utf-8", newline="") as f:      # LF endings, Apache is happy with them
        f.write("\n".join(lines))
    print(OK, "app.cgi now uses Python at", exe)
    if " " in exe:
        print(WARN, "That path contains a space. If Apache shows a 500 error, install Python to a")
        print("       folder without spaces (for example C:\\Python312) and run this setup again.")


def install_packages():
    print("...  installing Flask, PyMySQL and bcrypt (this can take a minute)")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(HERE, "requirements.txt")])
    print(OK if r.returncode == 0 else WARN, "packages installed" if r.returncode == 0 else "pip failed, see the messages above")


def check_xampp():
    root, folder = find_xampp(HERE)
    if root is None:
        print(WARN, "This folder is not inside XAMPP's htdocs folder.")
        print("       Move it to e.g. C:\\xampp\\htdocs\\RecipePantrySystem and run this setup again.")
        return None
    print(OK, "Project folder is inside htdocs:", HERE)
    conf = os.path.join(root, "apache", "conf", "httpd.conf")
    if os.path.exists(conf):
        text = open(conf, encoding="utf-8", errors="ignore").read()
        for module in ("rewrite_module", "cgi_module"):
            on = re.search(r"^\s*LoadModule\s+%s\s" % module, text, re.M)
            print(OK if on else WARN, "Apache %s is %s" % (module, "enabled" if on else
                  "NOT enabled: open httpd.conf and remove the # in front of its LoadModule line"))
        allow = re.search(r"<Directory\s+\"?[^>]*htdocs\"?>(.*?)</Directory>", text, re.S | re.I)
        if allow and not re.search(r"AllowOverride\s+(All|FileInfo)", allow.group(1), re.I):
            print(WARN, "htdocs does not allow .htaccess files: set 'AllowOverride All' for it in httpd.conf")
    return folder


def check_database():
    code = "from app import app\nimport db\nwith app.app_context():\n    db.get_db()\n"
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True)
    if r.returncode == 0:
        print(OK, "MySQL is reachable; database 'recipe_pantry' and its tables are ready")
        return
    last = (r.stderr.strip().splitlines() or ["unknown error"])[-1]
    print(WARN, "Could not reach MySQL:", last)
    print("       Press Start next to MySQL in the XAMPP Control Panel, then run this setup again")
    print("       (or just open the site: the database is also created on first use).")


def main():
    set_shebang()
    install_packages()
    folder = check_xampp()
    check_database()
    print()
    if folder:
        print("Done. From now on, open cmd in this folder and run:  run.bat")
        print("It starts MySQL and Apache and opens  http://localhost/%s/  in your browser." % folder)
    else:
        print("Setup finished, but fix the warning(s) above before starting Apache.")


if __name__ == "__main__":
    main()
