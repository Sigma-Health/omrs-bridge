@echo off
echo Starting OpenMRS Bridge API Development Server...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy env.example .env
    echo.
    echo Please edit .env file with your database credentials before continuing.
    echo Press any key to continue...
    pause >nul
)

REM Start the development server
echo Starting development server...
python start_dev.py

pause 