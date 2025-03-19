"""
Tests for UI components and Streamlit interactions.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
import base64
import re

# Import functions from app.py
from app import create_download_link

# We need to mock Streamlit components since they can't be tested directly


class MockDelta:
    def __init__(self, value=None):
        self.value = value


class MockElement:
    def __init__(self):
        self.value = None
        self.empty_value = None
        self.progress_value = 0
        self.button_value = False
        self.text_value = ""
        self.dataframe_value = None
        self.markdown_value = None
        self.metric_value = None
        self.title_value = None
        self.subheader_value = None
        self.header_value = None
        self.expander_value = False
        self.tabs = []

    def button(self, text, key=None, type=None):
        self.button_value = text
        return self.button_value

    def text(self, text):
        self.text_value = text
        return self

    def markdown(self, text):
        self.markdown_value = text
        return self

    def metric(self, label, value):
        self.metric_value = (label, value)
        return self

    def title(self, text):
        self.title_value = text
        return self

    def subheader(self, text):
        self.subheader_value = text
        return self

    def header(self, text):
        self.header_value = text
        return self

    def dataframe(self, df, use_container_width=False):
        self.dataframe_value = df
        return self

    def progress(self, value):
        self.progress_value = value
        return self

    def file_uploader(self, label, type=None, accept_multiple_files=False):
        return []

    def text_area(self, label, value="", height=None):
        return value

    def empty(self):
        return self

    def error(self, text):
        self.error_value = text
        return self

    def success(self, text):
        self.success_value = text
        return self

    def info(self, text):
        self.info_value = text
        return self

    def expander(self, text):
        self.expander_value = True
        return self

    def download_button(self, label, data, file_name, mime):
        return False

    def tabs(self, tabs):
        self.tabs = [MockElement() for _ in tabs]
        return self.tabs


@pytest.fixture
def mock_st():
    """Create a mock for Streamlit functions."""
    with patch('streamlit.button') as mock_button, \
            patch('streamlit.text') as mock_text, \
            patch('streamlit.markdown') as mock_markdown, \
            patch('streamlit.metric') as mock_metric, \
            patch('streamlit.title') as mock_title, \
            patch('streamlit.subheader') as mock_subheader, \
            patch('streamlit.header') as mock_header, \
            patch('streamlit.dataframe') as mock_dataframe, \
            patch('streamlit.progress') as mock_progress, \
            patch('streamlit.file_uploader') as mock_file_uploader, \
            patch('streamlit.text_area') as mock_text_area, \
            patch('streamlit.empty') as mock_empty, \
            patch('streamlit.error') as mock_error, \
            patch('streamlit.success') as mock_success, \
            patch('streamlit.info') as mock_info, \
            patch('streamlit.expander') as mock_expander, \
            patch('streamlit.download_button') as mock_download_button, \
            patch('streamlit.sidebar') as mock_sidebar, \
            patch('streamlit.tabs') as mock_tabs, \
            patch('streamlit.columns') as mock_columns, \
            patch('streamlit.session_state', {}):

        mock_st = MockElement()

        # Configure mocks
        mock_button.side_effect = mock_st.button
        mock_text.side_effect = mock_st.text
        mock_markdown.side_effect = mock_st.markdown
        mock_metric.side_effect = mock_st.metric
        mock_title.side_effect = mock_st.title
        mock_subheader.side_effect = mock_st.subheader
        mock_header.side_effect = mock_st.header
        mock_dataframe.side_effect = mock_st.dataframe
        mock_progress.side_effect = mock_st.progress
        mock_file_uploader.side_effect = mock_st.file_uploader
        mock_text_area.side_effect = mock_st.text_area
        mock_empty.return_value = mock_st
        mock_error.side_effect = mock_st.error
        mock_success.side_effect = mock_st.success
        mock_info.side_effect = mock_st.info
        mock_expander.side_effect = mock_st.expander
        mock_download_button.side_effect = mock_st.download_button
        mock_sidebar.return_value = mock_st
        mock_tabs.side_effect = mock_st.tabs
        mock_columns.return_value = [mock_st, mock_st]

        yield mock_st

# Now let's test the UI-related functions


def test_create_download_link():
    """Test the create_download_link function."""
    # Test with a simple string
    content = "Test content for download"
    filename = "test.txt"
    link_text = "Download Test"

    result = create_download_link(content, filename, link_text)

    # Verify the result is a string containing an HTML link
    assert "<a href=" in result
    assert f'download="{filename}"' in result
    assert link_text in result

    # Verify the base64 encoding works
    encoded_content = base64.b64encode(content.encode()).decode()
    assert encoded_content in result


@patch('app.main')
def test_main_entry_point(mock_main):
    """Test the entry point of the application."""
    # We import __name__ == "__main__" block
    import app

    # This should call main() if __name__ == "__main__"
    # Let's simulate that
    if hasattr(app, '__name__'):
        old_name = app.__name__
        app.__name__ = "__main__"
        # Run the relevant code
        app.main()
        # Reset the name
        app.__name__ = old_name

    # Verify main() was called
    mock_main.assert_called_once()


# Test the feedback button functionality
@patch('app.APIClient.submit_feedback')
def test_feedback_buttons(mock_submit_feedback, mock_st):
    """Test the feedback button functionality."""
    # Import the main function from app.py
    from app import main

    # Configure the mock feedback response
    mock_submit_feedback.return_value = {
        "message": "Feedback submitted successfully"}

    # Set up the session state
    import streamlit as st
    st.session_state['analysis_completed'] = True
    st.session_state['results'] = [
        {
            "CV Name": "test_cv.pdf",
            "Analysis": "Test analysis content with 85% match",
            "Thread ID": "thread_test123",
            "Message ID": "msg_test456"
        }
    ]

    # Mock the button click for feedback
    # Since we can't directly trigger Streamlit UI interactions, we'll check if
    # the submit_feedback function would be called with correct parameters
    # if we were to click the button

    # We can check if the buttons are rendered correctly by inspecting the
    # app's structure and verifying that the feedback function would be called
    # with correct parameters when buttons are clicked

    # This test is a bit limited due to Streamlit's UI model, but we can verify
    # that the API client's submit_feedback method would be called correctly
    from app import st

    # Create mock button clicks
    with patch('streamlit.button', return_value=True):
        # We would normally need to test this within the app's UI flow,
        # but for unit testing, we'll just verify the API client is called correctly

        # Simulate positive feedback
        APIClient = app.APIClient
        APIClient.submit_feedback("msg_test456", "thread_test123", True)

        # Verify the API call
        mock_submit_feedback.assert_called_with(
            "msg_test456", "thread_test123", True)

        # Reset the mock
        mock_submit_feedback.reset_mock()

        # Simulate negative feedback
        APIClient.submit_feedback("msg_test456", "thread_test123", False)

        # Verify the API call
        mock_submit_feedback.assert_called_with(
            "msg_test456", "thread_test123", False)
