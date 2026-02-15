@echo off
TITLE VOLTS INSTALLER
color 0A

echo ===================================================
echo      ⚡ VOLTS COMMAND CENTER - INSTALLATION ⚡
echo ===================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from python.org and tick "Add to PATH" during installation.
    pause
    exit /b
)

echo [1/4] Python detected. Creating Virtual Environment...
python -m venv venv

echo [2/4] Activating Environment...
call venv\Scripts\activate

echo [3/4] Installing Dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install streamlit undetected-chromedriver

echo [4/4] Setting up Configuration...
if not exist .env (
    echo Creating default .env file...
    type nul > .env
)

echo.
echo ===================================================
echo      ✅ INSTALLATION COMPLETE!
echo      You can now double-click 'LAUNCH_VOLTS.bat'
echo ===================================================
pause
