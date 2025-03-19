#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting CV Analysis Tool...${NC}"

# Check if json-server is installed
if ! command -v json-server &> /dev/null; then
    echo -e "${RED}json-server is not installed. Installing globally...${NC}"
    npm install -g json-server
fi

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Virtual environment not found. Creating one...${NC}"
    python -m venv .venv
    
    # Activate virtual environment based on OS
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows using Git Bash or similar
        source .venv/Scripts/activate
    else
        # Linux/macOS
        source .venv/bin/activate
    fi
    
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
else
    # Activate virtual environment based on OS
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows using Git Bash or similar
        source .venv/Scripts/activate
    else
        # Linux/macOS
        source .venv/bin/activate
    fi
fi

# Start json-server in the background
echo -e "${GREEN}Starting JSON Server...${NC}"
json-server --watch db.json --routes routes.json --port 3000 &
JSON_SERVER_PID=$!

# Give the JSON server a moment to start
sleep 2

# Start Streamlit app
echo -e "${GREEN}Starting Streamlit app...${NC}"
streamlit run app.py

# When Streamlit is stopped (Ctrl+C), also stop the JSON server
echo -e "${BLUE}Shutting down servers...${NC}"
kill $JSON_SERVER_PID

echo -e "${GREEN}All servers stopped. Goodbye!${NC}"