"""
Google Gemini API Integration
Provides "AI Brain" capabilities for generating scripts, hooks, and content strategy.
"""
import os
from google import genai

def is_configured() -> bool:
    """Check if the Gemini API key is available in the environment."""
    return bool(os.getenv("GEMINI_API_KEY"))

def generate_script(topic: str, platform: str = "Instagram Reels", duration: str = "Short (15-30s)") -> dict:
    """Generate a high-converting short-form script using the new google-genai SDK."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "success": False, 
            "error": "Gemini API key not found. Please add GEMINI_API_KEY to your .env file."
        }
        
    try:
        # Initialize client with the new SDK
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an elite Social Media Marketer specializing in {platform} for lead generation.
        Write a highly converting, {duration} script about: "{topic}"
        
        CRITICAL RULES:
        1. STRATEGY: Use the "Hook + Value + Call to Action" framework.
        2. THE HOOK: The first 3 seconds must be a powerful, disruptive hook that grabs attention immediately.
        3. FORMAT: Output the script clearly formatted with [VISUAL] and [AUDIO] cues.
        4. TONE: Professional, authoritative, yet approachable and engaging. 
        5. DO NOT use emojis.
        
        Please provide the script exactly as the user should record it.
        """
        
        # Use simple text generation syntax from new SDK
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        return {
            "success": True,
            "script": response.text
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Gemini API Error: {str(e)}"
        }
