
@echo off
echo DPS-OS Windows Installation
echo ===========================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements_windows.txt

if errorlevel 1 (
    echo Error installing dependencies!
    echo Try running as Administrator
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo To run DPS-OS:
echo   python dps_app.py
echo.
echo Then open: http://localhost:8080
echo.
pause