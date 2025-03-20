"""
Tests for UI components and utilities.
"""

import pytest
import base64
from unittest.mock import patch, MagicMock
from ui.components import create_download_link, process_api_response, display_feedback_buttons


def test_create_download_link():
    """Test creation of a download link."""
    # Call the function
    result = create_download_link(
        content="Test content",
        filename="test.txt",
        text="Download Test"
    )

    # Encode content for comparison
    b64 = base64.b64encode("Test content".encode()).decode()
    expected = f'<a href="data:file/txt;base64,{b64}" download="test.txt">Download Test</a>'

    # Verify the link was created correctly
    assert result == expected


def test_process_api_response_successful():
    """Test processing a successful API response."""
    # Create a sample response
    response_data = {
        "agent_response": "Analysis result"
    }

    # Call the function
    result = process_api_response(response_data)

    # Verify the result
    assert result == "Analysis result"


def test_process_api_response_missing_response():
    """Test processing an API response with missing agent_response."""
    # Create a sample response
    response_data = {
        "status": "success",
        # No agent_response
    }

    # Call the function
    result = process_api_response(response_data)

    # Verify the result
    assert result == "Analysis failed to retrieve a response"


def test_process_api_response_error():
    """Test error handling in process_api_response."""
    # Create a sample response that will cause an error
    response_data = None

    # Call the function with error patching
    with patch('streamlit.error') as mock_error:
        result = process_api_response(response_data)

        # Verify error was displayed
        mock_error.assert_called_once()
        assert "Error processing API response" in mock_error.call_args[0][0]

        # Verify the result contains the error message
        assert "Error processing analysis" in result


def test_display_feedback_buttons_positive(mock_feedback_response):
    """Test display of positive feedback button."""
    # Create a sample result
    result = {
        "Message ID": "sample-message-id",
        "Thread ID": "sample-thread-id"
    }

    # Setup mocks for positive feedback
    with patch('streamlit.columns', return_value=[MagicMock(), MagicMock()]) as mock_columns, \
            patch.object(MagicMock, 'button', side_effect=[True, False]) as mock_button, \
            patch('streamlit.success') as mock_success, \
            patch('services.APIClient.submit_feedback', return_value=mock_feedback_response) as mock_submit_feedback:

        # Call the function
        display_feedback_buttons(result, 0)

        # Verify the feedback was submitted
        mock_submit_feedback.assert_called_once_with(
            "sample-message-id",
            "sample-thread-id",
            True
        )

        # Verify success message was displayed
        mock_success.assert_called_once()
        assert "Thank you for your feedback!" in mock_success.call_args[0][0]


def test_display_feedback_buttons_negative(mock_feedback_response):
    """Test display of negative feedback button."""
    # Create a sample result
    result = {
        "Message ID": "sample-message-id",
        "Thread ID": "sample-thread-id"
    }

    # Setup mocks for negative feedback
    with patch('streamlit.columns', return_value=[MagicMock(), MagicMock()]) as mock_columns, \
            patch.object(MagicMock, 'button', side_effect=[False, True]) as mock_button, \
            patch('streamlit.success') as mock_success, \
            patch('services.APIClient.submit_feedback', return_value=mock_feedback_response) as mock_submit_feedback:

        # Call the function
        display_feedback_buttons(result, 0)

        # Verify the feedback was submitted
        mock_submit_feedback.assert_called_once_with(
            "sample-message-id",
            "sample-thread-id",
            False
        )

        # Verify success message was displayed
        mock_success.assert_called_once()
        assert "Thank you for your feedback. We'll improve our analysis." in mock_success.call_args[
            0][0]


def test_display_feedback_buttons_no_click():
    """Test when no feedback button is clicked."""
    # Create a sample result
    result = {
        "Message ID": "sample-message-id",
        "Thread ID": "sample-thread-id"
    }

    # Setup mocks with no button clicks
    with patch('streamlit.columns', return_value=[MagicMock(), MagicMock()]) as mock_columns, \
            patch.object(MagicMock, 'button', return_value=False) as mock_button, \
            patch('streamlit.success') as mock_success, \
            patch('services.APIClient.submit_feedback') as mock_submit_feedback:

        # Call the function
        display_feedback_buttons(result, 0)

        # Verify the feedback was not submitted
        mock_submit_feedback.assert_not_called()

        # Verify no success message was displayed
        mock_success.assert_not_called()
