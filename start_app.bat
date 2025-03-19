@echo off
echo Starting CV Analysis Tool...

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

:: Check if .env file exists
if not exist .env (
    echo .env file not found. Creating a template...
    echo API_USERNAME=your_username_here> .env
    echo API_PASSWORD=your_password_here>> .env
    echo API_BASE_URL=https://hr-demo-app.ambitiousriver-e696f55c.australiaeast.azurecontainerapps.io/api/v1>> .env
    echo REVISION_ID=5ccc4a42-1e24-4b82-a550-e7e9c6ffa48b>> .env
    echo Please edit the .env file with your actual credentials before proceeding.
    exit /b
)

:: Start Streamlit app
echo Starting Streamlit app...
streamlit run app.py

echo App closed. Goodbye!