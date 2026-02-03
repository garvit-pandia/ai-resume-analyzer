"""
AI Resume Analyzer - Main Streamlit Application
A fire-and-forget tool to analyze resumes using Google Gemini.
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from src.pdf_loader import extract_text_from_pdf, get_pdf_info
from src.gemini_engine import analyze_resume

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Upload area styling */
    .upload-section {
        background: linear-gradient(145deg, #1a1d24 0%, #0e1117 100%);
        border: 2px dashed #6C63FF;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #8B85FF;
        box-shadow: 0 0 30px rgba(108, 99, 255, 0.2);
    }
    
    /* Results card styling */
    .result-card {
        background: linear-gradient(145deg, #1e222a 0%, #14171c 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(108, 99, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Score display */
    .score-container {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        margin: 1rem 0;
    }
    
    .score-value {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Info cards */
    .info-card {
        background: rgba(108, 99, 255, 0.1);
        border-left: 4px solid #6C63FF;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    /* Success message */
    .success-message {
        background: rgba(46, 204, 113, 0.1);
        border-left: 4px solid #2ecc71;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        color: #2ecc71;
    }
    
    /* Error message */
    .error-message {
        background: rgba(231, 76, 60, 0.1);
        border-left: 4px solid #e74c3c;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        color: #e74c3c;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1d24 0%, #0e1117 100%);
    }
    
    /* File uploader */
    .stFileUploader {
        border-radius: 12px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(108, 99, 255, 0.1);
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #6C63FF, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render the main header section."""
    st.markdown("""
    <div class="main-header">
        <h1>📄 AI Resume Analyzer</h1>
        <p>Powered by Google Gemini • Get instant, actionable feedback on your resume</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with instructions."""
    with st.sidebar:
        st.markdown("### 📋 How to Use")
        st.markdown("""
        1. **Upload your resume** (PDF format)
        2. **Click Analyze** and wait
        3. **Review the insights** and improve!
        """)
        
        st.markdown("---")
        
        # Tips
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Use **text-based PDFs** (not scanned images)
        - Resumes created in Word, Google Docs, or PDF editors work best
        - Maximum file size: **10 MB**
        """)
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
        <div class="footer">
            Made with ❤️ using Streamlit & Gemini
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Get API key from environment or secrets
    api_key = os.getenv("GOOGLE_API_KEY")
    # Also check Streamlit secrets
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Upload section
        uploaded_file = render_upload_section()
        
        if uploaded_file:
            # Show file info
            render_file_info(uploaded_file)
            
            # Analyze button
            st.markdown("")  # Spacer
            analyze_button = st.button("🚀 Analyze Resume", use_container_width=True)
            
            if analyze_button:
                # Validate API key
                if not api_key:
                    st.error("❌ **Configuration Error**: `GOOGLE_API_KEY` not found. Please set it in `.env` or Streamlit Secrets.")
                    return
                
                # Process the resume
                with st.spinner("📄 Extracting text from PDF..."):
                    uploaded_file.seek(0)  # Reset file pointer
                    success, message, extracted_text = extract_text_from_pdf(uploaded_file)
                
                if not success:
                    st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
                    return
                
                # Show extraction success
                st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                
                # Show extracted text in expander
                with st.expander("👁️ View Extracted Text", expanded=False):
                    st.text_area("", extracted_text, height=300, disabled=True)
                
                # Analyze with Gemini
                with st.spinner("🤖 Analyzing with AI... This may take a moment..."):
                    result = analyze_resume(extracted_text, api_key)
                
                if result["success"]:
                    render_analysis_results(result["analysis"])
                else:
                    st.markdown(f'<div class="error-message">{result["error"]}</div>', unsafe_allow_html=True)
    
    with col2:
        # Quick info panel
        st.markdown("### ℹ️ What You'll Get")
        
        st.markdown("""
        <div class="info-card">
            <strong>📊 Overall Score</strong><br>
            A comprehensive rating out of 100
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <strong>💪 Key Strengths</strong><br>
            What makes your resume stand out
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <strong>🔧 Improvements</strong><br>
            Specific areas to enhance
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <strong>🤖 ATS Check</strong><br>
            Compatibility with tracking systems
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <strong>✨ Quick Wins</strong><br>
            Easy changes for instant impact
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
