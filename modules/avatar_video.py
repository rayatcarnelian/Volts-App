"""
AVATAR VIDEO GENERATOR
AI Spokesperson videos using HeyGen or D-ID APIs.
Choose an avatar face, enter script, generate professional marketing video.
"""

import os
import time
import json
import requests
from typing import Optional, Dict, List
from dataclasses import dataclass

# Load environment
from dotenv import load_dotenv
load_dotenv()


# ============================================================================
# AVATAR CATALOG
# ============================================================================

# Pre-defined avatars (HeyGen-style IDs - will work with their API)
AVATAR_CATALOG = {
    "professional_male_1": {
        "name": "Marcus",
        "description": "Professional male, 30s, business attire",
        "preview": "👨‍💼",
        "heygen_id": "josh_lite3_20230714",
        "did_id": "amy-Aq6OmGZnMt"
    },
    "professional_female_1": {
        "name": "Sarah",
        "description": "Professional female, 30s, business attire",
        "preview": "👩‍💼",
        "heygen_id": "anna_costume1_20221108",
        "did_id": "amy-Aq6OmGZnMt"
    },
    "friendly_male_1": {
        "name": "Alex",
        "description": "Friendly male, 25-30, casual smart",
        "preview": "🧑",
        "heygen_id": "tyler-ingreen",
        "did_id": "amy-Aq6OmGZnMt"
    },
    "friendly_female_1": {
        "name": "Emma",
        "description": "Friendly female, 25-30, modern style",
        "preview": "👩",
        "heygen_id": "monica_lite2_20221201",
        "did_id": "amy-Aq6OmGZnMt"
    },
    "mature_male_1": {
        "name": "David",
        "description": "Mature male, 45+, executive style",
        "preview": "👨‍🦳",
        "heygen_id": "wayne_costume2_20230728",
        "did_id": "amy-Aq6OmGZnMt"
    },
    "mature_female_1": {
        "name": "Catherine",
        "description": "Mature female, 45+, elegant professional",
        "preview": "👩‍🦳",
        "heygen_id": "angela_costume2_20230815",
        "did_id": "amy-Aq6OmGZnMt"
    }
}

# Voice options
VOICE_OPTIONS = {
    "en_male_professional": {"name": "English (Male, Professional)", "heygen_voice": "en-US-GuyNeural"},
    "en_female_professional": {"name": "English (Female, Professional)", "heygen_voice": "en-US-JennyNeural"},
    "en_male_friendly": {"name": "English (Male, Friendly)", "heygen_voice": "en-US-DavisNeural"},
    "en_female_friendly": {"name": "English (Female, Friendly)", "heygen_voice": "en-US-AriaNeural"},
    "ms_male": {"name": "Malay (Male)", "heygen_voice": "ms-MY-OsmanNeural"},
    "ms_female": {"name": "Malay (Female)", "heygen_voice": "ms-MY-YasminNeural"},
    "zh_male": {"name": "Chinese (Male)", "heygen_voice": "zh-CN-YunxiNeural"},
    "zh_female": {"name": "Chinese (Female)", "heygen_voice": "zh-CN-XiaoxiaoNeural"},
}


# ============================================================================
# HEYGEN API CLIENT
# ============================================================================

