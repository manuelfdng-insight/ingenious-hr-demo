"""
Integration tests for the CV Analysis Tool.

These tests verify that the entire application flow works correctly,
from file upload to displaying results.

Since Streamlit apps are challenging to test end-to-end, we focus on
testing the integration between components rather than UI interactions.
"""
import os
import pytest
import pandas as pd
from unittest.mock import patch, Mock, MagicMock
import streamlit as st
import uuid
import time

# Import app and components for testing
from app import main, APIClient, extract_text_from_file


@pytest.fixture
def mock_session_state():
    """Mock Streamlit's session state."""
    with patch('streamlit.session_state', {}) as mock_state:
        yield mock_state


@pytest.fixture
def mock_streamlit():
    """Mock key Streamlit functions used in the app."""
    with patch('streamlit.title') as mock_title, \
            patch('streamlit.header') as mock_header, \
            patch('streamlit.subheader') as mock_subheader, \
            patch('streamlit.sidebar.file_uploader') as mock_file_uploader, \
            patch('streamlit.sidebar.text_area') as mock_text_area, \
            patch('streamlit.sidebar.button') as mock_button, \
            patch('streamlit.spinner') as mock_spinner, \
            patch('streamlit.progress') as mock_progress, \
            patch('streamlit.tabs') as mock_tabs, \
            patch('streamlit.columns') as mock_columns, \
            patch('streamlit.dataframe') as mock_dataframe, \
            patch('streamlit.markdown') as mock_markdown, \
            patch('streamlit.info') as mock_info, \
            patch('streamlit.error') as mock_error, \
            patch('streamlit.success') as mock_success, \
            patch('streamlit.metric') as mock_metric, \
            patch('streamlit.expander') as mock_expander:

        yield {
            'title': mock_title,
            'header': mock_header,
            'subheader': mock_subheader,
            'file_uploader': mock_file_uploader,
            'text_area': mock_text_area,
            'button': mock_button,
            'spinner': mock_spinner,
            'progress': mock_progress,
            'tabs': mock_tabs,
            'columns': mock_columns,
            'dataframe': mock_dataframe,
            'markdown': mock_markdown,
            'info': mock_info,
            'error': mock_error,
            'success': mock_success,
            'metric': mock_metric,
            'expander': mock_expander
        }


@pytest.fixture
def sample_uploaded_files():
    """Create sample uploaded files for testing."""
    # Create mock CV files
    pdf_file = Mock()
    pdf_file.name = "candidate1.pdf"
    pdf_file.getvalue = lambda: b"%PDF-1.5 Mock PDF content"

    docx_file = Mock()
    docx_file.name = "candidate2.docx"
    docx_file.getvalue = lambda: b"PK Mock DOCX content"

    txt_file = Mock()
    txt_file.name = "candidate3.txt"
    txt_file.getvalue = lambda: b"This is a plain text CV for candidate 3"

    return [pdf_file, docx_file, txt_file]


# Define a context manager for mocking the spinner context
class MockSpinnerContext:
    def __init__(self, text):
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@patch('app.APIClient.create_chat')
@patch('app.extract_text_from_file')
def test_full_analysis_flow(mock_extract_text, mock_create_chat, mock_streamlit, mock_session_state, sample_uploaded_files):
    """Test the full CV analysis flow from upload to results display."""
    # Configure the mocks
    mock_streamlit['file_uploader'].return_value = sample_uploaded_files
    mock_streamlit['text_area'].return_value = "Test evaluation criteria"
    mock_streamlit['button'].return_value = True  # Process button clicked

    # Mock the spinner context manager
    mock_streamlit['spinner'].return_value = MockSpinnerContext(
        "Analyzing CVs...")

    # Mock tab creation
    mock_tabs = [Mock() for _ in range(len(sample_uploaded_files))]
    for i, tab in enumerate(mock_tabs):
        tab.__enter__ = Mock(return_value=tab)
        tab.__exit__ = Mock(return_value=None)
    mock_streamlit['tabs'].return_value = mock_tabs

    # Mock columns
    mock_cols = [Mock(), Mock()]
    mock_streamlit['columns'].return_value = mock_cols

    # Configure text extraction responses
    mock_extract_text.side_effect = [
        "Mock extracted text from PDF",
        "Mock extracted text from DOCX",
        "Mock extracted text from TXT"
    ]

    # Configure API responses
    mock_create_chat.side_effect = [
        {
            "thread_id": f"thread_{uuid.uuid4()}",
            "message_id": f"msg_{uuid.uuid4()}",
            "agent_response": "Analysis for candidate 1 with 75% match",
            "token_count": 150
        },
        {
            "thread_id": f"thread_{uuid.uuid4()}",
            "message_id": f"msg_{uuid.uuid4()}",
            "agent_response": "Analysis for candidate 2 with 88% match",
            "token_count": 150
        },
        {
            "thread_id": f"thread_{uuid.uuid4()}",
            "message_id": f"msg_{uuid.uuid4()}",
            "agent_response": "Analysis for candidate 3 with 65% match",
            "token_count": 150
        }
    ]

    # We need to patch time.sleep to avoid actual delays
    with patch('time.sleep'):
        # Run the main function
        main()

    # Verify file uploader was called
    mock_streamlit['file_uploader'].assert_called_once()

    # Verify text extraction was called for each file
    assert mock_extract_text.call_count == 3

    # Verify API was called for each CV
    assert mock_create_chat.call_count == 3

    # Verify session state was updated
    assert st.session_state['analysis_completed'] is True
    assert len(st.session_state['results']) == 3

    # Verify tabs were created for results
    mock_streamlit['tabs'].assert_called_once()


