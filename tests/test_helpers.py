"""
Tests for utility helper functions.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure


def test_convert_text_to_job_criteria_json():
    """Test conversion of text to job criteria JSON."""
    # Sample job description text
    job_text = "This is a sample job description for a software developer position."

    # Call the function
    result = convert_text_to_job_criteria_json(job_text)

    # Verify the result
    assert isinstance(result, dict)
    assert "job_criteria_text" in result
    assert result["job_criteria_text"] == job_text


def test_convert_text_to_job_criteria_json_empty_text():
    """Test conversion of empty text to job criteria JSON."""
    # Empty job description text
    job_text = ""

    # Call the function
    result = convert_text_to_job_criteria_json(job_text)

    # Verify the result
    assert isinstance(result, dict)
    assert "job_criteria_text" in result
    assert result["job_criteria_text"] == ""


def test_convert_text_to_job_criteria_json_special_chars():
    """Test conversion of text with special characters to job criteria JSON."""
    # Job description text with special characters
    job_text = "Job description with special characters: !@#$%^&*()_+{}[]|\\"

    # Call the function
    result = convert_text_to_job_criteria_json(job_text)

    # Verify the result
    assert isinstance(result, dict)
    assert "job_criteria_text" in result
    assert result["job_criteria_text"] == job_text


def test_update_job_criteria_in_azure_success(mock_blob_storage_url):
    """Test successful update of job criteria in Azure."""
    # Sample job criteria
    job_criteria = {
        "job_criteria_text": "Sample job description"
    }

    # Setup mocks
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobClient.from_blob_url') as mock_blob_client_factory, \
            patch('streamlit.info') as mock_info, \
            patch('streamlit.success') as mock_success:

        # Setup mock blob client
        mock_blob_client = MagicMock()
        mock_blob_client_factory.return_value = mock_blob_client

        # Call the function
        result = update_job_criteria_in_azure(job_criteria)

        # Verify the blob was uploaded correctly
        mock_blob_client_factory.assert_called_once_with(mock_blob_storage_url)
        mock_blob_client.upload_blob.assert_called_once()
        args, kwargs = mock_blob_client.upload_blob.call_args

        # Verify the payload
        expected_content = json.dumps(job_criteria, indent=2)
        assert args[0] == expected_content
        assert kwargs['overwrite'] is True

        # Verify success message was displayed
        mock_success.assert_called_once()
        assert result is True


def test_update_job_criteria_in_azure_error(mock_blob_storage_url):
    """Test error handling during update of job criteria in Azure."""
    # Sample job criteria
    job_criteria = {
        "job_criteria_text": "Sample job description"
    }

    # Setup mocks
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobClient.from_blob_url') as mock_blob_client_factory, \
            patch('streamlit.error') as mock_error:

        # Setup mock blob client to raise an exception
        mock_blob_client = MagicMock()
        mock_blob_client.upload_blob.side_effect = Exception(
            "Blob upload failed")
        mock_blob_client_factory.return_value = mock_blob_client

        # Call the function
        result = update_job_criteria_in_azure(job_criteria)

        # Verify error was displayed
        mock_error.assert_called()
        assert "Error updating job criteria: Blob upload failed" in mock_error.call_args_list[
            0][0][0]
        assert result is False


def test_update_job_criteria_in_azure_missing_url():
    """Test handling of missing blob storage URL."""
    # Sample job criteria
    job_criteria = {
        "job_criteria_text": "Sample job description"
    }

    # Setup mocks with empty URL
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": ""}), \
            patch('streamlit.error') as mock_error:

        # Call the function
        result = update_job_criteria_in_azure(job_criteria)

        # Verify error was displayed
        mock_error.assert_called()
        assert result is False
