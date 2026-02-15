"""
ZERO-COST STUDIO AGENTS
100% Free alternatives to paid APIs using:
- Hugging Face Inference API (free tier - 300 req/hour)
- PIL/MoviePy for local image animations (no API needed)
- Edge-TTS for voice synthesis (free, unlimited)
- Gemini Flash (free tier with limits)
"""

import os
import time
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

class FreeImageGenerator:
    """
    Uses Hugging Face Inference API (free tier) for image generation.
    Falls back to local gradient generation if API unavailable.
    Uses the new huggingface_hub InferenceClient (2024+ compatible).
    """
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        # Models that work with free HF inference (tested)
        self.models = [
            "black-forest-labs/FLUX.1-schnell",  # Fast, high quality
            "stabilityai/stable-diffusion-xl-base-1.0",
            "CompVis/stable-diffusion-v1-4",
        ]
        
    def generate_image(self, prompt, lead_id=None, save_dir="assets/studio/"):
        """
        Generates an image using Hugging Face free tier.
        Falls back to enhanced local generation if quota exceeded.
        """
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"concept_{lead_id or 'gen'}_{timestamp}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        # Enhanced prompt for better interior design images
        enhanced_prompt = f"ultra realistic interior design photography, {prompt}, professional architectural photography, 8k resolution, high detail, natural lighting, award winning design, architectural digest style"
        
        # Try Hugging Face API first (free tier) using InferenceClient
        if self.hf_token:
            try:
                from huggingface_hub import InferenceClient
                client = InferenceClient(token=self.hf_token)
                
                for model in self.models:
                    try:
                        # Generate image using official HF client
                        image = client.text_to_image(enhanced_prompt, model=model)
                        
                        # Enhance the image
                        image = self._enhance_image(image)
                        image.save(filepath, "JPEG", quality=95)
                        return filepath, f"Generated with {model.split('/')[-1]} (FREE)"
                        
                    except Exception:
                        continue
                        
            except ImportError:
                pass  # huggingface_hub not installed, fallback
        
        # Fallback: Generate an enhanced local concept mockup
        return self._generate_premium_mockup(prompt, filepath)
    
    def _enhance_image(self, image):
        """Apply professional enhancements to AI-generated images."""
        try:
            # Slight contrast boost
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Slight saturation boost
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.05)
            
            # Slight sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            return image
        except:
            return image
    
    def _generate_premium_mockup(self, prompt, filepath):
        """
        Creates a much more sophisticated concept mockup locally.
        Uses actual stock image fetch or creates premium gradient design.
        """
        try:
            # Try to fetch a free stock image first
            stock_image = self._fetch_stock_image(prompt)
            if stock_image:
                stock_image.save(filepath, "JPEG", quality=95)
                return filepath, "Premium stock image from Unsplash"
        except:
            pass
        
        # Create a sophisticated gradient mockup with design overlay
        return self._create_premium_gradient(prompt, filepath)
    
    def _fetch_stock_image(self, prompt):
        """Fetches a free stock image from Unsplash (free API)."""
        try:
            # Use Unsplash Source (free, no API key needed)
            keywords = "luxury+interior+design+modern"
            url = f"https://source.unsplash.com/1920x1080/?{keywords}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                # Add a subtle overlay to make it look customized
                image = self._add_design_overlay(image, prompt)
                return image
        except:
            pass
        return None
    
    def _add_design_overlay(self, image, prompt):
        """Adds a subtle branded overlay to stock images."""
        try:
            # Create overlay
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Add subtle gradient at bottom for text
            for i in range(200):
                alpha = int(180 * (i / 200))
                y = image.size[1] - 200 + i
                draw.line([(0, y), (image.size[0], y)], fill=(0, 0, 0, alpha))
            
            # Convert to RGB for final save
            image = image.convert('RGBA')
            image = Image.alpha_composite(image, overlay)
            return image.convert('RGB')
        except:
            return image
    
    def _create_premium_gradient(self, prompt, filepath):
        """Creates a sophisticated gradient-based design concept as final fallback."""
        try:
            width, height = 1920, 1080
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            # Create a rich gradient background (dark luxury aesthetic)
            for i in range(height):
                # Dark gradient from charcoal to deep navy
                r = int(25 + (i / height) * 15)
                g = int(25 + (i / height) * 20)
                b = int(35 + (i / height) * 25)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
            
            # Add subtle grid pattern for sophistication
            for x in range(0, width, 80):
                for y in range(0, height, 80):
                    draw.rectangle([x, y, x+1, y+1], fill=(60, 60, 80))
            
            # Large decorative geometric shapes (representing space)
            # Main "room" outline
            draw.rectangle([150, 150, 1770, 930], outline=(180, 160, 120), width=2)
            
            # Interior floor (perspective effect)
            draw.polygon([(150, 930), (960, 500), (1770, 930)], fill=(45, 40, 55))
            
            # Window/Light source rectangle
            draw.rectangle([700, 200, 1220, 480], fill=(255, 250, 240))
            draw.rectangle([720, 220, 1200, 460], fill=(255, 255, 245))
            
            # Furniture shapes (abstract)
            draw.rectangle([250, 650, 550, 900], fill=(70, 65, 85), outline=(100, 95, 110))
            draw.rectangle([1350, 700, 1650, 900], fill=(65, 60, 80), outline=(100, 95, 110))
            draw.ellipse([850, 600, 1100, 850], fill=(80, 75, 95), outline=(110, 105, 120))
            
            # Gold accent line at top
            draw.rectangle([0, 0, width, 8], fill=(212, 175, 55))
            
            # Text overlays
            try:
                font_title = ImageFont.truetype("arial.ttf", 56)
                font_sub = ImageFont.truetype("arial.ttf", 28)
                font_prompt = ImageFont.truetype("arial.ttf", 20)
            except:
                font_title = ImageFont.load_default()
                font_sub = font_title
                font_prompt = font_title
            
            # Title block
            draw.rectangle([60, 40, 700, 140], fill=(0, 0, 0))
            draw.text((80, 55), "DESIGN CONCEPT", fill=(212, 175, 55), font=font_title)
            
            # Subtitle
            draw.text((80, 110), "VOLTS INTERIOR STUDIO", fill=(150, 150, 150), font=font_sub)
            
            # Prompt display at bottom
            prompt_short = prompt[:100] + "..." if len(prompt) > 100 else prompt
            draw.rectangle([60, height-80, width-60, height-20], fill=(0, 0, 0, 200))
            draw.text((80, height-65), f"Vision: {prompt_short}", fill=(180, 180, 180), font=font_prompt)
            
            img.save(filepath, "JPEG", quality=95)
            return filepath, "Premium gradient concept (offline mode)"
            
        except Exception as e:
            return None, str(e)


