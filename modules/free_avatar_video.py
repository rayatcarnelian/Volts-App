"""
FREE AVATAR VIDEO GENERATOR
100% Free, Local, No API Keys Required

Uses:
- Edge-TTS (Microsoft's free text-to-speech API)
- Stock avatar images
- MoviePy for video composition
- Simple lip-sync simulation with image transitions
"""

import os
import time
import asyncio
import tempfile
from typing import Optional, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

# Edge-TTS for free voice
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# MoviePy for video
try:
    from moviepy import (
        ImageClip, AudioFileClip, CompositeVideoClip, 
        TextClip, concatenate_videoclips, ColorClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


# ============================================================================
# FREE AVATAR IMAGES (Public domain / CC0 / AI-generated placeholders)
# ============================================================================

# We'll use Picsum/UI Faces or generate simple avatars
FREE_AVATARS = {
    "avatar_male_1": {
        "name": "Alex",
        "description": "Professional male",
        "preview": "👨‍💼",
        "color": "#3498db",  # Blue
        "initials": "AX"
    },
    "avatar_female_1": {
        "name": "Sarah", 
        "description": "Professional female",
        "preview": "👩‍💼",
        "color": "#e74c3c",  # Red
        "initials": "SR"
    },
    "avatar_male_2": {
        "name": "Marcus",
        "description": "Friendly male",
        "preview": "🧑",
        "color": "#2ecc71",  # Green
        "initials": "MC"
    },
    "avatar_female_2": {
        "name": "Emma",
        "description": "Friendly female", 
        "preview": "👩",
        "color": "#9b59b6",  # Purple
        "initials": "EM"
    },
    "avatar_neutral": {
        "name": "Jordan",
        "description": "Modern professional",
        "preview": "🧑‍💻",
        "color": "#f39c12",  # Orange
        "initials": "JD"
    }
}


# Free Edge-TTS voices (Microsoft Azure Free tier)
FREE_VOICES = {
    "en_male_professional": {"name": "English (Male, Professional)", "voice_id": "en-US-GuyNeural"},
    "en_female_professional": {"name": "English (Female, Professional)", "voice_id": "en-US-JennyNeural"},
    "en_male_friendly": {"name": "English (Male, Friendly)", "voice_id": "en-US-DavisNeural"},
    "en_female_friendly": {"name": "English (Female, Friendly)", "voice_id": "en-US-AriaNeural"},
    "en_gb_male": {"name": "British (Male)", "voice_id": "en-GB-RyanNeural"},
    "en_gb_female": {"name": "British (Female)", "voice_id": "en-GB-SoniaNeural"},
    "ms_male": {"name": "Malay (Male)", "voice_id": "ms-MY-OsmanNeural"},
    "ms_female": {"name": "Malay (Female)", "voice_id": "ms-MY-YasminNeural"},
    "zh_male": {"name": "Chinese Mandarin (Male)", "voice_id": "zh-CN-YunxiNeural"},
    "zh_female": {"name": "Chinese Mandarin (Female)", "voice_id": "zh-CN-XiaoxiaoNeural"},
}


# ============================================================================
# AVATAR IMAGE GENERATOR (Creates simple but professional avatar images)
# ============================================================================

class AvatarImageGenerator:
    """Generates simple avatar images locally - no API needed."""
    
    def __init__(self):
        self.avatar_dir = "assets/avatars"
        os.makedirs(self.avatar_dir, exist_ok=True)
    
    def create_avatar(self, avatar_key: str, size: int = 512) -> str:
        """Create a simple but professional-looking avatar image."""
        avatar = FREE_AVATARS.get(avatar_key, FREE_AVATARS["avatar_male_1"])
        
        filepath = os.path.join(self.avatar_dir, f"{avatar_key}.png")
        
        # Check if already exists
        if os.path.exists(filepath):
            return filepath
        
        # Create circular avatar with gradient background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Parse color
        color = avatar["color"]
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Draw circular background
        draw.ellipse([0, 0, size-1, size-1], fill=(r, g, b))
        
        # Draw initials
        initials = avatar["initials"]
        
        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", size // 3)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 3)
            except:
                font = ImageFont.load_default()
        
        # Center the text
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - text_height // 4
        
        draw.text((x, y), initials, fill=(255, 255, 255), font=font)
        
        img.save(filepath, "PNG")
        return filepath
    
    def get_speaking_frames(self, avatar_key: str, num_frames: int = 3) -> list:
        """Create simple speaking animation frames."""
        base_path = self.create_avatar(avatar_key)
        
        # For now, just return the same image (can be enhanced later)
        # In a full implementation, this would create mouth shapes
        return [base_path] * num_frames


# ============================================================================
# FREE TEXT-TO-SPEECH (Edge-TTS - Microsoft Free)
# ============================================================================

class FreeVoiceGenerator:
    """Generate voice audio using Edge-TTS (100% free)."""
    
    def __init__(self):
        self.audio_dir = "assets/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def generate_audio_async(
        self, 
        text: str, 
        voice_id: str = "en-US-GuyNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Tuple[Optional[str], Optional[str]]:
        """Generate audio from text using Edge-TTS."""
        if not EDGE_TTS_AVAILABLE:
            return None, "edge-tts not installed. Run: pip install edge-tts"
        
        try:
            timestamp = int(time.time())
            output_path = os.path.join(self.audio_dir, f"voice_{timestamp}.mp3")
            
            # Create communicate object
            communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
            
            await communicate.save(output_path)
            
            return output_path, None
            
        except Exception as e:
            return None, str(e)
    
    def generate_audio(self, text: str, voice_id: str = "en-US-GuyNeural") -> Tuple[Optional[str], Optional[str]]:
        """Synchronous wrapper for generate_audio_async."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.generate_audio_async(text, voice_id))
            loop.close()
            return result
        except Exception as e:
            return None, str(e)


# ============================================================================
# FREE VIDEO COMPOSER
# ============================================================================

class FreeAvatarVideoComposer:
    """Compose avatar videos locally - 100% free."""
    
    def __init__(self):
        self.output_dir = "assets/studio/avatar_videos"
        os.makedirs(self.output_dir, exist_ok=True)
        self.avatar_gen = AvatarImageGenerator()
        self.voice_gen = FreeVoiceGenerator()
    
    def create_video(
        self,
        script: str,
        avatar_key: str = "avatar_male_1",
        voice_key: str = "en_male_professional",
        background_color: str = "#1a1a2e"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Create an avatar video with voice.
        
        Returns:
            Tuple of (video_path, error_message)
        """
        if not MOVIEPY_AVAILABLE:
            return None, "MoviePy not installed. Run: pip install moviepy"
        
        if not EDGE_TTS_AVAILABLE:
            return None, "edge-tts not installed. Run: pip install edge-tts"
        
        try:
            timestamp = int(time.time())
            
            # 1. Generate avatar image
            avatar_path = self.avatar_gen.create_avatar(avatar_key, size=512)
            
            # 2. Generate voice audio
            voice = FREE_VOICES.get(voice_key, FREE_VOICES["en_male_professional"])
            audio_path, error = self.voice_gen.generate_audio(script, voice["voice_id"])
            
            if not audio_path:
                return None, f"Voice generation failed: {error}"
            
            # 3. Create video with avatar and audio
            output_path = os.path.join(self.output_dir, f"avatar_video_{timestamp}.mp4")
            
            # Load audio to get duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Parse background color
            bg_color = background_color.lstrip('#')
            bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Create background
            bg_clip = ColorClip(size=(1080, 1920), color=bg_rgb, duration=duration)
            
            # Create avatar clip (centered in upper portion)
            avatar_img = Image.open(avatar_path).convert("RGBA")
            avatar_img = avatar_img.resize((400, 400), Image.LANCZOS)
            
            # Convert to RGB with background
            avatar_rgb = Image.new("RGB", avatar_img.size, bg_rgb)
            avatar_rgb.paste(avatar_img, mask=avatar_img.split()[3] if avatar_img.mode == 'RGBA' else None)
            
            # Save as temp file for MoviePy
            temp_avatar = os.path.join(self.output_dir, f"temp_avatar_{timestamp}.png")
            avatar_rgb.save(temp_avatar)
            
            avatar_clip = (ImageClip(temp_avatar)
                          .set_duration(duration)
                          .set_position(("center", 400)))
            
            # Create subtitle text
            # Split script into chunks for readability
            words = script.split()
            words_per_chunk = 8
            chunks = [' '.join(words[i:i+words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
            chunk_duration = duration / len(chunks) if chunks else duration
            
            # Create text clips for subtitles
            text_clips = []
            for i, chunk in enumerate(chunks):
                try:
                    txt_clip = (TextClip(chunk, fontsize=40, color='white', font='Arial',
                                        size=(1000, None), method='caption')
                               .set_start(i * chunk_duration)
                               .set_duration(chunk_duration)
                               .set_position(("center", 1400)))
                    text_clips.append(txt_clip)
                except:
                    # Fallback if TextClip fails (needs ImageMagick)
                    pass
            
            # Compose final video
            clips = [bg_clip, avatar_clip] + text_clips
            final = CompositeVideoClip(clips)
            final = final.set_audio(audio_clip)
            
            # Write video
            final.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(self.output_dir, f"temp_audio_{timestamp}.m4a"),
                remove_temp=True,
                logger=None  # Suppress output
            )
            
            # Cleanup temp files
            if os.path.exists(temp_avatar):
                os.remove(temp_avatar)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Close clips
            audio_clip.close()
            final.close()
            
            return output_path, None
            
        except Exception as e:
            return None, str(e)


# ============================================================================
# MAIN FREE AVATAR VIDEO STUDIO
# ============================================================================

class FreeAvatarVideoStudio:
    """
    100% Free Avatar Video Generator
    No API keys required!
    """
    
    def __init__(self):
        self.composer = FreeAvatarVideoComposer()
        self.script_gen = None
        
        # Try to use Gemini for script generation
        try:
            from modules.avatar_video import ScriptGenerator
            self.script_gen = ScriptGenerator()
        except:
            pass
    
    def generate_video(
        self,
        script: str,
        avatar_key: str = "avatar_male_1",
        voice_key: str = "en_male_professional"
    ) -> Dict:
        """Generate a free avatar video."""
        result = self.composer.create_video(
            script=script,
            avatar_key=avatar_key,
            voice_key=voice_key
        )
        
        if result[0]:
            return {
                "success": True,
                "video_path": result[0],
                "provider": "local_free"
            }
        else:
            return {
                "success": False,
                "error": result[1]
            }
    
    def generate_script(self, lead_name: str = None, lead_bio: str = None, duration: int = 15) -> str:
        """Generate a personalized script."""
        if self.script_gen and self.script_gen.model:
            return self.script_gen.generate_script(lead_name, lead_bio, duration)
        
        # Fallback script
        name = lead_name or "there"
        return f"""Hi {name}! I noticed your amazing work and I think we could create something incredible together. At our studio, we specialize in bringing dream spaces to life. I'd love to show you a personalized design concept, completely free. Just reply to this message and let's make it happen!"""


# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    print("Free Avatar Video Studio")
    print("=" * 50)
    
    # Check dependencies
    print(f"Edge-TTS available: {EDGE_TTS_AVAILABLE}")
    print(f"MoviePy available: {MOVIEPY_AVAILABLE}")
    
    if EDGE_TTS_AVAILABLE and MOVIEPY_AVAILABLE:
        studio = FreeAvatarVideoStudio()
        
        # Test avatar generation
        avatar_gen = AvatarImageGenerator()
        path = avatar_gen.create_avatar("avatar_male_1")
        print(f"Avatar created: {path}")
        
        print("\nReady to generate free avatar videos!")
    else:
        print("\nMissing dependencies. Install with:")
        print("pip install edge-tts moviepy")
