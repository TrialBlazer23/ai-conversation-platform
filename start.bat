@echo off
echo 🤖 Starting AI Conversation Platform...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -q -r requirements.txt

REM Run the application
echo.
echo Starting server...
echo Open your browser to: http://localhost:5000
echo.
python app.py