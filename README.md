# CV Analysis Tool

A Streamlit-based application that analyzes multiple CV/resume documents against user-defined criteria, providing detailed feedback and comparison tools for recruitment processes.

![CV Analysis Tool](https://via.placeholder.com/800x400?text=CV+Analysis+Tool)

## Overview

The CV Analysis Tool interfaces with the Ingenious API to help recruiters and hiring managers efficiently evaluate multiple candidate CVs against specific job requirements. The application provides a user-friendly interface for uploading documents, defining evaluation criteria, and reviewing analysis results with visual comparisons.

### Key Features

- **Multi-CV Upload**: Support for PDF, DOCX, and TXT file formats
- **Customizable Criteria**: Define specific evaluation criteria for candidate assessment
- **Individual Analysis**: Detailed breakdown of each CV against specified criteria
- **Match Scoring**: Visual representation of how well each candidate matches requirements
- **Comparative Summary**: At-a-glance view of all candidates' match percentages
- **Feedback System**: Rate the quality of analysis to improve future results
- **Export Functionality**: Download analysis results in CSV format

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm (for the mock API server)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/cv-analysis-tool.git
   cd cv-analysis-tool
   ```

2. **Set up the mock API server**

   ```bash
   # Install json-server globally
   npm install -g json-server

   # Start the server with the provided configuration
   json-server --watch db.json --routes routes.json --port 3000
   ```

3. **Install Python dependencies**

   ```bash
   # Create and activate a virtual environment (optional but recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install required packages
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   streamlit run app.py
   ```

5. **Access the application**

   Open your browser and navigate to `http://localhost:8501`

## How to Use

1. **Upload CVs**: Use the sidebar to upload one or more CV files (PDF, DOCX, or TXT)
2. **Define Criteria**: Enter evaluation criteria in the text area provided
3. **Run Analysis**: Click the "Analyze CVs" button to process all documents
4. **Review Results**:
   - Navigate between individual tabs to see detailed analysis for each CV
   - Use the summary table to compare all candidates
   - Provide feedback using the thumbs up/down buttons
5. **Export Data**: Download results as CSV for further processing or sharing

## Project Structure

- **app.py**: Main Streamlit application file containing the UI and API integration logic
- **db.json**: Mock database file for simulating API responses during development
- **requirements.txt**: Python dependencies for the project
- **.gitignore**: Specifies files to exclude from version control

### Component Breakdown

#### APIClient Class

Handles all interactions with the Ingenious API, including:

- Submitting CVs for analysis
- Retrieving conversation history
- Sending user feedback on analysis quality

#### Text Extraction Functions

Utilities that handle various document formats:

- `extract_text_from_file()`: Detects file type and routes to appropriate extractor
- `extract_text_from_pdf()`: Processes PDF documents using PyPDF2
- `extract_text_from_docx()`: Extracts text from Word documents using docx2txt

#### UI Components

The application is divided into:

- Sidebar for input controls (file upload, criteria definition)
- Tab-based interface for individual CV analysis
- Summary table for at-a-glance comparison
- Feedback mechanisms for continuous improvement

## API Integration

The application interacts with the following API endpoints:

- `POST /api/v1/chat`: Submit CVs for analysis
- `GET /api/v1/conversations/{thread_id}`: Retrieve conversation history
- `PUT /api/v1/messages/{message_id}/feedback`: Submit feedback on analysis quality

During development, these endpoints are mocked via json-server using the provided db.json file.

## Customization Options

- Modify the `API_BASE_URL` in app.py to connect to a different server
- Extend `extract_text_from_file()` to support additional document formats
- Adjust the UI layout by modifying the Streamlit component structure
- Enhance visualization options in the individual analysis tabs
