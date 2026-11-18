@echo off
REM ============================================================
REM  Byungmat Love Simulation - game launcher
REM  Runs byungmat_love.py with the official (signed) Python,
REM  so antivirus does not block an unsigned program.
REM ============================================================
cd /d "%~dp0"

REM 0) run.bat alone does nothing: the game file must be next to it
if not exist "byungmat_love.py" (
    echo.
    echo  [!] byungmat_love.py was not found next to run.bat.
    echo.
    echo      Please do not download run.bat alone.
    echo      On the GitHub page: green "Code" button - "Download ZIP",
    echo      unzip it, then double-click run.bat inside that folder.
    echo.
    pause
    exit /b 1
)

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
