"""
Tests for the Azure Blob Storage client.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from services.blob_storage import AzureBlobClient
from azure.storage.blob import BlobServiceClient, ContentSettings


@pytest.fixture
def mock_blob_service_client():
    """Mock BlobServiceClient for testing."""
    return MagicMock(spec=BlobServiceClient)


@pytest.fixture
def mock_blob_client():
    """Mock BlobClient for testing."""
    return MagicMock()


def test_azure_blob_client_initialization(mock_blob_storage_url, mock_blob_service_client):
    """Test initialization of AzureBlobClient."""
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobServiceClient', return_value=mock_blob_service_client):

        client = AzureBlobClient()

        # Verify the client was initialized correctly
        assert client.full_url == mock_blob_storage_url
        assert client.container_name == "container"
        assert client.account_url == "https://storageaccount.blob.core.windows.net"
        assert client.sas_token.startswith("sv=")
        assert client.blob_service_client == mock_blob_service_client


def test_azure_blob_client_missing_url():
    """Test handling of missing blob storage URL."""
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": ""}), \
            pytest.raises(ValueError) as excinfo:

        AzureBlobClient()

        # Verify error message
        assert "AZURE_BLOB_STORAGE_URL environment variable is not set or is empty" in str(
            excinfo.value)


def test_upload_blob_success(mock_blob_storage_url, mock_blob_service_client, mock_blob_client):
    """Test successful blob upload."""
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobServiceClient', return_value=mock_blob_service_client), \
            patch('streamlit.info') as mock_info, \
            patch('streamlit.success') as mock_success:

        # Setup the mock
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = mock_blob_storage_url

        # Initialize client and call upload_blob
        client = AzureBlobClient()
        result = client.upload_blob("Test content", "test-blob.json")

        # Verify the blob was uploaded correctly
        mock_blob_service_client.get_blob_client.assert_called_once_with(
            container="container",
            blob="test-blob.json"
        )
        mock_blob_client.upload_blob.assert_called_once()
        args, kwargs = mock_blob_client.upload_blob.call_args
        assert args[0] == "Test content"
        assert kwargs['overwrite'] is True

        # Verify the success message was displayed
        mock_success.assert_called_once()
        assert result is True


def test_upload_blob_error(mock_blob_storage_url, mock_blob_service_client, mock_blob_client):
    """Test error handling during blob upload."""
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobServiceClient', return_value=mock_blob_service_client), \
            patch('streamlit.error') as mock_error:

        # Setup the mock to raise an exception
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = mock_blob_storage_url
        mock_blob_client.upload_blob.side_effect = Exception(
            "Blob upload failed")

        # Initialize client and call upload_blob
        client = AzureBlobClient()
        result = client.upload_blob("Test content", "test-blob.json")

        # Verify error was displayed
        mock_error.assert_called()
        assert "Azure Blob Error during upload: Blob upload failed" in mock_error.call_args_list[
            0][0][0]
        assert result is False


def test_download_blob_success(mock_blob_storage_url, mock_blob_service_client, mock_blob_client):
    """Test successful blob download."""
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobServiceClient', return_value=mock_blob_service_client), \
            patch('streamlit.info') as mock_info, \
            patch('streamlit.success') as mock_success:

        # Setup the mock
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = mock_blob_storage_url
        mock_download_stream = MagicMock()
        mock_download_stream.readall.return_value = b"Downloaded content"
        mock_blob_client.download_blob.return_value = mock_download_stream

        # Initialize client and call download_blob
        client = AzureBlobClient()
        content = client.download_blob("test-blob.json")

        # Verify the blob was downloaded correctly
        mock_blob_service_client.get_blob_client.assert_called_once_with(
            container="container",
            blob="test-blob.json"
        )
        mock_blob_client.download_blob.assert_called_once()

        # Verify the success message was displayed
        mock_success.assert_called_once()
        assert content == "Downloaded content"


def test_download_blob_error(mock_blob_storage_url, mock_blob_service_client, mock_blob_client):
    """Test error handling during blob download."""
    with patch.dict(os.environ, {"AZURE_BLOB_STORAGE_URL": mock_blob_storage_url}), \
            patch('azure.storage.blob.BlobServiceClient', return_value=mock_blob_service_client), \
            patch('streamlit.error') as mock_error:

        # Setup the mock to raise an exception
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = mock_blob_storage_url
        mock_blob_client.download_blob.side_effect = Exception(
            "Blob download failed")

        # Initialize client and call download_blob
        client = AzureBlobClient()
        content = client.download_blob("test-blob.json")

        # Verify error was displayed
        mock_error.assert_called()
        assert "Azure Blob Error during download: Blob download failed" in mock_error.call_args_list[
            0][0][0]
        assert content is None


def test_missing_os_import():
    """Test that the os module is properly imported in blob_storage.py."""
    import inspect
    from services.blob_storage import AzureBlobClient

    # Get the source code of the AzureBlobClient class
    source = inspect.getsource(AzureBlobClient)

    # Check if os is imported in the module
    assert "import os" in source or "from os import" in source, "Missing 'os' import in AzureBlobClient class"
