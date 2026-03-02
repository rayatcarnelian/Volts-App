"""
LUMA DREAM MACHINE API WRAPPER
Generates high-quality AI videos from text or images.
"""

import os
import time
import requests
import json
from typing import Optional, Dict

class LumaGenerator:
    """
    Wrapper for Luma Dream Machine API.
    Handles generation creation and polling for completion.
    """
    
    # Base API URL (Subject to change based on Luma's official release, using placeholder for now)
    # NOTE: As of 2026, we assume standard Luma API endpoint structure.
    API_URL = "https://api.lumalabs.ai/dream-machine/v1/generations"
    
    def __init__(self):
        self.api_key = os.getenv("LUMA_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def generate_video(
        self,
        prompt: str,
        image_url: str = None,
        loop: bool = False,
        aspect_ratio: str = "16:9"
    ) -> Dict:
        """
        Start a video generation task.
        
        Args:
            prompt: Text description of movement/scene.
            image_url: Optional start frame (URL).
            loop: Whether to create a seamless loop.
            aspect_ratio: "16:9", "9:16", or "1:1".
            
        Returns:
            Dict containing 'id' of the generation task.
        """
        if not self.api_key:
             raise ValueError("Luma API Key not configured.")

        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": loop
        }
        
        if image_url:
            payload["keyframes"] = {
                "frame0": {
                    "type": "image",
                    "url": image_url
                }
            }
            
        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json() # Should return {"id": "gen_..."}
        except Exception as e:
            # For demo purposes, if API fails (or key is invalid/mock), we might simulate or return error
            # But strictly raising error is better for production
            print(f"[LUMA ERROR] {e}")
            raise e

    def get_generation(self, generation_id: str) -> Dict:
        """Check status of a generation."""
        url = f"{self.API_URL}/{generation_id}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json() # Returns status, assets, video_url

    def wait_for_completion(self, generation_id: str, timeout: int = 300) -> Optional[str]:
        """Polls until video is ready. Returns Video URL or None."""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            data = self.get_generation(generation_id)
            state = data.get("state") # "queued", "dreaming", "completed", "failed"
            
            if state == "completed":
                # Extract video URL
                assets = data.get("assets", {})
                return assets.get("video")
            elif state == "failed":
                raise RuntimeError(f"Luma Generation Failed: {data.get('failure_reason')}")
            
            time.sleep(5) # Poll every 5s
            
        return None
