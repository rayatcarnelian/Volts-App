import os
import time
import replicate
import google.generativeai as genai
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

class CinemaDirector:
    def __init__(self):
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.vision_model = genai.GenerativeModel('gemini-2.0-flash')

    def direct_scene(self, image_path):
        """Uses Gemini Vision to analyze the image and suggest a camera movement."""
        if not self.vision_model:
            return "Error: Gemini Keys missing."
            
        retries = 3
        base_delay = 15
        
        for attempt in range(retries):
            try:
                # Load image for Gemini
                sample_file = genai.upload_file(image_path)
                
                prompt = """
                Act as a cinematography director. Describe a 5-second camera movement for this interior design shot to make it look like a luxury real estate commercial. 
                Keep it under 20 words. Focus on 'Slow Dolly', 'Pan', or 'Push In'. 
                Do not include phrases like 'Here is a ...'. Just the movement description.
                """
                
                response = self.vision_model.generate_content([sample_file, prompt])
                return response.text.strip()
                
            except Exception as e:
                # Robust Error Handling (Auto-fallback for Free Tier Limits)
                if "429" in str(e) or "Quota" in str(e):
                    if attempt < retries - 1:
                        wait = 30 + (10 * attempt) # API asked for ~35s
                        st.warning(f"⚠️ High Traffic (Free Tier Limit). Pausing for {wait}s to cool down... (Attempt {attempt+1}/{retries})")
                        time.sleep(wait)
                        continue
                return f"Director Error: {str(e)}"

    def render_video(self, image_path, prompt, save_path="assets/videos/"):
        """Uses Replicate Minimax Video-01 to generate video."""
        if not self.replicate_token:
            st.error("Replicate Token missing.")
            return None
            
        os.makedirs(save_path, exist_ok=True)
        
        try:
            # Replicate wants a public URL or a file handle. 
            # For local files, we pass the file object directly if the client supports it,
            # or we might need to rely on Replicate's ability to handle upload.
            # The python client handles file uploads automatically if passed as open file.
            
            output = replicate.run(
                "minimax/video-01",
                input={
                    "first_frame_image": open(image_path, "rb"),
                    "prompt": prompt,
                    "prompt_optimizer": True
                }
            )
            
            # Minimax returns a URL to the mp4
            video_url = str(output)
            
            filename = f"scene_{int(time.time())}.mp4"
            filepath = os.path.join(save_path, filename)
            
            # Download
            with requests.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
            return filepath
            
        except Exception as e:
            st.error(f"Render Error check logs: {e}")
            return None

    def render_montage(self, image_paths, prompt):
        """Generates multiple videos and stitches them together."""
        from moviepy import concatenate_videoclips
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        clips_paths = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total = len(image_paths)
        
        for idx, img_path in enumerate(image_paths):
            status_text.text(f"Animating scene {idx+1}/{total}... (This takes ~2 mins)")
            clip_path = self.render_video(img_path, prompt)
            
            if clip_path:
                clips_paths.append(clip_path)
            
            progress_bar.progress((idx + 1) / total)
            
        if not clips_paths:
            return None
            
        try:
            status_text.text("Stitching montage...")
            # Load all clips
            loaded_clips = [VideoFileClip(p) for p in clips_paths]
            
            # Concatenate
            final_clip = concatenate_videoclips(loaded_clips, method="compose")
            
            filename = f"montage_{int(time.time())}.mp4"
            filepath = os.path.join("assets/videos", filename)
            
            final_clip.write_videofile(filepath, fps=24, codec='libx264', audio_codec='aac')
            
            # Cleanup
            for c in loaded_clips:
                c.close()
                
            return filepath
            
        except Exception as e:
            st.error(f"Montage Error: {e}")
            return None