class FreeVideoAnimator:
    """
    Creates video animations from static images using MoviePy.
    No API costs - runs 100% locally.
    """
    
    def __init__(self):
        pass
    
    def create_ken_burns(self, image_path, output_path=None, duration=5, zoom_factor=1.1):
        """
        Creates a Ken Burns effect (slow zoom + pan) from a static image.
        Professional-looking animation without any API costs.
        Uses PIL directly to avoid MoviePy resize ANTIALIAS deprecation.
        """
        try:
            from moviepy import ImageSequenceClip
            from PIL import Image
            import numpy as np
            
            # Patch for PIL ANTIALIAS deprecation
            if not hasattr(Image, 'ANTIALIAS'):
                Image.ANTIALIAS = Image.LANCZOS
            
            if not output_path:
                timestamp = int(time.time())
                output_path = f"assets/studio/videos/animation_{timestamp}.mp4"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Load and prepare image
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            w, h = img.size
            # Ensure even dimensions
            if w % 2 != 0: w -= 1
            if h % 2 != 0: h -= 1
            img = img.resize((w, h), Image.LANCZOS)
            
            # Generate frames using PIL (avoids MoviePy resize)
            fps = 24
            num_frames = int(duration * fps)
            frames = []
            
            for i in range(num_frames):
                t = i / num_frames
                scale = 1 + (zoom_factor - 1) * t
                
                # Calculate crop dimensions for zoom effect
                new_w = int(w / scale)
                new_h = int(h / scale)
                
                # Center crop coordinates
                left = (w - new_w) // 2
                top = (h - new_h) // 2
                right = left + new_w
                bottom = top + new_h
                
                # Crop and resize back to original dimensions
                frame = img.crop((left, top, right, bottom))
                frame = frame.resize((w, h), Image.LANCZOS)
                frames.append(np.array(frame))
            
            # Create video from frames
            clip = ImageSequenceClip(frames, fps=fps)
            clip.write_videofile(
                output_path, 
                fps=fps, 
                codec='libx264', 
                audio=False,
                preset='medium',
                threads=4,
                logger=None
            )
            clip.close()
            
            return output_path, None
            
        except Exception as e:
            return None, str(e)
    
    def create_slideshow(self, image_paths, output_path=None, slide_duration=3):
        """
        Creates a slideshow video from multiple images.
        Uses PIL to avoid ANTIALIAS deprecation.
        """
        try:
            from moviepy import ImageSequenceClip
            from PIL import Image
            import numpy as np
            
            # Patch for PIL ANTIALIAS deprecation
            if not hasattr(Image, 'ANTIALIAS'):
                Image.ANTIALIAS = Image.LANCZOS
            
            if not output_path:
                timestamp = int(time.time())
                output_path = f"assets/studio/videos/slideshow_{timestamp}.mp4"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Determine output size from first image
            first_img = Image.open(image_paths[0])
            target_w, target_h = first_img.size
            # Ensure even dimensions
            if target_w % 2 != 0: target_w -= 1
            if target_h % 2 != 0: target_h -= 1
            
            # Generate frames for all images
            fps = 24
            frames_per_image = int(slide_duration * fps)
            all_frames = []
            
            for img_path in image_paths:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to match target dimensions
                img = img.resize((target_w, target_h), Image.LANCZOS)
                frame_array = np.array(img)
                
                # Add frames for this image
                for _ in range(frames_per_image):
                    all_frames.append(frame_array)
            
            # Create video from frames
            clip = ImageSequenceClip(all_frames, fps=fps)
            clip.write_videofile(
                output_path, 
                fps=fps, 
                codec='libx264', 
                audio=False,
                preset='medium',
                threads=4,
                logger=None
            )
            clip.close()
            
            return output_path, None
            
        except Exception as e:
            return None, str(e)


