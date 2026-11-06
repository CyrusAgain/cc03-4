"""Start the Recipe Pantry System from cmd and open it in your browser.

    python run.py            inside XAMPP's htdocs: starts MySQL and Apache (if they are not
                             running) and opens http://localhost/RecipePantrySystem/
    python run.py --flask    skips Apache: runs the app itself on http://127.0.0.1:5000/
                             (MySQL is still started from XAMPP when it is found)
    options: --no-browser, --port N (Flask mode)

On Windows you can simply run:  run.bat
"""
import argparse
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

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


def port_open(port, host="127.0.0.1", timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_for_port(port, seconds=30):
    end = time.time() + seconds
    while time.time() < end:
        if port_open(port):
            return True
        time.sleep(0.5)
    return False


def apache_port(root):
    """The port Apache listens on (80 unless httpd.conf says otherwise)."""
    try:
        text = open(os.path.join(root, "apache", "conf", "httpd.conf"), encoding="utf-8", errors="ignore").read()
        m = re.search(r"^\s*Listen\s+(?:[\w.:\[\]]*:)?(\d+)\s*$", text, re.M)
        if m:
            return int(m.group(1))
    except OSError:
        pass
    return 80


def start_service(root, label, script, port):
    """Starts an XAMPP service (in its own minimised window) unless it is already running."""
    if port_open(port):
        print(OK, label, "is already running")
        return True
    path = os.path.join(root, script)
    if os.name != "nt" or not os.path.exists(path):
        print(WARN, "Could not start %s from here: press Start next to it in the XAMPP Control Panel." % label)
        return False
    print("...  starting %s" % label)
    subprocess.Popen(["cmd", "/c", "start", "XAMPP " + label, "/min", "cmd", "/c", path], cwd=root)
    if wait_for_port(port):
        print(OK, label, "is running")
        return True
    print(WARN, "%s did not start within 30 seconds. Open the XAMPP Control Panel to see why." % label)
    return False


def open_browser(url):
    print("Opening", url)
    webbrowser.open(url)


def xampp_mode(root, folder, browser=True):
    start_service(root, "MySQL", "mysql_start.bat", 3306)
    port = apache_port(root)
    apache_ok = start_service(root, "Apache", "apache_start.bat", port)
    url = "http://localhost%s/%s/" % ("" if port == 80 else ":%d" % port, folder)
    if apache_ok:
        try:
            urllib.request.urlopen(url, timeout=15)
            print(OK, "the site answers at", url)
        except urllib.error.HTTPError as exc:
            print(WARN, "the site answered with HTTP %d. If it says the app could not start, run setup_xampp.bat once." % exc.code)
        except OSError as exc:
            print(WARN, "could not reach the site yet (%s)" % exc)
    if browser:
        open_browser(url)
    return 0


def free_port(start):
    for port in range(start, start + 20):
        if not port_open(port):
            return port
    return start


def flask_mode(root, port, browser=True):
    if root and os.environ.get("RECIPEPANTRY_DB_BACKEND", "mysql") == "mysql":
        start_service(root, "MySQL", "mysql_start.bat", 3306)
    port = free_port(port)
    url = "http://127.0.0.1:%d/" % port
    if browser:
        threading.Timer(1.5, open_browser, args=(url,)).start()
    from app import app
    print("Recipe Pantry System running at", url, "(press Ctrl+C to stop)")
    app.run(host="127.0.0.1", port=port, debug=False)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Start the Recipe Pantry System and open it in the browser.")
    parser.add_argument("--flask", action="store_true", help="run the app directly instead of through Apache")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    parser.add_argument("--port", type=int, default=5000, help="port for --flask mode (default 5000)")
    args = parser.parse_args(argv)

    root, folder = find_xampp(HERE)
    if args.flask or root is None:
        if root is None and not args.flask:
            print(WARN, "This folder is not inside XAMPP's htdocs, so the app will run on its own (Flask mode).")
        return flask_mode(root, args.port, not args.no_browser)
    return xampp_mode(root, folder, not args.no_browser)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped.")
