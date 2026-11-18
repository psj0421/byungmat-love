@echo off
REM ============================================================
REM  Byungmat Love Simulation - game launcher
REM  Runs byungmat_love.py with the official (signed) Python,
REM  so antivirus does not block an unsigned program.
REM ============================================================
cd /d "%~dp0"

REM 1) Python launcher (installed by the python.org installer)
py -3 -c "import tkinter" >nul 2>nul
if not errorlevel 1 (
    start "" pyw -3 byungmat_love.py
    exit /b 0
)

REM 2) python on PATH (checks it really runs, not the Store shortcut)
python -c "import tkinter" >nul 2>nul
if not errorlevel 1 (
    start "" pythonw byungmat_love.py
    exit /b 0
)

REM 3) No Python: show how to install it
echo.
echo  [!] Python 3 was not found on this PC.
echo.
echo      1. Install Python 3 from https://www.python.org/downloads/
echo         (turn on "Add python to PATH" during install)
echo      2. Double-click run.bat again.
echo.
start "" https://www.python.org/downloads/
pause
exit /b 1
