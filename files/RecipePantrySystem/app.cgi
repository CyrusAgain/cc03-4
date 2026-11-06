#!C:/Python312/python.exe
# Runs the Flask app inside XAMPP's Apache (mod_cgi). setup_xampp.py rewrites the first
# line to point at the Python on your PC, so you normally never edit this file.
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

try:
    # The URL the app is mounted at, e.g. /RecipePantrySystem (Apache reports .../app.cgi)
    script = os.environ.get("SCRIPT_NAME", "")
    if script.endswith("/app.cgi"):
        os.environ["SCRIPT_NAME"] = script[: -len("/app.cgi")]

    from wsgiref.handlers import CGIHandler
    from app import app

    CGIHandler().run(app)
except Exception:
    sys.stdout.write("Status: 500 Internal Server Error\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n")
    sys.stdout.write("The Recipe Pantry app could not start.\r\n"
                     "Run setup_xampp.bat once (it installs the Python packages and fixes the Python path).\r\n\r\n")
    sys.stdout.write(traceback.format_exc())
