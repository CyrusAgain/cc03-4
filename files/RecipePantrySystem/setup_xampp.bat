@echo off
rem One-time setup for XAMPP. Double-click this file.
cd /d "%~dp0"
where py >nul 2>nul && (py -3 setup_xampp.py & goto done)
where python >nul 2>nul && (python setup_xampp.py & goto done)
echo Python was not found. Install Python 3 from https://www.python.org/downloads/
echo (tick "Add python.exe to PATH" in the installer) and run this file again.
:done
echo.
pause
