@echo off
echo Starting CV Analysis Tool...

:: Check if json-server is installed
where json-server >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo json-server is not installed. Installing globally...
    npm install -g json-server
)

:: Check if Python virtual environment exists
if not exist .venv\ (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate
    echo Installing Python dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

:: Start json-server in a new window
echo Starting JSON Server...
start "JSON Server" cmd /c "json-server --watch db.json --routes routes.json --port 3000"

:: Give the JSON server a moment to start
timeout /t 2 >nul

:: Start Streamlit app
echo Starting Streamlit app...
streamlit run app.py

:: Note: When you close the Streamlit window, you'll need to manually close the JSON Server window
echo Note: Remember to close the JSON Server window when you're done!