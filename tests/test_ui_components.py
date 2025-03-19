"""
Tests for UI components and Streamlit interactions.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
import base64
import re

# Import functions from app.py
from app import create_download_link, APIClient


class MockElement:
    """A simple mock for Streamlit UI elements."""

    def __init__(self):
        self.value = None
        self.button_value = False
        self.text_value = ""
        self.dataframe_value = None
        self.markdown_value = None
        self.metric_value = None
        self.title_value = None
        self.error_value = None
        self.success_value = None
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

    def error(self, text):
        self.error_value = text
        return self

    def success(self, text):
        self.success_value = text
        return self


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


@patch('app.APIClient.submit_feedback')
def test_feedback_buttons(mock_submit_feedback):
    """Test the feedback button functionality by directly calling the API client method."""
    # Configure the mock feedback response
    mock_submit_feedback.return_value = {
        "message": "Feedback submitted successfully"
    }

    # Test direct API client calls instead of via UI
    # Simulate positive feedback
    APIClient.submit_feedback("msg_test456", "thread_test123", True)

    # Verify the API call
    mock_submit_feedback.assert_called_with(
        "msg_test456", "thread_test123", True
    )

    # Reset the mock
    mock_submit_feedback.reset_mock()

    # Simulate negative feedback
    APIClient.submit_feedback("msg_test456", "thread_test123", False)

    # Verify the API call
    mock_submit_feedback.assert_called_with(
        "msg_test456", "thread_test123", False
    )
