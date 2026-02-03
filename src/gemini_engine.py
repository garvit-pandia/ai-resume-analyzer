"""
Gemini Engine Module (via OpenRouter)
Handles interaction with OpenRouter API for resume analysis.
"""

from openai import OpenAI
from typing import Dict, Any, Generator
import json
import os

# List of free models to try in order of preference
FREE_MODELS = [
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "google/gemini-2.0-pro-exp-02-05:free",
    "google/gemini-2.0-flash-thinking-exp:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free",
]

def get_client(api_key: str) -> OpenAI:
    """Get OpenRouter client."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def analyze_resume_structure(resume_text: str, jd_text: str, api_key: str) -> Dict[str, Any]:
    """
    Analyze resume vs JD and return structured JSON data.
    """
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
    
    client = get_client(api_key)
    last_error = None

    for model in FREE_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096,
                headers={
                    "HTTP-Referer": "https://ai-resume-analyzer.streamlit.app",
                    "X-Title": "AI Resume Analyzer"
                },
            )
            
            text_response = response.choices[0].message.content
            
            # Clean the response
            text_response = text_response.replace("```json", "").replace("```", "").strip()
            
            # Use regex or simple search to find the start/end of JSON if extra text exists
            if "{" in text_response:
                text_response = text_response[text_response.find("{"):text_response.rfind("}")+1]

            data = json.loads(text_response)
            return {"success": True, "data": data}
            
        except Exception as e:
            last_error = e
            print(f"Model {model} failed: {e}")
            continue
    
    return {"success": False, "error": f"All free models failed. Last error: {str(last_error)}"}

def stream_summary(resume_text: str, jd_text: str, api_key: str) -> Generator[str, None, None]:
    """
    Stream a 'Vibes' summary of the candidate.
    """
    prompt = f"""Read the resume and job description below.
Write a direct, engaging "Vibes" summary of this candidate for the role (approx 100 words).
Address the user directly as "You".
Be informal but professional. Capture the essence of their fit.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}
"""
    
    client = get_client(api_key)
    
    # Try the first working model for streaming
    for model in FREE_MODELS:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=True,
                headers={
                    "HTTP-Referer": "https://ai-resume-analyzer.streamlit.app",
                    "X-Title": "AI Resume Analyzer"
                },
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return # Exit after successful stream
            
        except Exception:
            continue
    
    yield "Error: Could not generate summary with available free models."
