"""
Gemini Engine Module
Handles interaction with Google Gemini API for resume analysis.
"""

import google.generativeai as genai
from typing import Dict, Any, Generator
import json
import os

def initialize_gemini(api_key: str):
    """Initialize Gemini with the API Key."""
    genai.configure(api_key=api_key)

import time

def get_gemini_model():
    """Get the specific stable model."""
    # gemini-2.5-flash-lite - lightest and fastest
    return genai.GenerativeModel('gemini-2.5-flash-lite')

def retry_on_failure(func):
    """Decorator to retry API calls on 429 Rate Limit errors."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check for rate limit error (429)
                if "429" in str(e) or "Resource exhausted" in str(e):
                    if attempt < max_retries - 1:
                        # Wait gracefully
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                # If not 429 or retries exhausted, re-raise
                raise e
    return wrapper

def list_available_models(api_key: str):
    """List all available models for the provided API key."""
    try:
        initialize_gemini(api_key)
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except Exception as e:
        return [f"Error listing models: {str(e)}"]

def analyze_resume_structure(resume_text: str, jd_text: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze resume vs JD and return structured JSON data using Google Gemini.
    """
    try:
        initialize_gemini(api_key)
        model = get_gemini_model()
        
        prompt = f"""Act as a strict HR manager. Analyze the following resume against the provided job description.

RETURN ONLY A VALID JSON OBJECT with this exact structure:
{{
  "score": <integer 0-100>,
  "good": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "bad": ["<weakness 1>", "<weakness 2>", "<weakness 3>"]
}}

Critique strictly. The "bad" array must contain 3 genuine areas for improvement or nitpicks.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}
"""
        
        # Use retry wrapper directly or implement retry logic in place
        
        # 1. Analyze Structure
        @retry_on_failure
        def generate_json_response():
            return model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
        response = generate_json_response()
        
        if not response.parts:
             return {"success": False, "error": "Content blocked by safety filters."}

        # Parse JSON
        text_response = response.text.strip()
         # fallback cleanup if mimetype fails
        text_response = text_response.replace("```json", "").replace("```", "").strip()
        data = json.loads(text_response)
        
        return {"success": True, "data": data, "model_used": "gemini-2.5-flash-lite"}
        
    except Exception as e:
        return {"success": False, "error": f"AI Parsing Error: {str(e)}"}


def stream_summary(resume_text: str, jd_text: str, api_key: str) -> Generator[str, None, None]:
    """
    Stream a 'Vibes' summary of the candidate using Google Gemini.
    """
    try:
        initialize_gemini(api_key)
        model = get_gemini_model()
        
        prompt = f"""Read the resume and job description below.
Write a direct, engaging "Vibes" summary of this candidate for the role (approx 100 words).
Address the user directly as "You".
Be informal but professional. Capture the essence of their fit.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}
"""
        # Streaming call with manual retry handling (since stream object can't simply be retried in a decorator midway)
        # We start the stream with retry
        
        @retry_on_failure
        def start_stream():
            return model.generate_content(prompt, stream=True)
            
        response_stream = start_stream()
        
        for chunk in response_stream:
             if chunk.text:
                yield chunk.text
                
    except Exception as e:
        yield f"Error generating summary: {str(e)}"