@patch('app.APIClient.create_chat')
@patch('app.extract_text_from_file')
def test_error_handling_during_analysis(mock_extract_text, mock_create_chat, mock_streamlit, mock_session_state, sample_uploaded_files):
    """Test error handling during the analysis process."""
    # Configure the mocks
    # Just one file
    mock_streamlit['file_uploader'].return_value = sample_uploaded_files[:1]
    mock_streamlit['text_area'].return_value = "Test evaluation criteria"
    mock_streamlit['button'].return_value = True  # Process button clicked

    # Mock the spinner context manager
    mock_streamlit['spinner'].return_value = MockSpinnerContext(
        "Analyzing CVs...")

    # Configure text extraction to succeed
    mock_extract_text.return_value = "Mock extracted text from PDF"

    # Configure API to fail
    mock_create_chat.side_effect = Exception("API connection error")

    # We need to patch time.sleep to avoid actual delays
    with patch('time.sleep'):
        # Run the main function
        main()

    # Verify error was shown
    mock_streamlit['error'].assert_called()

    # Verify session state was updated even with error
    assert st.session_state['analysis_completed'] is True
    assert len(st.session_state['results']) == 1

    # Verify error is captured in the result
    result = st.session_state['results'][0]
    assert "Analysis failed" in result["Analysis"]


@patch('pandas.DataFrame.to_csv')
def test_export_results_functionality(mock_to_csv, mock_streamlit, mock_session_state):
    """Test the export results functionality."""
    # Set up session state with some results
    st.session_state['analysis_completed'] = True
    st.session_state['results'] = [
        {
            "CV Name": "candidate1.pdf",
            "Analysis": "Analysis for candidate 1 with 75% match",
            "Thread ID": "thread_123",
            "Message ID": "msg_456"
        },
        {
            "CV Name": "candidate2.docx",
            "Analysis": "Analysis for candidate 2 with 88% match",
            "Thread ID": "thread_789",
            "Message ID": "msg_012"
        }
    ]

    # Configure mocks
    mock_to_csv.return_value = "mocked,csv,content"
    mock_streamlit['sidebar.download_button'].return_value = True

    # Run the main function
    main()

    # Verify DataFrame conversion was called
    mock_to_csv.assert_called_once()

    # Verify download button was displayed
    mock_streamlit['sidebar.download_button'].assert_called_once()


@patch('re.search')
def test_score_extraction_in_summary(mock_re_search, mock_streamlit, mock_session_state):
    """Test extraction of score percentages from analysis text."""
    # Configure the mock to simulate finding percentages
    mock_re_search.side_effect = [
        Mock(group=lambda x: "75"),
        Mock(group=lambda x: "88"),
        None  # Simulate no match for the third entry
    ]

    # Set up session state with results
    st.session_state['analysis_completed'] = True
    st.session_state['results'] = [
        {
            "CV Name": "candidate1.pdf",
            "Analysis": "Analysis for candidate 1 with 75% match",
            "Thread ID": "thread_123",
            "Message ID": "msg_456"
        },
        {
            "CV Name": "candidate2.docx",
            "Analysis": "Analysis for candidate 2 with 88% match",
            "Thread ID": "thread_789",
            "Message ID": "msg_012"
        },
        {
            "CV Name": "candidate3.txt",
            "Analysis": "Analysis for candidate 3 with no percentage",
            "Thread ID": "thread_345",
            "Message ID": "msg_678"
        }
    ]

    # Run the main function
    with patch('pandas.DataFrame') as mock_df:
        main()

    # Verify score extraction was attempted for each result
    assert mock_re_search.call_count == 3


def test_info_display_with_no_files(mock_streamlit):
    """Test that info message is shown when no files are uploaded."""
    # Configure file uploader to return an empty list
    mock_streamlit['file_uploader'].return_value = []

    # Run the main function
    main()

    # Verify info message was displayed
    mock_streamlit['info'].assert_called_once()

    # Verify expander was shown with example
    mock_streamlit['expander'].assert_called_once()


@patch('app.APIClient.submit_feedback')
def test_feedback_submission(mock_submit_feedback, mock_streamlit, mock_session_state):
    """Test feedback submission functionality."""
    # Configure mocks
    mock_submit_feedback.return_value = {
        "message": "Feedback submitted successfully"}

    # Set up session state with results
    st.session_state['analysis_completed'] = True
    st.session_state['results'] = [
        {
            "CV Name": "candidate1.pdf",
            "Analysis": "Analysis for candidate 1 with 75% match",
            "Thread ID": "thread_123",
            "Message ID": "msg_456"
        }
    ]

    # Set up tab mocking
    mock_tab = Mock()
    mock_tab.__enter__ = Mock(return_value=mock_tab)
    mock_tab.__exit__ = Mock(return_value=None)
    mock_streamlit['tabs'].return_value = [mock_tab]

    # Set up button clicks - first column button clicked (helpful)
    mock_cols = [Mock(), Mock()]
    mock_cols[0].button.return_value = True
    mock_cols[1].button.return_value = False
    mock_streamlit['columns'].return_value = mock_cols

    # Run the main function
    main()

    # Verify feedback submission was called with correct parameters
    mock_submit_feedback.assert_called_once_with(
        "msg_456", "thread_123", True
    )

    # Reset for negative feedback test
    mock_submit_feedback.reset_mock()
    mock_cols[0].button.return_value = False
    mock_cols[1].button.return_value = True

    # Run the main function again
    main()

    # Verify feedback submission was called with correct parameters
    mock_submit_feedback.assert_called_once_with(
        "msg_456", "thread_123", False
    )
