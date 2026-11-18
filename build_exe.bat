@echo off
REM Build byungmat_love.exe  (needs: pip install pyinstaller)
REM Output: release\byungmat_love.exe  (committed to GitHub so it is easy to find)
cd /d "%~dp0"

echo [1/3] Running tests...
python -m unittest test_byungmat
if errorlevel 1 (
    echo Tests failed. exe was NOT built.
    exit /b 1
)

echo [2/3] Building exe...
python -m PyInstaller --onefile --windowed --name byungmat_love --add-data "images;images" --clean -y byungmat_love.py
if errorlevel 1 exit /b 1

echo [3/3] Copying exe to release folder...
if not exist release mkdir release
copy /y dist\byungmat_love.exe release\byungmat_love.exe > nul
echo Done: release\byungmat_love.exe
