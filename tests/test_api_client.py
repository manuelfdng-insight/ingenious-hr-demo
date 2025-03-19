"""
Tests for the APIClient class that handles interactions with the FastAgent API.
"""
import json
import pytest
import os
from unittest.mock import patch, Mock, MagicMock

# Import the APIClient class from app.py
from app import APIClient

# Get API_BASE_URL from environment, or use a default for testing
API_BASE_URL = os.getenv("API_BASE_URL", "https://mock-api-url.com/api/v1")


def test_create_chat(mock_requests, sample_cv_text, mock_api_response, mock_env_vars):
    """Test creating a new chat conversation."""
    # Configure the mock response
    mock_response = mock_requests['mock_response']
    mock_response.json.return_value = mock_api_response
    mock_requests['post'].return_value = mock_response

    # Call the method under test
    result = APIClient.create_chat(sample_cv_text)

    # Verify the API was called correctly
    mock_requests['post'].assert_called_once()
    call_args = mock_requests['post'].call_args

    # Check that the URL is correct
    assert call_args[0][0] == f"{API_BASE_URL}/chat"

    # Check authentication was used
    # Just check that auth is being used, don't verify the exact values
    assert 'auth' in call_args[1]

    # Check that the payload contains expected data
    payload = call_args[1]['json']
    assert "user_prompt" in payload
    assert "conversation_flow" in payload
    assert payload["conversation_flow"] == "hr_insights"

    # Check that the user_prompt JSON string contains expected elements
    user_prompt_data = json.loads(payload["user_prompt"])
    assert "revision_id" in user_prompt_data
    assert "identifier" in user_prompt_data
    assert "Page_1" in user_prompt_data
    assert sample_cv_text in user_prompt_data["Page_1"]

    # Check that the result matches the mock response
    assert result == mock_api_response


def test_create_chat_with_thread_id(mock_requests, sample_cv_text, mock_api_response, mock_env_vars):
    """Test creating a chat with an existing thread ID."""
    # Configure the mock response
    mock_response = mock_requests['mock_response']
    mock_response.json.return_value = mock_api_response
    mock_requests['post'].return_value = mock_response

    # Call the method with a thread ID
    thread_id = "existing_thread_123"
    result = APIClient.create_chat(sample_cv_text, thread_id=thread_id)

    # Verify the thread ID was passed correctly
    call_args = mock_requests['post'].call_args
    payload = call_args[1]['json']
    assert payload["thread_id"] == thread_id


@patch('streamlit.error')
def test_create_chat_error_handling(mock_st_error, mock_requests, sample_cv_text):
    """Test handling of API errors in create_chat."""
    # Configure the mock to raise an exception
    mock_requests['post'].side_effect = Exception("Mock API error")

    # Call the method
    result = APIClient.create_chat(sample_cv_text)

    # Verify the error was handled and returned in the result
    assert "error" in result
    assert "Mock API error" in result["error"]

    # Verify the error was displayed to the user
    mock_st_error.assert_called_once()


def test_submit_feedback(mock_requests, mock_feedback_response, mock_env_vars):
    """Test submitting feedback on an analysis."""
    # Configure the mock response
    mock_response = mock_requests['mock_response']
    mock_response.json.return_value = mock_feedback_response
    mock_requests['put'].return_value = mock_response

    # Call the method under test
    message_id = "msg_test456"
    thread_id = "thread_test123"
    positive = True
    result = APIClient.submit_feedback(message_id, thread_id, positive)

    # Verify the API was called correctly
    mock_requests['put'].assert_called_once()
    call_args = mock_requests['put'].call_args

    # Check that the URL is correct
    assert call_args[0][0] == f"{API_BASE_URL}/messages/{message_id}/feedback"

    # Check authentication was used
    # Just check that auth is being used, don't verify the exact values
    assert 'auth' in call_args[1]

    # Check that the payload contains expected data
    payload = call_args[1]['json']
    assert payload["thread_id"] == thread_id
    assert payload["message_id"] == message_id
    assert payload["positive_feedback"] == positive

    # Check that the result matches the mock response
    assert result == mock_feedback_response


@patch('app.requests.post')
@patch('streamlit.error')
def test_create_chat_error_handling(mock_st_error, mock_post, sample_cv_text):
    """Test handling of API errors in create_chat."""
    # Configure the mock to raise an exception
    mock_post.side_effect = Exception("Mock API error")

    # Call the method directly
    result = APIClient.create_chat(sample_cv_text)

    # Verify the error was handled and returned in the result
    assert "error" in result
    assert "Mock API error" in result["error"]

    # Verify the error was displayed to the user
    mock_st_error.assert_called_once()


@patch('app.requests.put')
@patch('streamlit.error')
def test_submit_feedback_error_handling(mock_st_error, mock_put):
    """Test handling of API errors in submit_feedback."""
    # Configure the mock to raise an exception
    mock_put.side_effect = Exception("Mock API error")

    # Call the method
    result = APIClient.submit_feedback("msg_id", "thread_id", True)

    # Verify the error was handled and returned in the result
    assert "error" in result
    assert "Mock API error" in result["error"]

    # Verify the error was displayed to the user
    mock_st_error.assert_called_once()
