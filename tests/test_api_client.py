"""
Tests for the API client that interacts with the FastAgent API.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from services.api_client import APIClient
from config import API_BASE_URL, API_USERNAME, API_PASSWORD, DEFAULT_REVISION_ID


def test_create_chat_successful(mock_api_response):
    """Test successful creation of a chat session."""
    with patch('requests.post') as mock_post:
        # Setup the mock
        mock_post.return_value.json.return_value = mock_api_response
        mock_post.return_value.raise_for_status = MagicMock()

        # Call the function
        response = APIClient.create_chat(
            "Sample CV content", thread_id="test-thread", identifier="test-id")

        # Verify the response
        assert response == mock_api_response

        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['thread_id'] == "test-thread"
        assert kwargs['json']['conversation_flow'] == "hr_insights"
        assert kwargs['auth'] == (API_USERNAME, API_PASSWORD)

        # Verify the payload format
        user_prompt_data = json.loads(kwargs['json']['user_prompt'])
        assert user_prompt_data['revision_id'] == DEFAULT_REVISION_ID
        assert user_prompt_data['identifier'] == "test-id"
        assert user_prompt_data['Page_1'] == "Sample CV content"


def test_create_chat_error_handling():
    """Test error handling in create_chat."""
    with patch('requests.post') as mock_post, patch('streamlit.error') as mock_error:
        # Setup the mock to raise an exception
        mock_post.side_effect = Exception("API connection error")

        # Call the function
        response = APIClient.create_chat("Sample CV content")

        # Verify error was displayed
        mock_error.assert_called_once()
        assert "API Error: API connection error" in mock_error.call_args[0][0]

        # Verify the response contains the error
        assert "error" in response
        assert response["error"] == "API connection error"


def test_submit_feedback_successful(mock_feedback_response):
    """Test successful submission of feedback."""
    with patch('requests.put') as mock_put:
        # Setup the mock
        mock_put.return_value.json.return_value = mock_feedback_response
        mock_put.return_value.raise_for_status = MagicMock()

        # Call the function
        response = APIClient.submit_feedback(
            "sample-message-id",
            "sample-thread-id",
            True
        )

        # Verify the response
        assert response == mock_feedback_response

        # Verify the request was made correctly
        mock_put.assert_called_once()
        args, kwargs = mock_put.call_args
        assert kwargs['json']['thread_id'] == "sample-thread-id"
        assert kwargs['json']['message_id'] == "sample-message-id"
        assert kwargs['json']['positive_feedback'] is True
        assert kwargs['auth'] == (API_USERNAME, API_PASSWORD)


def test_submit_feedback_error_handling():
    """Test error handling in submit_feedback."""
    with patch('requests.put') as mock_put, patch('streamlit.error') as mock_error:
        # Setup the mock to raise an exception
        mock_put.side_effect = Exception("API connection error")

        # Call the function
        response = APIClient.submit_feedback(
            "sample-message-id",
            "sample-thread-id",
            True
        )

        # Verify error was displayed
        mock_error.assert_called_once()
        assert "API Error: API connection error" in mock_error.call_args[0][0]

        # Verify the response contains the error
        assert "error" in response
        assert response["error"] == "API connection error"
