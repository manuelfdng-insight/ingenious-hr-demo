"""
Pytest fixtures for testing the CV Analysis Tool.
"""

import pytest
import io
import json
import streamlit as st
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions for testing."""
    with patch('streamlit.sidebar'), \
            patch('streamlit.title'), \
            patch('streamlit.header'), \
            patch('streamlit.subheader'), \
            patch('streamlit.markdown'), \
            patch('streamlit.text'), \
            patch('streamlit.info'), \
            patch('streamlit.success'), \
            patch('streamlit.error'), \
            patch('streamlit.warning'), \
            patch('streamlit.progress'), \
            patch('streamlit.spinner'), \
            patch('streamlit.button'), \
            patch('streamlit.download_button'), \
            patch('streamlit.file_uploader'), \
            patch('streamlit.columns'), \
            patch('streamlit.expander'), \
            patch('streamlit.tabs'), \
            patch('streamlit.session_state', {}):
        yield


@pytest.fixture
def sample_pdf_file():
    """Create a mock PDF file for testing."""
    return MagicMock(
        name="sample.pdf",
        getvalue=MagicMock(
            return_value=b"%PDF-1.5\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Count 1/Kids[3 0 R]>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 595 842]/Resources<<>>/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 21>>stream\nBT /F1 12 Tf (Test PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000015 00000 n \n0000000060 00000 n \n0000000111 00000 n \n0000000190 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n259\n%%EOF")
    )


@pytest.fixture
def sample_docx_file():
    """Create a mock DOCX file for testing."""
    return MagicMock(
        name="sample.docx",
        getvalue=MagicMock(return_value=b"Mock DOCX content")
    )


@pytest.fixture
def sample_txt_file():
    """Create a mock TXT file for testing."""
    return MagicMock(
        name="sample.txt",
        getvalue=MagicMock(
            return_value=b"This is a sample text file for testing.")
    )


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "thread_id": "sample-thread-id",
        "message_id": "sample-message-id",
        "agent_response": json.dumps([
            {
                "__dict__": {
                    "chat_name": "summary",
                    "chat_response": {
                        "chat_message": {
                            "__dict__": {
                                "content": "This is a sample analysis result."
                            }
                        }
                    }
                }
            }
        ])
    }


@pytest.fixture
def mock_feedback_response():
    """Mock feedback response for testing."""
    return {
        "message_id": "sample-message-id",
        "thread_id": "sample-thread-id",
        "status": "success"
    }


@pytest.fixture
def mock_blob_storage_url():
    """Mock Azure Blob Storage URL for testing."""
    return "https://storageaccount.blob.core.windows.net/container/blob?sv=2020-08-04&st=2021-09-01T00%3A00%3A00Z&se=2022-09-01T00%3A00%3A00Z&sr=c&sp=racwl&sig=signature"