class HeyGenClient:
    """
    HeyGen API client for generating avatar videos.
    Free tier: 10 credits (1 credit = 1 minute of video)
    """
    
    BASE_URL = "https://api.heygen.com/v2"
    
    def __init__(self):
        self.api_key = os.getenv("HEYGEN_API_KEY")
        self.headers = {
            "X-Api-Key": self.api_key or "",
            "Content-Type": "application/json"
        }
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def create_video(
        self,
        script: str,
        avatar_id: str = "josh_lite3_20230714",
        voice_id: str = "en-US-GuyNeural",
        background_color: str = "#1a1a2e",
        video_duration: int = 20
    ) -> Dict:
        """
        Create an avatar video.
        
        Args:
            script: The text the avatar will speak (max ~150 words for 20s)
            avatar_id: HeyGen avatar ID
            voice_id: Voice ID for TTS
            background_color: Hex color for background
            video_duration: Approximate duration in seconds
            
        Returns:
            Dict with video_id and status
        """
        if not self.is_configured:
            return {"success": False, "error": "HEYGEN_API_KEY not configured"}
        
        # Trim script to fit duration (roughly 150 words = 60 seconds)
        words = script.split()
        max_words = int(video_duration * 2.5)  # ~2.5 words per second
        if len(words) > max_words:
            script = ' '.join(words[:max_words]) + "..."
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id
                },
                "background": {
                    "type": "color",
                    "value": background_color
                }
            }],
            "dimension": {
                "width": 1080,
                "height": 1920  # Vertical for social media
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/video/generate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "video_id": data.get("data", {}).get("video_id"),
                    "status": "processing"
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_video_status(self, video_id: str) -> Dict:
        """Check the status of a video generation."""
        if not self.is_configured:
            return {"success": False, "error": "Not configured"}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/video_status.get?video_id={video_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                return {
                    "success": True,
                    "status": data.get("status"),
                    "video_url": data.get("video_url"),
                    "thumbnail_url": data.get("thumbnail_url")
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def wait_for_video(self, video_id: str, max_wait: int = 300) -> Dict:
        """Wait for video to complete processing."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_video_status(video_id)
            
            if not status["success"]:
                return status
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                return {"success": False, "error": "Video generation failed"}
            
            time.sleep(5)  # Check every 5 seconds
        
        return {"success": False, "error": "Timeout waiting for video"}


# ============================================================================
# D-ID API CLIENT (Cheaper alternative)
# ============================================================================

class DIDClient:
    """
    D-ID API client for generating avatar videos.
    Cheapest option at $4.7/month.
    """
    
    BASE_URL = "https://api.d-id.com"
    
    def __init__(self):
        self.api_key = os.getenv("DID_API_KEY")
        self.headers = {
            "Authorization": f"Basic {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def create_video(
        self,
        script: str,
        presenter_id: str = "amy-Aq6OmGZnMt",
        voice_id: str = "en-US-JennyNeural"
    ) -> Dict:
        """Create a talking avatar video using D-ID."""
        if not self.is_configured:
            return {"success": False, "error": "DID_API_KEY not configured"}
        
        payload = {
            "script": {
                "type": "text",
                "input": script,
                "provider": {
                    "type": "microsoft",
                    "voice_id": voice_id
                }
            },
            "source_url": f"https://create-images-results.d-id.com/DefaultPresenters/{presenter_id}/image.png"
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/talks",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "video_id": data.get("id"),
                    "status": "processing"
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================================
# SCRIPT GENERATOR (AI-powered)
# ============================================================================

class ScriptGenerator:
    """Generate sales scripts using Gemini AI."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except:
                pass
    
    def generate_script(
        self,
        lead_name: str = None,
        lead_bio: str = None,
        video_duration: int = 15,
        tone: str = "professional yet friendly"
    ) -> str:
        """
        Generate a personalized sales script.
        
        Args:
            lead_name: Name of the lead for personalization
            lead_bio: Lead's bio/description for context
            video_duration: Target duration (affects word count)
            tone: Desired tone of the message
            
        Returns:
            Generated script text
        """
        # Calculate word count (approx 2.5 words per second)
        target_words = int(video_duration * 2.5)
        
        if not self.model:
            return self._fallback_script(lead_name, target_words)
        
        try:
            prompt = f"""Write a short video script for an interior design/renovation company.

Target: {lead_name or 'a potential client'}
Context: {lead_bio or 'interested in renovation services'}
Duration: {video_duration} seconds
Word count: {target_words} words MAX
Tone: {tone}

Rules:
1. Start with a friendly greeting
2. Mention we noticed their interest/work
3. Offer value (free consultation, design concept)
4. End with a soft call-to-action
5. Keep it conversational, not salesy
6. NO emojis, NO hashtags
7. EXACTLY {target_words} words or less

Output ONLY the script, nothing else."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return self._fallback_script(lead_name, target_words)
    
    def _fallback_script(self, name: str = None, words: int = 40) -> str:
        """Fallback template script."""
        name = name or "there"
        return f"""Hi {name}! I came across your profile and I was really impressed by your work. I think we could create something amazing together. At our studio, we specialize in bringing dream spaces to life. I'd love to show you a personalized design concept, completely free. Just reply to this message and let's make it happen!"""


# ============================================================================
# AVATAR VIDEO ORCHESTRATOR
# ============================================================================

class AvatarVideoStudio:
    """Master orchestrator for avatar video generation."""
    
    def __init__(self):
        self.heygen = HeyGenClient()
        self.did = DIDClient()
        self.script_gen = ScriptGenerator()
    
    def get_available_provider(self) -> str:
        """Check which provider is configured."""
        if self.heygen.is_configured:
            return "heygen"
        elif self.did.is_configured:
            return "did"
        else:
            return None
    
    def generate_video(
        self,
        script: str,
        avatar_key: str = "professional_male_1",
        voice_key: str = "en_male_professional",
        provider: str = "auto"
    ) -> Dict:
        """
        Generate an avatar video.
        
        Args:
            script: Text for the avatar to speak
            avatar_key: Key from AVATAR_CATALOG
            voice_key: Key from VOICE_OPTIONS
            provider: "heygen", "did", or "auto"
            
        Returns:
            Dict with video URL or error
        """
        # Auto-select provider
        if provider == "auto":
            provider = self.get_available_provider()
        
        if not provider:
            return {
                "success": False,
                "error": "No avatar API configured. Add HEYGEN_API_KEY or DID_API_KEY to .env"
            }
        
        # Get avatar and voice IDs
        avatar = AVATAR_CATALOG.get(avatar_key, AVATAR_CATALOG["professional_male_1"])
        voice = VOICE_OPTIONS.get(voice_key, VOICE_OPTIONS["en_male_professional"])
        
        if provider == "heygen":
            result = self.heygen.create_video(
                script=script,
                avatar_id=avatar["heygen_id"],
                voice_id=voice["heygen_voice"]
            )
            
            if result["success"]:
                # Wait for video to complete
                video_result = self.heygen.wait_for_video(result["video_id"])
                if video_result["success"]:
                    return {
                        "success": True,
                        "video_url": video_result["video_url"],
                        "thumbnail_url": video_result.get("thumbnail_url"),
                        "provider": "heygen"
                    }
                return video_result
            return result
        
        elif provider == "did":
            result = self.did.create_video(
                script=script,
                presenter_id=avatar["did_id"],
                voice_id=voice["heygen_voice"]  # D-ID also uses Azure voices
            )
            return result
        
        return {"success": False, "error": f"Unknown provider: {provider}"}
    
    def generate_personalized_video(
        self,
        lead_data: Dict,
        avatar_key: str = "professional_female_1",
        voice_key: str = "en_female_professional",
        duration: int = 15
    ) -> Dict:
        """Generate a personalized video for a lead."""
        # Generate script from lead data
        script = self.script_gen.generate_script(
            lead_name=lead_data.get("name", "").split()[0] if lead_data.get("name") else None,
            lead_bio=lead_data.get("bio"),
            video_duration=duration
        )
        
        # Generate video
        result = self.generate_video(
            script=script,
            avatar_key=avatar_key,
            voice_key=voice_key
        )
        
        result["script"] = script
        return result


# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    studio = AvatarVideoStudio()
    
    print("Avatar Video Studio initialized!")
    print(f"HeyGen configured: {studio.heygen.is_configured}")
    print(f"D-ID configured: {studio.did.is_configured}")
    print(f"Script generator ready: {studio.script_gen.model is not None}")
    
    # Test script generation
    script = studio.script_gen.generate_script("John", "Interior designer from KL", 15)
    print(f"\nGenerated script:\n{script}")
