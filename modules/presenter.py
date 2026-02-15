import os
import asyncio
import edge_tts
import google.generativeai as genai
# MoviePy 1.x Imports
from moviepy import ImageClip, ColorClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

class PresenterProducer:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    async def generate_script(self, context):
        """Generates a narrator script using Gemini."""
        if not self.model:
            return "Error: Gemini API Key missing."
        
        prompt = f"""
        Write a sophisticated, 30-second audio script for a high-end interior design commercial based on this context: 
        '{context}'
        
        Rules:
        - Do not include visual directions (no [Fade in], [Scene 1] etc). 
        - Just the spoken words.
        - Tone: Luxury, confident, inviting.
        - Keep it under 60 words.
        """
        retries = 3
        # base_delay = 10 # Unused
        
        for attempt in range(retries):
            try:
                response = await self.model.generate_content_async(prompt)
                return response.text.strip()
            except Exception as e:
                if "429" in str(e) or "Quota" in str(e):
                    if attempt < retries - 1:
                        wait = 30 + (10 * attempt)
                        st.warning(f"⚠️ High Traffic (Free Tier Limit). Pausing for {wait}s... (Attempt {attempt+1}/{retries})")
                        await asyncio.sleep(wait)
                        continue
                return f"Script Error: {str(e)}"

    async def generate_audio(self, text, voice="en-GB-RyanNeural", output_file="temp_audio.mp3"):
        """Generates MP3 using Edge-TTS."""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            return output_file
        except Exception as e:
            st.error(f"TTS Error: {e}")
            return None

    def create_slideshow(self, image_paths, audio_path, output_path, slide_duration=3.0):
        """Creates a slideshow from multiple images with Ken Burns and transitions (v1 compatible)."""
        try:
            audio_clip = AudioFileClip(audio_path)
            total_audio_duration = audio_clip.duration
            
            clips = []
            
            # Determine base resolution from first image
            first_clip = ImageClip(image_paths[0])
            w, h = first_clip.size
            
            # Ensure even dimensions for encoding
            if w % 2 != 0: w -= 1
            if h % 2 != 0: h -= 1
            base_size = (w, h)
            first_clip.close()

            for img_path in image_paths:
                # Load
                clip = ImageClip(img_path)
                
                # Resize to cover
                img_w, img_h = clip.size
                scale = max(w / img_w, h / img_h)
                clip = clip.resize(scale) # v1 syntax
                
                # Center crop
                icon_w, icon_h = clip.size
                x1 = (icon_w / 2) - (w / 2)
                y1 = (icon_h / 2) - (h / 2)
                clip = clip.crop(x1=x1, y1=y1, width=w, height=h) # v1 syntax
                
                clip = clip.set_duration(slide_duration) # v1 syntax
                
                # Simple zoom 1.0 -> 1.05
                # v1 syntax: resize(lambda t: ...)
                zoomed_clip = (clip.resize(lambda t: 1 + 0.05 * (t / slide_duration))
                               .set_position('center')) # v1 syntax
                
                # Composite onto base black slide
                final_slide = CompositeVideoClip([zoomed_clip], size=base_size).set_duration(slide_duration)
                
                # Crossfade In (v1 syntax: method of VideoClip)
                # Note: crossfadein makes the clip start transparent and fade in.
                final_slide = final_slide.crossfadein(0.5)
                clips.append(final_slide)

            # Concatenate
            video = concatenate_videoclips(clips, method="compose") 
            
            # Loop video if audio is longer
            if video.duration < total_audio_duration:
                # v1 syntax loop helper from fx
                import moviepy.video.fx.all as vfx
                # Loop n times to cover duration
                # Or just loop duration?
                # v1 loop(duration=...) might not exist on clip directly in all versions, but let's try .loop()
                # Actually safest is to repeat list or use vfx.loop
                # video.loop(duration=...) is valid in many versions
                video = video.fx(vfx.loop, duration=total_audio_duration)
            else:
                video = video.set_duration(total_audio_duration)
            
            video = video.set_audio(audio_clip)
            
            # Write
            video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', preset='medium', threads=4)
            
            audio_clip.close()
            video.close()
            return output_path

        except Exception as e:
            st.error(f"Slideshow Error: {e}")
            return None

    async def produce_commercial(self, image_paths, context, voice, output_folder="assets/presentations/", slide_duration=3.0):
        """Orchestrator."""
        os.makedirs(output_folder, exist_ok=True)
        
        # 1. Script
        script = await self.generate_script(context)
        if "Error" in script:
            return None, script
            
        # 2. Audio
        audio_path = os.path.join(output_folder, "temp_vo.mp3")
        audio_res = await self.generate_audio(script, voice, audio_path)
        if not audio_res:
            return None, "Audio Generation Failed"
            
        # 3. Video
        timestamp = int(time.time())
        video_filename = f"presentation_{timestamp}.mp4"
        video_path = os.path.join(output_folder, video_filename)
        
        # Determine if single or multi image
        if isinstance(image_paths, str):
            image_paths = [image_paths]
            
        final_video = self.create_slideshow(image_paths, audio_path, video_path, slide_duration)
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return final_video, script
