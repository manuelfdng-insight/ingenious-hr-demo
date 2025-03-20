"""
Tests for text extraction functions that handle various document types.
"""

import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from services.text_extraction import (
    extract_text_from_file,
    extract_text_from_pdf,
    extract_text_from_docx
)


def test_extract_text_from_pdf(sample_pdf_file):
    """Test extracting text from a PDF file."""
    with patch('pypdf.PdfReader') as mock_pdf_reader:
        # Setup mock
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_pdf_reader.return_value.pages = [mock_page]

        # Call the function
        result = extract_text_from_pdf(sample_pdf_file)

        # Verify the text was extracted correctly
        mock_pdf_reader.assert_called_once()
        mock_page.extract_text.assert_called_once()
        assert result == "Test PDF content"


def test_extract_text_from_docx(sample_docx_file):
    """Test extracting text from a DOCX file."""
    with patch('docx2txt.process', return_value="Test DOCX content") as mock_process:
        # Call the function
        result = extract_text_from_docx(sample_docx_file)

        # Verify the text was extracted correctly
        mock_process.assert_called_once()
        assert result == "Test DOCX content"


def test_extract_text_from_file_pdf(sample_pdf_file):
    """Test extract_text_from_file with a PDF."""
    with patch('services.text_extraction.extract_text_from_pdf',
               return_value="Extracted PDF content") as mock_extract_pdf:

        # Call the function
        result = extract_text_from_file(sample_pdf_file)

        # Verify the correct extractor was called
        mock_extract_pdf.assert_called_once_with(sample_pdf_file)
        assert result == "Extracted PDF content"


def test_extract_text_from_file_docx(sample_docx_file):
    """Test extract_text_from_file with a DOCX."""
    with patch('services.text_extraction.extract_text_from_docx',
               return_value="Extracted DOCX content") as mock_extract_docx:

        # Call the function
        result = extract_text_from_file(sample_docx_file)

        # Verify the correct extractor was called
        mock_extract_docx.assert_called_once_with(sample_docx_file)
        assert result == "Extracted DOCX content"


def test_extract_text_from_file_txt(sample_txt_file):
    """Test extract_text_from_file with a TXT file."""
    # Call the function
    result = extract_text_from_file(sample_txt_file)

    # Verify the text was extracted correctly
    assert result == "This is a sample text file for testing."


def test_extract_text_from_file_unsupported():
    """Test extract_text_from_file with an unsupported file type."""
    # Create a mock file with an unsupported extension
    unsupported_file = MagicMock(
        name="sample.xyz",
        getvalue=MagicMock(return_value=b"Test content")
    )

    # Call the function
    result = extract_text_from_file(unsupported_file)

    # Verify the error message
    assert "Unsupported file type: .xyz" in result


def test_extract_text_from_file_error():
    """Test error handling in extract_text_from_file."""
    # Create a mock file that will cause an error
    error_file = MagicMock(
        name="sample.pdf",
        getvalue=MagicMock(side_effect=Exception("File read error"))
    )

    # Call the function
    result = extract_text_from_file(error_file)

    # Verify the error message
    assert "Error extracting text: File read error" in result


def test_extract_text_from_file_multi_page_pdf():
    """Test extracting text from a multi-page PDF file."""
    # Create a mock PDF file
    mock_pdf_file = MagicMock(
        name="multi_page.pdf",
        getvalue=MagicMock(return_value=b"%PDF-1.5\nMulti-page PDF content")
    )

    with patch('pypdf.PdfReader') as mock_pdf_reader:
        # Setup mock for multiple pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_pdf_reader.return_value.pages = [mock_page1, mock_page2]

        # Call the function
        result = extract_text_from_pdf(mock_pdf_file)

        # Verify text from both pages was extracted
        assert result == "Page 1 contentPage 2 content"
        assert mock_page1.extract_text.call_count == 1
        assert mock_page2.extract_text.call_count == 1
