import os
import requests
import streamlit as st

class VoiceStudio:
    """
    Handles AI Voice Cloning and Generation using ElevenLabs.
    """
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate_voice_preview(self, text, voice_id="21m00Tcm4TlvDq8ikWAM", stability=0.5):
        """
        Generates audio bytes for a given text.
        Default voice: Rachel (Generic)
        """
        if not self.api_key:
            return None, "Error: ElevenLabs API Key missing in .env"
            
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                os.makedirs("assets/audio", exist_ok=True)
                # Create a unique filename
                import time
                filename = f"assets/audio/voice_{int(time.time())}.mp3"
                with open(filename, "wb") as f:
                    f.write(response.content)
                return filename, None
            else:
                return None, f"ElevenLabs API Error: {response.text}"
        except Exception as e:
            return None, f"Connection Error: {str(e)}"

    def get_voices(self):
        """Fetch available voices."""
        if not self.api_key:
            return []
            
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('voices', [])
            return []
        except:
            return []
