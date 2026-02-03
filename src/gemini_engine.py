"""
Gemini Engine Module
Handles interaction with Google Gemini API for resume analysis.
"""

import google.generativeai as genai
from typing import Optional, Dict, Any


# Resume analysis prompt template
RESUME_ANALYSIS_PROMPT = """You are an expert resume analyst and career coach. Analyze the following resume and provide a comprehensive, actionable assessment.

## Resume Content:
{resume_text}

---

## Your Analysis Task:
Provide a detailed analysis in the following structured format. Be specific, constructive, and actionable.

### 📊 OVERALL SCORE
Rate this resume out of 100, considering:
- Content quality and relevance
- Structure and formatting
- ATS (Applicant Tracking System) compatibility
- Impact and achievements presentation

Provide the score as: **Score: X/100**

### 💪 KEY STRENGTHS (Top 3-5)
List the strongest aspects of this resume with brief explanations.

### 🔧 AREAS FOR IMPROVEMENT (Top 3-5)
Identify specific weaknesses with constructive suggestions for improvement.

### 🤖 ATS COMPATIBILITY
Evaluate how well this resume would perform with Applicant Tracking Systems:
- Keyword optimization
- Format compatibility
- Section headers
- Overall ATS score (High/Medium/Low)

### 📝 SPECIFIC RECOMMENDATIONS
Provide 3-5 actionable recommendations, prioritized by impact:
1. [Highest Priority]
2. [High Priority]
3. [Medium Priority]
(Add more if needed)

### ✨ QUICK WINS
List 2-3 small changes that could make an immediate positive impact.

### 🎯 TAILORING SUGGESTIONS
Tips for tailoring this resume to specific job applications or industries.

Be thorough but concise. Focus on actionable insights that will genuinely help improve this resume.
"""


def initialize_gemini(api_key: str) -> bool:
    """
    Initialize the Gemini API with the provided API key.
    
    Args:
        api_key: Google API key for Gemini
        
    Returns:
        True if initialization successful, False otherwise
    """
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False


def analyze_resume(resume_text: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze a resume using Google Gemini 1.5 Flash.
    
    Args:
        resume_text: The extracted text from the resume PDF
        api_key: Google API key for Gemini
        
    Returns:
        Dictionary containing:
        - success: bool
        - analysis: str (the analysis text if successful)
        - error: str (error message if failed)
    """
    try:
        # Initialize Gemini
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the prompt
        prompt = RESUME_ANALYSIS_PROMPT.format(resume_text=resume_text)
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4096,
            )
        )
        
        # Check if response was blocked
        if not response.parts:
            return {
                "success": False,
                "analysis": None,
                "error": "The analysis was blocked. Please ensure your resume contains appropriate content."
            }
        
        return {
            "success": True,
            "analysis": response.text,
            "error": None
        }
        
    except Exception as e:
        error_message = str(e)
        
        # Provide user-friendly error messages
        if "API_KEY" in error_message.upper() or "invalid" in error_message.lower():
            return {
                "success": False,
                "analysis": None,
                "error": "❌ **Invalid API Key**\n\nPlease check your Google API key and try again."
            }
        elif "quota" in error_message.lower():
            return {
                "success": False,
                "analysis": None,
                "error": "❌ **API Quota Exceeded**\n\nYou've reached the API usage limit. Please try again later."
            }
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            return {
                "success": False,
                "analysis": None,
                "error": "❌ **Connection Error**\n\nUnable to reach the Gemini API. Please check your internet connection."
            }
        else:
            return {
                "success": False,
                "analysis": None,
                "error": f"❌ **Analysis Failed**\n\nAn error occurred: {error_message}"
            }


def validate_api_key(api_key: str) -> bool:
    """
    Validate if the provided API key is functional.
    
    Args:
        api_key: Google API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test request
        response = model.generate_content("Say 'ok'")
        return bool(response.text)
        
    except Exception:
        return False
