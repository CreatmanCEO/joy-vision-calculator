@echo off
chcp 65001 >nul
echo ========================================
echo Joy Vision Calculator - Installation
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt

echo [5/5] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your settings
)

echo.
echo Installation completed!
echo Next: Edit .env file, then run start.bat
pause
