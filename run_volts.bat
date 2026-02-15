@echo off
TITLE VOLTS | CLIENT ACQUISITION SYSTEM
COLOR 0A

echo ===================================================
echo      VOLTS | CLIENT ACQUISITION SYSTEM
echo      "Powering High-End Growth"
echo ===================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org (Tick "Add to PATH").
    pause
    exit
)

:: 2. Check/Create Virtual Environment
if not exist "venv" (
    echo [SETUP] Creating Virtual Environment (First Run Only)...
    python -m venv venv
)

:: 3. Activate Venv
call venv\Scripts\activate

:: 4. Install Dependencies
echo [SETUP] Checking Dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

:: 5. Launch App
echo.
echo [SYSTEM] Starting VOLTS Command Center...
echo.
streamlit run main.py

pause
