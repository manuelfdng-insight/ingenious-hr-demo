"""
Integration tests for the CV Analysis Tool application flow.
Tests how components work together in the complete application.
"""

import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
from app import main
from ui.main_page import process_cvs, display_results
from ui.sidebar import render_sidebar
from services import APIClient, extract_text_from_file


@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state for testing."""
    # Setup initial session state
    session_state = {
        'analysis_completed': False,
        'results': [],
        'thread_ids': []
    }

    # Create a context manager to patch st.session_state
    with patch.object(st, 'session_state', session_state):
        yield session_state


def test_main_app_flow_no_files(mock_streamlit, mock_session_state):
    """Test the main app flow with no files uploaded."""
    with patch('ui.sidebar.render_sidebar', return_value=([], False)) as mock_render_sidebar, \
            patch('streamlit.info') as mock_info, \
            patch('streamlit.expander') as mock_expander:

        # Call the main function
        main()

        # Verify the sidebar was rendered
        mock_render_sidebar.assert_called_once()

        # Verify the info message was displayed
        mock_info.assert_called_once()
        assert "Please upload one or more CV files" in mock_info.call_args[0][0]

        # Verify the example expander was shown
        mock_expander.assert_called_once()
        assert "View Example Analysis" in mock_expander.call_args[0][0]


def test_main_app_flow_with_files(mock_streamlit, mock_session_state, sample_pdf_file, mock_api_response):
    """Test the main app flow with files uploaded."""
    # Mock uploaded files
    uploaded_files = [sample_pdf_file]

    with patch('ui.sidebar.render_sidebar', return_value=(uploaded_files, True)) as mock_render_sidebar, \
            patch('ui.main_page.process_cvs', return_value=[{"CV Name": "sample.pdf", "Analysis": "Sample analysis"}]) as mock_process_cvs, \
            patch('ui.main_page.display_results') as mock_display_results:

        # Call the main function
        main()

        # Verify the sidebar was rendered
        mock_render_sidebar.assert_called_once()

        # Verify the CVs were processed
        mock_process_cvs.assert_called_once_with(uploaded_files)

        # Verify the results were displayed
        mock_display_results.assert_called_once()

        # Verify the session state was updated
        assert mock_session_state['analysis_completed'] is True
        assert len(mock_session_state['results']) == 1
        assert mock_session_state['results'][0]["CV Name"] == "sample.pdf"


def test_main_app_flow_already_completed(mock_streamlit, mock_session_state):
    """Test the main app flow when analysis is already completed."""
    # Setup pre-existing results
    mock_session_state['analysis_completed'] = True
    mock_session_state['results'] = [
        {"CV Name": "previous.pdf", "Analysis": "Previous analysis"}]

    with patch('ui.sidebar.render_sidebar', return_value=([MagicMock()], False)) as mock_render_sidebar, \
            patch('ui.main_page.process_cvs') as mock_process_cvs, \
            patch('ui.main_page.display_results') as mock_display_results:

        # Call the main function
        main()

        # Verify the sidebar was rendered
        mock_render_sidebar.assert_called_once()

        # Verify the CVs were not processed again
        mock_process_cvs.assert_not_called()

        # Verify the results were displayed
        mock_display_results.assert_called_once_with(
            mock_session_state['results'])


def test_process_cvs(mock_streamlit, sample_pdf_file, mock_api_response):
    """Test processing of CV files."""
    # Mock uploaded files
    uploaded_files = [sample_pdf_file]

    with patch('services.extract_text_from_file', return_value="Sample CV text") as mock_extract_text, \
            patch('services.APIClient.create_chat', return_value=mock_api_response) as mock_create_chat, \
            patch('streamlit.spinner') as mock_spinner, \
            patch('streamlit.progress') as mock_progress, \
            patch('time.sleep') as mock_sleep:

        # Call the function
        results = process_cvs(uploaded_files)

        # Verify text extraction was called
        mock_extract_text.assert_called_once_with(sample_pdf_file)

        # Verify API call was made
        mock_create_chat.assert_called_once()
        args, kwargs = mock_create_chat.call_args
        assert args[0] == "Sample CV text"
        assert kwargs['identifier'] == "cv_1"

        # Verify progress was updated
        mock_progress.return_value.progress.assert_called_once_with(1.0)

        # Verify results were returned correctly
        assert len(results) == 1
        assert results[0]["CV Name"] == "sample.pdf"
        assert results[0]["Analysis"] == mock_api_response["agent_response"]
        assert results[0]["Thread ID"] == mock_api_response["thread_id"]
        assert results[0]["Message ID"] == mock_api_response["message_id"]


def test_process_cvs_multiple_files(mock_streamlit, sample_pdf_file, sample_docx_file, mock_api_response):
    """Test processing of multiple CV files."""
    # Mock uploaded files
    uploaded_files = [sample_pdf_file, sample_docx_file]

    with patch('services.extract_text_from_file', return_value="Sample text") as mock_extract_text, \
            patch('services.APIClient.create_chat', return_value=mock_api_response) as mock_create_chat, \
            patch('streamlit.spinner') as mock_spinner, \
            patch('streamlit.progress') as mock_progress, \
            patch('time.sleep') as mock_sleep:

        # Call the function
        results = process_cvs(uploaded_files)

        # Verify text extraction was called for each file
        assert mock_extract_text.call_count == 2

        # Verify API call was made for each file
        assert mock_create_chat.call_count == 2

        # Verify progress was updated correctly
        first_progress = mock_progress.return_value.progress.call_args_list[0][0][0]
        second_progress = mock_progress.return_value.progress.call_args_list[1][0][0]
        assert first_progress == 0.5
        assert second_progress == 1.0

        # Verify results were returned correctly
        assert len(results) == 2
        assert results[0]["CV Name"] == "sample.pdf"
        assert results[1]["CV Name"] == "sample.docx"


def test_display_results(mock_streamlit, mock_api_response):
    """Test display of analysis results."""
    # Sample results
    results = [
        {
            "CV Name": "sample1.pdf",
            "Analysis": mock_api_response["agent_response"],
            "Thread ID": "thread-1",
            "Message ID": "message-1"
        },
        {
            "CV Name": "sample2.pdf",
            "Analysis": mock_api_response["agent_response"],
            "Thread ID": "thread-2",
            "Message ID": "message-2"
        }
    ]

    with patch('streamlit.header') as mock_header, \
            patch('streamlit.tabs', return_value=[MagicMock(), MagicMock()]) as mock_tabs, \
            patch('streamlit.subheader') as mock_subheader, \
            patch('streamlit.markdown') as mock_markdown, \
            patch('ui.components.display_feedback_buttons') as mock_display_feedback:

        # Call the function
        display_results(results)

        # Verify the header was displayed
        mock_header.assert_called_once_with("Analysis Results")

        # Verify tabs were created for each CV
        mock_tabs.assert_called_once()
        args, kwargs = mock_tabs.call_args
        assert args[0] == ["sample1.pdf", "sample2.pdf"]

        # Verify feedback buttons were displayed
        assert mock_display_feedback.call_count == 2


def test_render_sidebar(mock_streamlit):
    """Test rendering of the sidebar."""
    with patch('streamlit.sidebar.header') as mock_header, \
            patch('streamlit.sidebar.file_uploader', return_value=[MagicMock()]) as mock_uploader, \
            patch('streamlit.sidebar.markdown') as mock_markdown, \
            patch('streamlit.sidebar.text') as mock_text, \
            patch('streamlit.sidebar.button', return_value=True) as mock_button:

        # Call the function
        uploaded_files, process_button = render_sidebar()

        # Verify the header was displayed
        mock_header.assert_called_once_with("Upload CVs")

        # Verify the file uploader was displayed
        mock_uploader.assert_called()

        # Verify the process button was displayed
        mock_button.assert_called()

        # Verify return values
        assert len(uploaded_files) == 1
        assert process_button is True
