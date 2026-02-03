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
from src.gemini_engine import analyze_resume_structure, stream_summary

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
        margin-bottom: 1rem;
    }
    
    .score-value {
        font-size: 5rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        line-height: 1;
    }
    
    .score-label {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Pro/Con cards */
    .pro-card {
        background: rgba(46, 204, 113, 0.1);
        border: 1px solid rgba(46, 204, 113, 0.3);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .con-card {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid rgba(231, 76, 60, 0.3);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    /* Streaming text container */
    .stream-container {
        font-family: 'Courier New', monospace;
        background: #1e222a;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #6C63FF;
        line-height: 1.6;
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
    
    /* Text Area styling */
    .stTextArea textarea {
        background-color: #1A1D24;
        border: 1px solid #2B303B;
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)


def render_header():
    """Render the main header section."""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Results & Job Fit Analyzer</h1>
        <p>Get instant feedback on your resume's fit for a specific role</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with instructions."""
    with st.sidebar:
        st.markdown("### 📋 How to Use")
        st.markdown("""
        1. **Paste Job Description** (Mandatory)
        2. **Upload Resume** (PDF)
        3. **Click Analyze**
        """)
        
        st.markdown("---")
        
        # Tips
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Use **Text-Based PDFs**
        - Ensure JD is detailed
        - Max file size: **10MB**
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
    render_header()
    render_sidebar()
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Check for API key early
    if not api_key:
        st.error("❌ **Configuration Error**: `GOOGLE_API_KEY` not found. Please set it in `.env` or Streamlit Secrets.")
        return

    # Layout: Dual Column for Inputs
    col_input_1, col_input_2 = st.columns([1, 1], gap="medium")
    
    with col_input_1:
         st.markdown("### 1. The Job")
         jd_text = st.text_area("Paste Job Description (Required)", height=300, placeholder="Paste the full job description here...")
         
    with col_input_2:
        st.markdown("### 2. Your Resume")
        uploaded_file = st.file_uploader("Upload PDF Resume (Required)", type=["pdf"])
        if uploaded_file:
            file_info = get_pdf_info(uploaded_file)
            st.caption(f"📄 {file_info['filename']} ({file_info['size_kb']} KB) - {file_info['pages']} pages")

    # Analyze Button - Centered
    st.markdown("---")
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
    with col_btn_2:
        analyze_button = st.button("🚀 Analyze Match", use_container_width=True)

    # Logic
    if analyze_button:
        # Validation
        if not jd_text or not jd_text.strip():
            st.error("⚠️ **Job Description Missing**: Please paste the job description to continue.")
            return
        
        if not uploaded_file:
            st.error("⚠️ **Resume Missing**: Please upload your PDF resume.")
            return
            
        # Processing
        with st.spinner("🔍 analyzing..."):
            # 1. Extract Text
            uploaded_file.seek(0)
            success, message, resume_text = extract_text_from_pdf(uploaded_file)
            
            if not success:
                st.error(message)
                return
                
            # 2. Analyze Structure (JSON)
            structure_result = analyze_resume_structure(resume_text, jd_text, api_key)
            
            if not structure_result.get("success"):
                st.error(f"❌ Analysis Failed: {structure_result.get('error')}")
                return
            
            data = structure_result["data"]
            
            # --- DISPLAY RESULTS ---
            
            # A. Score Section
            st.markdown("### 🎯 Match Score")
            col_score, col_summary = st.columns([1, 2])
            
            with col_score:
                st.markdown(f"""
                <div class="score-container">
                    <div class="score-value">{data['score']}</div>
                    <div class="score-label">/ 100</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_summary:
                st.markdown("#### 🗣️ Quick Summary")
                # B. Stream Summary
                stream_generator = stream_summary(resume_text, jd_text, api_key)
                st.write_stream(stream_generator)

            # C. Pros & Cons Split
            st.markdown("---")
            col_good, col_bad = st.columns(2, gap="large")
            
            with col_good:
                st.subheader("✅ Key Strengths")
                for point in data['good']:
                    st.markdown(f"""
                    <div class="pro-card">
                        ✔️ {point}
                    </div>
                    """, unsafe_allow_html=True)
                    
            with col_bad:
                st.subheader("⚠️ Weaknesses / Nitpicks")
                for point in data['bad']:
                    st.markdown(f"""
                    <div class="con-card">
                        🔻 {point}
                    </div>
                    """, unsafe_allow_html=True)
                    
            # D. Extracted Text (Hidden)
            with st.expander("📄 View Extracted Resume Text"):
                st.text(resume_text)


if __name__ == "__main__":
    main()
