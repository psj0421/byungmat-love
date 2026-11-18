@echo off
REM Build byungmat_love.exe  (needs: pip install pyinstaller)
REM Output: dist\byungmat_love.exe
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
echo Done: dist\byungmat_love.exe
