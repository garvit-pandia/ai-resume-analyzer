"""
Gemini Engine Module
Handles interaction with Google Gemini API for resume analysis.
Implements a model fallback chain for resilience.
"""

import google.generativeai as genai
from typing import Dict, Any, Generator
import json
import time

# Priority list of models to try (in order)
MODEL_PRIORITY = [
    'gemini-2.5-flash-lite',   # 1. Lightest, fastest, best free tier
    'gemini-2.5-flash',        # 2. Balanced
    'gemini-3-flash-preview',  # 3. Newest flash
    'gemini-flash-latest',     # 4. Alias for latest
    'gemini-2.5-pro',          # 5. Pro fallback
]


def initialize_gemini(api_key: str):
    """Initialize Gemini with the API Key."""
    genai.configure(api_key=api_key)


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
    Tries models in priority order until one succeeds.
    """
    initialize_gemini(api_key)
    
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
    
    last_error = None
    
    for model_name in MODEL_PRIORITY:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            
            if not response.parts:
                raise ValueError("Content blocked by safety filters.")
            
            # Parse JSON
            text_response = response.text.strip()
            text_response = text_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(text_response)
            
            return {"success": True, "data": data, "model_used": model_name}
            
        except Exception as e:
            last_error = str(e)
            # If rate limited, wait briefly before trying next model
            if "429" in str(e) or "Resource exhausted" in str(e):
                time.sleep(1)
            continue
    
    return {"success": False, "error": f"All models failed. Last error: {last_error}"}


def stream_summary(resume_text: str, jd_text: str, api_key: str) -> Generator[str, None, None]:
    """
    Stream a 'Vibes' summary of the candidate using Google Gemini.
    Tries models in priority order until one succeeds.
    """
    initialize_gemini(api_key)
    
    prompt = f"""Read the resume and job description below.
Write a direct, engaging "Vibes" summary of this candidate for the role (approx 100 words).
Address the user directly as "You".
Be informal but professional. Capture the essence of their fit.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}
"""
    
    for model_name in MODEL_PRIORITY:
        try:
            model = genai.GenerativeModel(model_name)
            response_stream = model.generate_content(prompt, stream=True)
            
            first_chunk = True
            for chunk in response_stream:
                if chunk.text:
                    first_chunk = False
                    yield chunk.text
            
            # If we got any content, we succeeded
            if not first_chunk:
                return
                
        except Exception as e:
            # If rate limited, wait briefly before trying next model
            if "429" in str(e) or "Resource exhausted" in str(e):
                time.sleep(1)
            continue
    
    yield "⚠️ Could not generate summary. All models are currently busy."
