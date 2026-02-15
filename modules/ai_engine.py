import os
import google.generativeai as genai
import replicate
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class AIGhostwriter:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None
            
        self.business_context = self.load_business_context()

    def load_business_context(self):
        """Loads business profile from text file."""
        try:
            with open("assets/business_profile.txt", "r") as f:
                return f.read()
        except Exception:
            return "You are a helpful AI assistant for a business."

    def generate_content(self, prompt, use_context=True):
        """Standard wrapper for generating text content."""
        if not self.model:
            return "Error: Gemini API Key missing."
            
        final_prompt = prompt
        if use_context and self.business_context:
            final_prompt = f"SYSTEM_CONTEXT:\n{self.business_context}\n\nUSER_REQUEST:\n{prompt}"
            
        try:
            response = self.model.generate_content(final_prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI Error: {str(e)}"

    def generate_icebreaker(self, name, bio, platform="Generic"):
        if not self.model:
            return "Error: Gemini API Key missing."
        
        prompt = f"""
        Act as a high-end luxury consultant. Write a 1-sentence, high-status compliment/opening for a cold outreach to:
        Name: {name}
        Bio/Context: {bio}
        Platform: {platform}
        
        Tone: Professional, sophisticated, intriguing. Not salesy.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI Error: {str(e)}"

    def score_lead(self, bio):
        """Simple heuristic scoring."""
        if not bio or not isinstance(bio, str):
            return "Standard"
        
        keywords_whale = ['award', 'luxury', 'high-end', 'commercial', 'director', 'founder', 'ceo']
        bio_lower = bio.lower()
        
        for k in keywords_whale:
            if k in bio_lower:
                return "WHALE"
        return "Standard"
    
    def intelligent_score(self, name, bio, source="Unknown"):
        """
        AI-powered lead scoring (0-100).
        Analyzes bio/headline to determine lead quality and business value.
        """
        if not self.model:
            # Fallback to heuristic if no API
            return self._heuristic_score(bio)
        
        prompt = f"""Analyze this business lead and assign a quality score from 0-100.

Lead Information:
- Name: {name}
- Bio/Headline: {bio}
- Source: {source}

Scoring Criteria:
- 90-100: C-Suite, Property Developers, High Net Worth Individuals, Business Owners
- 70-89: Senior Managers, Architects, Interior Designers, Real Estate Agents
- 50-69: Mid-level professionals, Small business owners
- 30-49: Junior professionals, Freelancers
- 0-29: Students, Unrelated fields, Unclear profiles

Return ONLY a number between 0-100. No explanation."""

        try:
            response = self.model.generate_content(prompt)
            score_text = response.text.strip()
            # Extract number from response
            import re
            match = re.search(r'\d+', score_text)
            if match:
                score = int(match.group())
                return min(max(score, 0), 100)  # Clamp to 0-100
            return 50  # Default if parsing fails
        except Exception as e:
            print(f"AI Scoring Error: {e}")
            return self._heuristic_score(bio)
    
    def _heuristic_score(self, bio):
        """Fallback scoring without AI."""
        if not bio or not isinstance(bio, str):
            return 30
        
        bio_lower = bio.lower()
        score = 40  # Base score
        
        # High value indicators
        high_value = ['ceo', 'founder', 'director', 'developer', 'owner', 'president', 'partner']
        mid_value = ['manager', 'architect', 'designer', 'agent', 'consultant']
        luxury = ['luxury', 'premium', 'high-end', 'exclusive', 'award']
        
        for keyword in high_value:
            if keyword in bio_lower:
                score += 20
                
        for keyword in mid_value:
            if keyword in bio_lower:
                score += 10
                
        for keyword in luxury:
            if keyword in bio_lower:
                score += 15
        
        return min(score, 100)

class VisualStudio:
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        
    def generate_concept(self, prompt, save_path="assets/concepts/"):
        if not self.api_token:
            st.error("Replicate API Token missing in .env")
            return None
            
        os.makedirs(save_path, exist_ok=True)
        
        # Enhanced prompt for Luxury Interior style
        full_prompt = f"Luxury interior design photography, editorial shot, 8k, photorealistic, {prompt}"
        
        try:
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": full_prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "output_quality": 90
                }
            )
            
            # Replicate returns a URL or stream. For FLUX it's usually a URL.
            # We need to download it.
            # Output is an iterator or list of URLs depending on model.
            
            # Simple handling assuming URL string or list[str]
            image_url = str(output)
            
            # Generate filename
            import time
            import requests
            
            filename = f"concept_{int(time.time())}.jpg"
            filepath = os.path.join(save_path, filename)
            
            img_data = requests.get(image_url).content
            with open(filepath, 'wb') as handler:
                handler.write(img_data)
                
            return filepath, image_url
            
        except Exception as e:
            st.error(f"Image Gen Error: {e}")
            return None, None
