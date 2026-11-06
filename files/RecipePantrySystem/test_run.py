"""Tests for run.py (the cmd launcher). Windows-only service starting is mocked."""
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import run

failures = 0


def ok(cond, label):
    global failures
    print(("ok   " if cond else "FAIL ") + label)
    if not cond:
        failures += 1


here = os.path.dirname(os.path.abspath(__file__))

# --- finding XAMPP and Apache's port
root, folder = run.find_xampp(os.path.join("C:\\", "xampp", "htdocs", "RecipePantrySystem")) if os.name == "nt" else run.find_xampp("/tmp/x/xampp/htdocs/RecipePantrySystem")
ok(root is not None and folder == "RecipePantrySystem", "finds the XAMPP root and the site folder")
ok(run.find_xampp("/tmp/not-xampp/project") == (None, None), "reports when the folder is not inside htdocs")
tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, "apache", "conf"))
conf = os.path.join(tmp, "apache", "conf", "httpd.conf")
for text, expected in (("Listen 80\n", 80), ("Listen 8081\n", 8081), ("Listen 0.0.0.0:8090\n", 8090), ("# nothing\n", 80)):
    open(conf, "w").write(text)
    ok(run.apache_port(tmp) == expected, "apache_port reads %r -> %d" % (text.strip(), expected))

# --- XAMPP mode: starts what is not running, then opens the browser at the right address
calls, opened = [], []
run.start_service = lambda root_, label, script, port: calls.append((label, script, port)) or True
run.open_browser = lambda url: opened.append(url)
class FakeResp: pass
_real_urlopen = urllib.request.urlopen
urllib.request.urlopen = lambda url, timeout=0: FakeResp()
open(conf, "w").write("Listen 80\n")
run.xampp_mode(tmp, "RecipePantrySystem", browser=True)
ok(calls == [("MySQL", "mysql_start.bat", 3306), ("Apache", "apache_start.bat", 80)], "XAMPP mode starts MySQL, then Apache")
ok(opened == ["http://localhost/RecipePantrySystem/"], "XAMPP mode opens the site address")
calls.clear(); opened.clear()
open(conf, "w").write("Listen 8080\n")
run.xampp_mode(tmp, "RecipePantrySystem", browser=False)
ok(not opened, "--no-browser does not open anything")
run.xampp_mode(tmp, "My Site", browser=True)
ok(opened == ["http://localhost:8080/My Site/"], "a non-default Apache port is part of the address")

# --- service already running -> nothing is started
import importlib
importlib.reload(run)
run.port_open = lambda port, host="127.0.0.1", timeout=0.5: True
ok(run.start_service(tmp, "MySQL", "mysql_start.bat", 3306) is True, "a service that is already running is left alone")

urllib.request.urlopen = _real_urlopen      # undo the fake before talking to a real server

# --- Flask mode really serves the site (SQLite so no MySQL is needed here)
port = 5071
env = dict(os.environ, RECIPEPANTRY_DB_BACKEND="sqlite")
proc = subprocess.Popen([sys.executable, os.path.join(here, "run.py"), "--flask", "--no-browser", "--port", str(port)],
                        env=env, cwd=here, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
try:
    body, css = b"", b""
    for _ in range(40):
        try:
            body = urllib.request.urlopen("http://127.0.0.1:%d/" % port, timeout=2).read()
            css = urllib.request.urlopen("http://127.0.0.1:%d/theme.css" % port, timeout=2).read()
            break
        except OSError:
            time.sleep(0.25)
    ok(b"Recipe Pantry System" in body, "python run.py --flask serves the site")
    ok(b"Playfair Display" in css, "...and its Python-generated stylesheet")
finally:
    proc.terminate()
    proc.wait(timeout=10)

print("\nALL CHECKS PASSED" if not failures else "\n%d CHECK(S) FAILED" % failures)
raise SystemExit(1 if failures else 0)
