"""
Tests for the text extraction functions that handle various file types.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from io import BytesIO

# Import functions from app.py
from app import extract_text_from_file, extract_text_from_pdf, extract_text_from_docx


@patch('app.extract_text_from_pdf')
def test_extract_text_from_file_pdf(mock_extract_pdf, mock_pdf_file):
    """Test PDF extraction is called for PDF files."""
    # Set up the mock return value
    expected_text = "Mock PDF extracted text"
    mock_extract_pdf.return_value = expected_text

    # Call the function
    result = extract_text_from_file(mock_pdf_file)

    # Verify extract_text_from_pdf was called with the file
    mock_extract_pdf.assert_called_once_with(mock_pdf_file)

    # Verify the result
    assert result == expected_text


@patch('app.extract_text_from_docx')
def test_extract_text_from_file_docx(mock_extract_docx, mock_docx_file):
    """Test DOCX extraction is called for DOCX files."""
    # Set up the mock return value
    expected_text = "Mock DOCX extracted text"
    mock_extract_docx.return_value = expected_text

    # Call the function
    result = extract_text_from_file(mock_docx_file)

    # Verify extract_text_from_docx was called with the file
    mock_extract_docx.assert_called_once_with(mock_docx_file)

    # Verify the result
    assert result == expected_text


def test_extract_text_from_file_txt(mock_txt_file):
    """Test TXT file extraction."""
    # Call the function
    result = extract_text_from_file(mock_txt_file)

    # Verify the result contains the expected content
    assert "This is a mock CV with skills in Python" in result


def test_extract_text_from_file_unsupported():
    """Test handling of unsupported file types."""
    # Create a mock file with an unsupported extension
    class MockUnsupportedFile:
        def __init__(self):
            self.name = "test_file.xyz"

    unsupported_file = MockUnsupportedFile()

    # Call the function
    result = extract_text_from_file(unsupported_file)

    # Verify the result indicates an unsupported file type
    assert "Unsupported file type: .xyz" in result


def test_extract_text_from_file_exception():
    """Test error handling when file extraction fails."""
    # Create a mock file that will cause an exception
    class MockFailingFile:
        def __init__(self):
            self.name = "test_cv.pdf"

        def getvalue(self):
            raise Exception("Mock file reading error")

    failing_file = MockFailingFile()

    # Call the function
    result = extract_text_from_file(failing_file)

    # Verify the result indicates an error
    assert "Error extracting text: Mock file reading error" in result


@patch('PyPDF2.PdfReader')
def test_extract_text_from_pdf_functionality(mock_pdf_reader):
    """Test the PDF extraction functionality."""
    # Set up the mock PDF reader
    mock_page1 = Mock()
    mock_page1.extract_text.return_value = "Page 1 content"

    mock_page2 = Mock()
    mock_page2.extract_text.return_value = "Page 2 content"

    mock_pdf = Mock()
    mock_pdf.pages = [mock_page1, mock_page2]

    mock_pdf_reader.return_value = mock_pdf

    # Create a mock BytesIO object
    mock_file = Mock()
    mock_file.getvalue.return_value = b"Mock PDF content"

    # Call the function
    result = extract_text_from_pdf(mock_file)

    # Verify the result contains content from all pages
    assert "Page 1 content" in result
    assert "Page 2 content" in result


@patch('docx2txt.process')
def test_extract_text_from_docx_functionality(mock_docx_process):
    """Test the DOCX extraction functionality."""
    # Set up the mock return value
    mock_docx_process.return_value = "Extracted DOCX content with skills in Python"

    # Create a mock file
    mock_file = Mock()
    mock_file.getvalue.return_value = b"Mock DOCX content"

    # Call the function
    result = extract_text_from_docx(mock_file)

    # Verify docx2txt.process was called with a BytesIO object
    args = mock_docx_process.call_args[0][0]
    assert isinstance(args, BytesIO)

    # Verify the result
    assert "Extracted DOCX content" in result
    assert "Python" in result
