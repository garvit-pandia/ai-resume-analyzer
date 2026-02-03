"""
Gemini Engine Module
Handles interaction with Google Gemini API for resume analysis.
"""

import google.generativeai as genai
from typing import Optional, Dict, Any, Generator
import json
import time

def initialize_gemini(api_key: str) -> bool:
    """Initialize the Gemini API."""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False

def _get_gemini_response(prompt: str, api_key: str, stream: bool = False, json_mode: bool = False):
    """
    Internal helper to call Gemini with fallback models.
    """
    genai.configure(api_key=api_key)
    
    models_to_try = [
        'gemini-1.5-flash',           # Fast and efficient (most reliable)
        'gemini-1.5-pro',             # More capable, slower
        'gemini-2.0-flash-exp',       # Experimental 2.0 (may not be available)
    ]
    
    last_error = None
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=4096,
    )
    
    if json_mode:
        generation_config.response_mime_type = "application/json"

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            if stream:
                return model.generate_content(prompt, stream=True, generation_config=generation_config), None
            else:
                response = model.generate_content(prompt, generation_config=generation_config)
                if not response.parts:
                    raise ValueError("Content blocked")
                return response, None
        except Exception as e:
            last_error = e
            continue
            
    return None, str(last_error) if last_error else "Unknown error"

def analyze_resume_structure(resume_text: str, jd_text: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze resume vs JD and return structured JSON data.
    """
    prompt = f"""
    Act as a strict HR manager. Analyze the following resume against the provided job description.
    
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
    
    response, error = _get_gemini_response(prompt, api_key, json_mode=True)
    
    if error:
        return {"success": False, "error": error}
    
    try:
        # Clean the response text just in case (remove markdown code blocks if present)
        text_response = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text_response)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": f"Failed to parse AI response: {str(e)}"}

def stream_summary(resume_text: str, jd_text: str, api_key: str) -> Generator[str, None, None]:
    """
    Stream a 'Vibes' summary of the candidate.
    """
    prompt = f"""
    Read the resume and job description below.
    Write a direct, engaging "Vibes" summary of this candidate for the role (approx 100 words).
    Address the user directly as "You".
    Be informal but professional. Capture the essence of their fit.
    
    JOB DESCRIPTION:
    {jd_text}
    
    RESUME:
    {resume_text}
    """
    
    response_stream, error = _get_gemini_response(prompt, api_key, stream=True)
    
    if error:
        yield f"Error generating summary: {error}"
        return

    for chunk in response_stream:
        if chunk.text:
            yield chunk.text

