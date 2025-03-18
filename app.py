import streamlit as st
import requests
import json
import pandas as pd
import uuid
import time
import os
from io import BytesIO
import docx2txt
import PyPDF2
import base64
from typing import List, Dict, Any, Tuple, Optional

# Configuration
API_BASE_URL = "http://localhost:3000/api/v1"  # json-server default port

# Set page config
st.set_page_config(
    page_title="CV Analysis Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

class APIClient:
    """Client for interacting with the Ingenious API."""
    
    @staticmethod
    def create_chat(cv_content: str, criteria: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a CV for analysis and get the results."""
        url = f"{API_BASE_URL}/chat"
        
        payload = {
            "thread_id": thread_id or str(uuid.uuid4()),
            "user_id": "streamlit_user",
            "user_prompt": f"CV Content:\n\n{cv_content}\n\nEvaluation Criteria:\n\n{criteria}",
            "conversation_flow": "cv_analysis",
            "topic": "cv evaluation",
            "memory_record": True
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def get_conversation(thread_id: str) -> List[Dict[str, Any]]:
        """Get the conversation history for a thread."""
        url = f"{API_BASE_URL}/conversations/{thread_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return []
    
    @staticmethod
    def submit_feedback(message_id: str, thread_id: str, positive: bool) -> Dict[str, Any]:
        """Submit feedback on an analysis."""
        url = f"{API_BASE_URL}/messages/{message_id}/feedback"
        
        payload = {
            "thread_id": thread_id,
            "message_id": message_id,
            "user_id": "streamlit_user",
            "positive_feedback": positive
        }
        
        try:
            response = requests.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return {"error": str(e)}

def extract_text_from_file(uploaded_file) -> str:
    """Extract text content from various file types."""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    try:
        if file_extension == ".pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_extension == ".docx":
            return extract_text_from_docx(uploaded_file)
        elif file_extension in [".txt", ".md", ".json"]:
            return uploaded_file.getvalue().decode("utf-8")
        else:
            return f"Unsupported file type: {file_extension}"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from PDF file."""
    pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_docx(uploaded_file) -> str:
    """Extract text from DOCX file."""
    return docx2txt.process(BytesIO(uploaded_file.getvalue()))

def create_download_link(content, filename, text):
    """Create a download link for exporting results."""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    st.title("📄 CV Analysis Tool")
    
    with st.sidebar:
        st.header("Upload CVs & Criteria")
        
        # Multi-file uploader for CVs
        uploaded_files = st.file_uploader(
            "Upload CV files (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )
        
        # Evaluation criteria
        st.subheader("Evaluation Criteria")
        criteria = st.text_area(
            "Enter the criteria to evaluate the CVs against",
            """1. Technical Skills: Python, JavaScript, React
2. Experience: Minimum 3 years in software development
3. Education: Computer Science degree or equivalent
4. Communication Skills: Clear writing and presentation skills
5. Projects: Demonstrated experience with relevant projects""",
            height=200
        )
        
        # Process button
        process_button = st.button("Analyze CVs", type="primary")
        
        # Export results button
        if st.session_state.get('analysis_completed'):
            export_results = st.download_button(
                label="Export Results as CSV",
                data=pd.DataFrame(st.session_state.get('results', [])).to_csv(index=False),
                file_name="cv_analysis_results.csv",
                mime="text/csv"
            )

    # Main content area
    if not uploaded_files:
        st.info("Please upload one or more CV files from the sidebar to begin analysis.")
        
        # Show example
        with st.expander("View Example Analysis"):
            st.markdown("""
            ### Example CV Analysis Result
            
            **CV: John Smith (Software Engineer)**
            
            **Analysis Results:**
            - **Technical Skills:** Candidate has strong Python and JavaScript experience but no mention of React. (Score: 2/3)
            - **Experience:** 4 years at XYZ Corp as a software developer. Meets requirement. (Score: 3/3)
            - **Education:** Bachelor's in Computer Science from State University. Meets requirement. (Score: 3/3)
            - **Communication Skills:** Well-written CV with clear descriptions. Evidence of presentations at conferences. (Score: 3/3)
            - **Projects:** Led development of e-commerce platform and API integration projects. (Score: 2/3)
            
            **Overall Match:** 13/15 (87%)
            """)
    
    elif process_button or st.session_state.get('analysis_completed'):
        # Initialize session state
        if 'analysis_completed' not in st.session_state:
            st.session_state['analysis_completed'] = False
            st.session_state['results'] = []
            st.session_state['thread_ids'] = []
            
        # Process CVs
        if not st.session_state['analysis_completed'] and process_button:
            results = []
            thread_ids = []
            
            with st.spinner("Analyzing CVs..."):
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    
                    # Extract text
                    cv_text = extract_text_from_file(uploaded_file)
                    
                    # Send to API
                    response = APIClient.create_chat(cv_text, criteria)
                    
                    # Store result
                    result = {
                        "CV Name": uploaded_file.name,
                        "Analysis": response.get("agent_response", "Analysis failed"),
                        "Thread ID": response.get("thread_id", ""),
                        "Message ID": response.get("message_id", "")
                    }
                    results.append(result)
                    thread_ids.append(response.get("thread_id", ""))
                    
                    # Simulate API delay to not overwhelm the server
                    time.sleep(0.5)
            
            st.session_state['results'] = results
            st.session_state['thread_ids'] = thread_ids
            st.session_state['analysis_completed'] = True
        
        # Display results
        st.header("Analysis Results")
        
        results = st.session_state.get('results', [])
        
        # Create tabs for each CV
        if results:
            tabs = st.tabs([result["CV Name"] for result in results])
            
            for i, tab in enumerate(tabs):
                with tab:
                    result = results[i]
                    
                    # CV name and metadata
                    st.subheader(f"CV: {result['CV Name']}")
                    
                    # Analysis result
                    st.markdown("### Analysis")
                    st.markdown(result["Analysis"])
                    
                    # Feedback buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Helpful", key=f"helpful_{i}"):
                            feedback = APIClient.submit_feedback(
                                result["Message ID"],
                                result["Thread ID"],
                                True
                            )
                            st.success("Thank you for your feedback!")
                    
                    with col2:
                        if st.button("👎 Not Helpful", key=f"not_helpful_{i}"):
                            feedback = APIClient.submit_feedback(
                                result["Message ID"],
                                result["Thread ID"],
                                False
                            )
                            st.success("Thank you for your feedback. We'll improve our analysis.")
                    
                    # Match score visualization
                    try:
                        # Try to extract a score if present in the analysis text
                        import re
                        score_match = re.search(r'(\d+)%', result["Analysis"])
                        if score_match:
                            score = int(score_match.group(1))
                            st.metric("Match Score", f"{score}%")
                            
                            # Visual representation
                            st.progress(score/100)
                    except:
                        pass

        # Show summary as a table
        st.header("Summary")
        
        # Create a DataFrame for easy viewing
        summary_data = []
        
        for result in results:
            # Try to extract a match percentage from the analysis text
            import re
            match_text = "N/A"
            match_percent = 0
            
            score_match = re.search(r'(\d+)%', result["Analysis"])
            if score_match:
                match_percent = int(score_match.group(1))
                match_text = f"{match_percent}%"
            
            summary_data.append({
                "CV Name": result["CV Name"],
                "Match Score": match_text,
                "Thread ID": result["Thread ID"]
            })
        
        # Display the summary table
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

if __name__ == "__main__":
    main()