"""
Tests for the APIClient class that handles interactions with the Ingenious API.
"""
import json
import pytest
from unittest.mock import patch, Mock

# Import the APIClient class from app.py
from app import APIClient

# Base URL used in the app
API_BASE_URL = "http://localhost:3000/api/v1"


def test_create_chat(mock_requests, sample_cv_text, sample_evaluation_criteria, mock_api_response):
    """Test creating a new chat conversation."""
    # Configure the mock response
    mock_response = mock_requests['mock_response']
    mock_response.json.return_value = mock_api_response
    mock_requests['post'].return_value = mock_response

    # Call the method under test
    result = APIClient.create_chat(sample_cv_text, sample_evaluation_criteria)

    # Verify the API was called correctly
    mock_requests['post'].assert_called_once()
    call_args = mock_requests['post'].call_args

    # Check that the URL is correct
    assert call_args[0][0] == f"{API_BASE_URL}/chat"

    # Check that the payload contains expected data
    payload = call_args[1]['json']
    assert "user_prompt" in payload
    assert sample_cv_text in payload["user_prompt"]
    assert sample_evaluation_criteria in payload["user_prompt"]
    assert payload["conversation_flow"] == "cv_analysis"

    # Check that the result matches the mock response
    assert result == mock_api_response


def test_create_chat_with_thread_id(mock_requests, sample_cv_text, sample_evaluation_criteria, mock_api_response):
    """Test creating a chat with an existing thread ID."""
    # Configure the mock response
    mock_response = mock_requests['mock_response']
    mock_response.json.return_value = mock_api_response
    mock_requests['post'].return_value = mock_response

    # Call the method with a thread ID
    thread_id = "existing_thread_123"
    result = APIClient.create_chat(
        sample_cv_text, sample_evaluation_criteria, thread_id)

    # Verify the thread ID was passed correctly
    call_args = mock_requests['post'].call_args
    payload = call_args[1]['json']
    assert payload["thread_id"] == thread_id


def test_create_chat_error_handling(mock_requests, sample_cv_text, sample_evaluation_criteria):
    """Test handling of API errors in create_chat."""
    # Make the mock raise an exception
    mock_requests['post'].side_effect = Exception("API connection error")

    # Call the method
    with patch('streamlit.error') as mock_st_error:
        result = APIClient.create_chat(
            sample_cv_text, sample_evaluation_criteria)

    # Verify error was logged to Streamlit
    mock_st_error.assert_called_once()

    # Verify an error result was returned
    assert "error" in result
    assert "API connection error" in result["error"]


def test_get_conversation(mock_requests, mock_conversation_history):
    """Test retrieving conversation history."""
    # Configure the mock response
    mock_response = mock_requests['mock_response']
    mock_response.json.return_value = mock_conversation_history
    mock_requests['get'].return_value = mock_response

    # Call the method under test
    thread_id = "thread_test123"
    result = APIClient.get_conversation(thread_id)

    # Verify the API was called correctly
    mock_requests['get'].assert_called_once_with(
        f"{API_BASE_URL}/conversations/{thread_id}")

    # Check that the result matches the mock response
    assert result == mock_conversation_history


def test_get_conversation_error_handling(mock_requests):
    """Test handling of API errors in get_conversation."""
    # Make the mock raise an exception
    mock_requests['get'].side_effect = Exception("API connection error")

    # Call the method
    with patch('streamlit.error') as mock_st_error:
        result = APIClient.get_conversation("thread_test123")

    # Verify error was logged to Streamlit
    mock_st_error.assert_called_once()

    # Verify an empty list was returned
    assert result == []


def test_submit_feedback(mock_requests, mock_feedback_response):
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

    # Check that the payload contains expected data
    payload = call_args[1]['json']
    assert payload["thread_id"] == thread_id
    assert payload["message_id"] == message_id
    assert payload["positive_feedback"] == positive

    # Check that the result matches the mock response
    assert result == mock_feedback_response


def test_submit_feedback_error_handling(mock_requests):
    """Test handling of API errors in submit_feedback."""
    # Make the mock raise an exception
    mock_requests['put'].side_effect = Exception("API connection error")

    # Call the method
    with patch('streamlit.error') as mock_st_error:
        result = APIClient.submit_feedback(
            "msg_test456", "thread_test123", True)

    # Verify error was logged to Streamlit
    mock_st_error.assert_called_once()

    # Verify an error result was returned
    assert "error" in result
    assert "API connection error" in result["error"]
