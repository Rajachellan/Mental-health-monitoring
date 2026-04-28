@echo off
REM Always run Flask from this folder (fixes wrong cwd / wrong app.py when double-clicking).
cd /d "%~dp0"
echo Running from: %CD%
python app.py
pause