class FreeVoiceGenerator:
    """
    Uses Edge-TTS for unlimited free text-to-speech.
    No API costs, high quality voices.
    """
    
    def __init__(self):
        self.default_voice = "en-GB-RyanNeural"  # Professional British male
        self.available_voices = {
            "professional_male": "en-GB-RyanNeural",
            "professional_female": "en-GB-SoniaNeural",
            "american_male": "en-US-GuyNeural",
            "american_female": "en-US-JennyNeural",
            "luxury_male": "en-AU-WilliamNeural"
        }
    
    def generate_speech(self, text, voice_style="professional_male", output_path=None):
        """
        Generates speech using Edge-TTS (free, unlimited).
        """
        try:
            import asyncio
            import edge_tts
            
            if not output_path:
                timestamp = int(time.time())
                output_path = f"assets/studio/audio/speech_{timestamp}.mp3"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            voice = self.available_voices.get(voice_style, self.default_voice)
            
            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            asyncio.run(_generate())
            return output_path, None
            
        except Exception as e:
            return None, str(e)


class FreePresentationCreator:
    """
    Creates full video presentations with images + voiceover.
    Uses MoviePy + Edge-TTS. Zero cost.
    """
    
    def __init__(self):
        self.voice_gen = FreeVoiceGenerator()
        self.animator = FreeVideoAnimator()
    
    def create_presentation(self, image_paths, script, output_path=None):
        """
        Creates a narrated slideshow presentation.
        """
        try:
            from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
            
            if not output_path:
                timestamp = int(time.time())
                output_path = f"assets/studio/presentations/pres_{timestamp}.mp4"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 1. Generate voiceover
            audio_path = output_path.replace('.mp4', '_temp.mp3')
            self.voice_gen.generate_speech(script, output_path=audio_path)
            
            # 2. Load audio to get duration
            audio = AudioFileClip(audio_path)
            total_duration = audio.duration
            slide_duration = total_duration / len(image_paths)
            
            # 3. Create video clips
            clips = []
            for img_path in image_paths:
                clip = ImageClip(img_path).set_duration(slide_duration)
                
                # Add Ken Burns zoom
                def make_zoom(clip, duration):
                    return clip.resize(lambda t: 1 + 0.05 * (t / duration))
                
                clip = make_zoom(clip, slide_duration)
                clip = clip.crossfadein(0.5)
                clips.append(clip)
            
            # 4. Concatenate and add audio
            video = concatenate_videoclips(clips, method="compose")
            video = video.set_audio(audio)
            
            # 5. Export
            video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            # Cleanup
            audio.close()
            video.close()
            for c in clips:
                c.close()
            
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return output_path, None
            
        except Exception as e:
            return None, str(e)


