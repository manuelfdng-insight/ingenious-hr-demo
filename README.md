# CV Analysis Tool

This is a Streamlit application that interfaces with the Ingenious API (mocked via json-server) to analyze multiple CVs against user-defined criteria.

## Setup Instructions

### 1. Set up the Mock API Server

First, set up the json-server to mock the Ingenious API:

```bash
# Install json-server
npm install -g json-server

# Start the server using the provided db.json file
json-server --watch db.json --routes routes.json --port 3000
```

### 2. Install the Required Python Packages

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Run the Streamlit Application

```bash
# Start the Streamlit app
streamlit run app.py
```

## Features

- **Upload Multiple CVs**: Support for PDF, DOCX, and TXT file formats
- **Custom Evaluation Criteria**: Define specific criteria for CV evaluation
- **Individual Analysis**: View detailed analysis for each CV
- **Summary View**: Compare results across multiple candidates
- **Feedback System**: Provide feedback on analysis quality
- **Export Results**: Download analysis results as CSV

## Application Structure

The application consists of:

1. **Sidebar**:

   - File upload section for CVs
   - Text area for defining evaluation criteria
   - Analysis trigger button
   - Export results button

2. **Main Content Area**:
   - Individual tabs for each CV analysis
   - Match score visualization
   - Feedback buttons
   - Summary table with all results

## API Integration

The application interacts with the following API endpoints:

- `POST /api/v1/chat`: Submit CVs for analysis
- `GET /api/v1/conversations/{thread_id}`: Retrieve conversation history
- `PUT /api/v1/messages/{message_id}/feedback`: Submit feedback on analysis

## Customization

You can modify the application by:

1. Updating the `API_BASE_URL` in the script if your json-server runs on a different port
2. Adding additional file format support in the `extract_text_from_file` function
3. Enhancing the analysis display with additional visualizations or metrics

## Notes

- The application uses a simulated delay between API calls to prevent overwhelming the server
- For production use, you would replace the mock API with the actual Ingenious API endpoints
"# ingenious-hr-demo" 
