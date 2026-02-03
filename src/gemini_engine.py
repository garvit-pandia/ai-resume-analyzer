"""
Gemini Engine Module (via OpenRouter)
Handles interaction with OpenRouter API for resume analysis.
"""

from openai import OpenAI
from typing import Dict, Any, Generator
import json
import os

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
    
    try:
        client = get_client(api_key)
        
        response = client.chat.completions.create(
            model="google/gemini-pro-1.5",  # Best free model for analysis
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        
        text_response = response.choices[0].message.content
        
        # Clean the response (remove markdown code blocks if present)
        text_response = text_response.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(text_response)
        return {"success": True, "data": data}
        
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse AI response as JSON: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

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
    
    try:
        client = get_client(api_key)
        
        stream = client.chat.completions.create(
            model="google/gemini-pro-1.5",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"Error generating summary: {str(e)}"