class ZeroCostOrchestrator:
    """
    Master orchestrator using all free tools.
    """
    
    def __init__(self):
        self.image_gen = FreeImageGenerator()
        self.video_gen = FreeVideoAnimator()
        self.voice_gen = FreeVoiceGenerator()
        self.presenter = FreePresentationCreator()
    
    def process_lead_free(self, lead_data, content_types=None):
        """
        Processes a lead using only free tools.
        """
        if content_types is None:
            content_types = ["image", "script"]
        
        results = {
            "lead_id": lead_data.get('id'),
            "name": lead_data.get('name'),
            "content": []
        }
        
        # Generate prompt based on lead
        bio = lead_data.get('bio', '')
        name = lead_data.get('name', 'Client')
        
        prompt = f"Luxury modern interior design inspired by {name}'s profile: {bio[:100]}"
        
        # Image generation
        if "image" in content_types:
            img_path, error = self.image_gen.generate_image(prompt, lead_data.get('id'))
            if img_path:
                results['content'].append({"type": "image", "path": img_path})
                
                # Video animation (free)
                if "video" in content_types:
                    vid_path, _ = self.video_gen.create_ken_burns(img_path)
                    if vid_path:
                        results['content'].append({"type": "video", "path": vid_path})
        
        # Script generation (uses Gemini free tier)
        if "script" in content_types:
            script = self._generate_outreach_script(lead_data)
            results['outreach_script'] = script
            
            # Voiceover (free)
            if "voiceover" in content_types:
                audio_path, _ = self.voice_gen.generate_speech(script)
                if audio_path:
                    results['content'].append({"type": "audio", "path": audio_path})
        
        return results
    
    def _generate_outreach_script(self, lead_data):
        """
        Generates outreach script using Gemini free tier or template.
        """
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""Write a short, sophisticated outreach message (max 50 words) for:
Name: {lead_data.get('name')}
Role: {lead_data.get('bio', 'Professional')}

Be professional, intriguing, not salesy. Reference their work if possible."""

                response = model.generate_content(prompt)
                return response.text.strip()
        except:
            pass
        
        # Fallback template
        name = lead_data.get('name', 'there').split()[0]
        return f"Hi {name}, I noticed your impressive work and created a design concept inspired by it. Would love to share it with you."
