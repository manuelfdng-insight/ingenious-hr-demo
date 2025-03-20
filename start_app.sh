#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting CV Analysis Tool...${NC}"

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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}.env file not found. Creating a template...${NC}"
    echo "API_USERNAME=your_username_here" > .env
    echo "API_PASSWORD=your_password_here" >> .env
    echo "API_BASE_URL=https://hr-demo-app.ambitiousriver-e696f55c.australiaeast.azurecontainerapps.io/api/v1" >> .env
    echo "REVISION_ID=5ccc4a42-1e24-4b82-a550-e7e9c6ffa48b" >> .env
    echo "# Add your full Azure Blob Storage URL with SAS token" >> .env
    echo "AZURE_BLOB_STORAGE_URL=https://storageaccount.blob.core.windows.net/container/blob?sastoken" >> .env
    echo "# Azure OpenAI API settings" >> .env
    echo "AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com" >> .env
    echo "AZURE_OPENAI_KEY=your_api_key_here" >> .env
    echo "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini" >> .env
    echo -e "${RED}Please edit the .env file with your actual credentials before proceeding.${NC}"
    echo -e "${RED}Especially ensure the Azure OpenAI API credentials are provided for CV comparison summary.${NC}"
    exit 1
fi

# Start Streamlit app
echo -e "${GREEN}Starting Streamlit app...${NC}"
streamlit run app.py

echo -e "${GREEN}All servers stopped. Goodbye!${NC}"