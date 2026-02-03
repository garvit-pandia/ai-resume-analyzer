"""
Gemini Engine Module (via OpenRouter)
Handles interaction with OpenRouter API for resume analysis using robust fallback logic.
"""

from openai import OpenAI
from typing import Dict, Any, Generator
import json
import re

# List of free models to try in order of preference (OpenRouter identifiers)
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
        default_headers={
            "HTTP-Referer": "https://ai-resume-analyzer.streamlit.app",
            "X-Title": "AI Resume Analyzer"
        }
    )

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Robustly extract JSON object from text using regex.
    """
    # 1. Try straightforward parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 2. Cleanup markdown code blocks
    clean_text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass
        
    # 3. Regex extraction (find outer-most brackets)
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
            
    raise ValueError("Could not extract valid JSON from response")

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
            )
            
            text_response = response.choices[0].message.content
            
            # Robust JSON extraction
            data = extract_json_from_text(text_response)
            
            # Schema validation (basic)
            if not all(k in data for k in ["score", "good", "bad"]):
                raise ValueError("Incomplete JSON schema")
                
            return {"success": True, "data": data, "model_used": model}
            
        except Exception as e:
            last_error = e
            print(f"Model {model} failed: {e}")
            continue
    
    return {
        "success": False, 
        "error": f"All free models busy or failed. Please try again later. (Last error: {str(last_error)})"
    }

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
    
    # Try the models in order until one streams successfully
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
            )
            
            first_chunk_received = False
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    first_chunk_received = True
                    yield chunk.choices[0].delta.content
            
            if first_chunk_received:
                return # Exit after successful stream
            
        except Exception:
            continue
    
    yield "⚠️ Could not generate summary (Models busy)."
