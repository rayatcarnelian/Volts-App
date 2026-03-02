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

echo [1/5] Creating Virtual Environment...
python -m venv venv

echo [2/5] Activating Environment...
call venv\Scripts\activate

echo [3/5] Installing Dependencies (This may take a while)...
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium

echo [4/5] Creating Desktop Shortcut...
set SCRIPT="%TEMP%\CreateShortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\VOLTS.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0LAUNCH_VOLTS.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "Launch Volts App" >> %SCRIPT%
echo oLink.IconLocation = "%~dp0app.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%
echo Shortcut created on Desktop!

echo [5/5] Configuration...
if not exist .env (
    echo Creating default .env variable template...
    type nul > .env
    echo STRIPE_SECRET_KEY= >> .env
    echo STRIPE_PRICE_ID= >> .env
    echo GEMINI_API_KEY= >> .env
    echo OPENAI_API_KEY= >> .env
    echo REPLICATE_API_TOKEN= >> .env
    echo GMAIL_USER= >> .env
    echo GMAIL_APP_PASS= >> .env
    echo SENTRY_DSN= >> .env
)
start notepad .env

echo.
echo ===================================================
echo      ✅ INSTALLATION COMPLETE!
echo      1. Fill in the .env file opened.
echo      2. Double-click 'VOLTS.lnk' on your Desktop to Launch.
echo ===================================================
pause
