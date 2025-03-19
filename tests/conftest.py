"""
Pytest configuration and fixtures for CV Analysis Tool tests.
"""
from app import APIClient, extract_text_from_file, extract_text_from_pdf, extract_text_from_docx
import os
import json
import pytest
from io import BytesIO
import pandas as pd
import streamlit as st
import requests
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import app
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Import components from app.py


@pytest.fixture
def mock_pdf_file():
    """Create a mock PDF file for testing."""
    # This is a simple BytesIO object that pretends to be a PDF
    class MockPDF:
        def __init__(self):
            self.name = "test_cv.pdf"
            self._content = b"%PDF-1.4 mock PDF content"

        def getvalue(self):
            return self._content

    return MockPDF()


@pytest.fixture
def mock_docx_file():
    """Create a mock DOCX file for testing."""
    class MockDOCX:
        def __init__(self):
            self.name = "test_cv.docx"
            self._content = b"PK mock DOCX content"

        def getvalue(self):
            return self._content

    return MockDOCX()


@pytest.fixture
def mock_txt_file():
    """Create a mock TXT file for testing."""
    class MockTXT:
        def __init__(self):
            self.name = "test_cv.txt"
            self._content = b"This is a mock CV with skills in Python, JavaScript, and React."

        def getvalue(self):
            return self._content

    return MockTXT()


@pytest.fixture
def sample_cv_text():
    """Sample CV text for testing."""
    return """
    John Smith
    Email: john.smith@example.com
    Phone: (123) 456-7890
    
    EXPERIENCE
    Senior Software Engineer, XYZ Corp (2021-Present)
    - Developed Python applications for data processing
    - Created React components for web dashboard
    - Led a team of 3 junior developers
    
    Software Developer, ABC Inc (2018-2021)
    - Built RESTful APIs using Flask
    - Implemented front-end features with JavaScript
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology (2014-2018)
    
    SKILLS
    Programming: Python, JavaScript, React, Flask
    Tools: Git, Docker, AWS
    """


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("API_BASE_URL", "https://mock-api-url.com/api/v1")
    monkeypatch.setenv("API_USERNAME", "test_user")
    monkeypatch.setenv("API_PASSWORD", "test_pass")
    monkeypatch.setenv("REVISION_ID", "test-revision-id")


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "thread_id": "thread_test123",
        "message_id": "msg_test456",
        "agent_response": """
        **Analysis Results:**
        - **Technical Skills:** Candidate has strong Python and JavaScript experience with React. (Score: 3/3)
        - **Experience:** 7 years total experience in software development. Exceeds requirement. (Score: 3/3)
        - **Education:** Bachelor's in Computer Science. Meets requirement. (Score: 3/3)
        - **Communication Skills:** Well-written CV with clear descriptions. (Score: 2/3)
        - **Projects:** Limited details on specific projects. (Score: 1/3)
        
        **Overall Match:** 12/15 (80%)
        """,
        "token_count": 150,
        "max_token_count": 8192,
        "memory_summary": "Candidate has strong technical skills and educational background."
    }


@pytest.fixture
def mock_conversation_history():
    """Mock conversation history for testing."""
    return [
        {
            "id": "msg_12345",
            "user_id": "user_test",
            "thread_id": "thread_test123",
            "message_id": "msg_12345",
            "positive_feedback": None,
            "timestamp": "2025-03-19T10:00:00Z",
            "role": "user",
            "content": "Analyze this CV against my criteria",
            "content_filter_results": None
        },
        {
            "id": "msg_test456",
            "user_id": "user_test",
            "thread_id": "thread_test123",
            "message_id": "msg_test456",
            "positive_feedback": None,
            "timestamp": "2025-03-19T10:01:00Z",
            "role": "assistant",
            "content": """
            **Analysis Results:**
            - **Technical Skills:** Candidate has strong Python and JavaScript experience with React. (Score: 3/3)
            - **Experience:** 7 years total experience in software development. Exceeds requirement. (Score: 3/3)
            - **Education:** Bachelor's in Computer Science. Meets requirement. (Score: 3/3)
            - **Communication Skills:** Well-written CV with clear descriptions. (Score: 2/3)
            - **Projects:** Limited details on specific projects. (Score: 1/3)
            
            **Overall Match:** 12/15 (80%)
            """,
            "content_filter_results": None
        }
    ]


@pytest.fixture
def mock_feedback_response():
    """Mock feedback response for testing."""
    return {
        "message": "Feedback submitted successfully"
    }


@pytest.fixture
def mock_requests():
    """Mock requests library for API testing."""
    with patch('requests.post') as mock_post, \
            patch('requests.get') as mock_get, \
            patch('requests.put') as mock_put:

        # Configure the mocks
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        yield {
            'post': mock_post,
            'get': mock_get,
            'put': mock_put,
            'mock_response': mock_response
        }
