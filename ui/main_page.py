"""
Main page UI logic for the CV Analysis Tool.
"""

import streamlit as st
import json
import time
import pandas as pd
from typing import List, Dict, Any

from services import APIClient, extract_text_from_file
from ui.components import display_feedback_buttons


def process_cvs(uploaded_files) -> List[Dict[str, Any]]:
    """Process uploaded CV files and send them to the API for analysis."""
    results = []

    with st.spinner("Analyzing CVs..."):
        progress_bar = st.progress(0)

        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)

            # Extract text
            cv_text = extract_text_from_file(uploaded_file)

            # Send to API
            identifier = f"cv_{i+1}"
            response = APIClient.create_chat(
                cv_text, identifier=identifier)

            # Log the response for debugging if needed
            if "error" in response:
                st.error(
                    f"Error analyzing {uploaded_file.name}: {response['error']}")
                continue

            # Store result
            result = {
                "CV Name": uploaded_file.name,
                "Analysis": response.get("agent_response", "Analysis failed"),
                "Thread ID": response.get("thread_id", ""),
                "Message ID": response.get("message_id", "")
            }
            results.append(result)

            # Simulate API delay to not overwhelm the server
            time.sleep(0.5)

    return results


def display_results(results: List[Dict[str, Any]]):
    """Display the analysis results for the uploaded CVs."""
    if not results:
        return

    st.header("Analysis Results")

    # Create tabs for each CV
    tabs = st.tabs([result["CV Name"] for result in results])

    for i, tab in enumerate(tabs):
        with tab:
            result = results[i]

            # CV name and metadata
            st.subheader(f"CV: {result['CV Name']}")

            # Analysis result
            st.markdown("### Analysis")

            # Parse and display the analysis
            try:
                analysis_data = json.loads(result["Analysis"])
                for header in analysis_data:
                    chat_dict = header.get('__dict__', {})
                    chat_name = chat_dict.get('chat_name', '')

                    if chat_name in ["summary", "applicant_lookup_agent"]:
                        chat_response = chat_dict.get('chat_response', {})
                        chat_message = chat_response.get('chat_message', {})
                        content = chat_message.get(
                            '__dict__', {}).get('content', '')

                        if content:
                            st.markdown(content)
            except Exception as e:
                st.error(f"Error displaying analysis: {str(e)}")
                st.markdown(result["Analysis"])

            # Display feedback buttons
            display_feedback_buttons(result, i)
