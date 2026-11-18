@echo off
REM (Optional) Build byungmat_love.exe for your own PC.  needs: pip install pyinstaller
REM Output: distyungmat_love.exe
REM Note: unsigned exe files are often blocked by antivirus (e.g. V3) on other PCs.
REM       For sharing, use run.bat instead.
cd /d "%~dp0"

echo [1/2] Running tests...
python -m unittest test_byungmat
if errorlevel 1 (
    echo Tests failed. exe was NOT built.
    exit /b 1
)

echo [2/2] Building exe...
python -m PyInstaller --onefile --windowed --name byungmat_love --add-data "images;images" --clean -y byungmat_love.py
if errorlevel 1 exit /b 1
echo Done: distyungmat_love.exe
