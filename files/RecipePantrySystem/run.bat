@echo off
rem Starts the Recipe Pantry System and opens it in your browser.
rem   run.bat           -> starts XAMPP MySQL + Apache, opens http://localhost/RecipePantrySystem/
rem   run.bat --flask   -> runs the app on its own at http://127.0.0.1:5000/
cd /d "%~dp0"
where py >nul 2>nul && (py -3 run.py %* & goto done)
where python >nul 2>nul && (python run.py %* & goto done)
echo Python was not found. Install Python 3 from https://www.python.org/downloads/
:done
if errorlevel 1 pause
