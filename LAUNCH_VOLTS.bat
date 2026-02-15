@echo off
TITLE VOLTS COMMAND CENTER
color 0B

echo ⚡ INITIALIZING VOLTS SYSTEMS...

if not exist venv (
    echo [ERROR] Virtual Environment not found! 
    echo Please run INSTALL_VOLTS.bat first.
    pause
    exit /b
)

:: Activate Venv
call venv\Scripts\activate

:: Check dependencies again lightly
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Dependencies might be missing. Attempting repair...
    pip install -r requirements.txt
)

:: Run App
echo.
echo >> LAUNCHING DASHBOARD...
echo.
streamlit run main.py

pause
