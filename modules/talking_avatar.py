"""
FREE LIP-SYNC TALKING AVATAR
Uses Hugging Face SadTalker API (100% FREE, unlimited)
Creates real talking face videos with mouth movement.
"""

import os
import time
import asyncio
import requests
import base64
from typing import Optional, Dict, Tuple, List, Any
from PIL import Image
from io import BytesIO

# Edge-TTS for free voice
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Gradio client for Hugging Face Spaces
try:
    from gradio_client import Client, handle_file
    GRADIO_CLIENT_AVAILABLE = True
except ImportError:
    GRADIO_CLIENT_AVAILABLE = False


# ============================================================================
# AVATAR FACE CATALOG - Real Faces for Selection
# ============================================================================

# These are real professional stock photos we'll download
AVATAR_FACES = {
    # Male Professionals
    "james_chen": {
        "name": "James Chen",
        "description": "Executive, 40s, Asian, formal suit",
        "gender": "male",
        "style": "executive",
        "preview": "👔",
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=512&h=512&fit=crop&crop=face"
    },
    "david_miller": {
        "name": "David Miller", 
        "description": "Professional, 30s, Caucasian, smart casual",
        "gender": "male",
        "style": "professional",
        "preview": "👨‍💼",
        "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=512&h=512&fit=crop&crop=face"
    },
    "marcus_johnson": {
        "name": "Marcus Johnson",
        "description": "Creative, 35, African American, modern",
        "gender": "male", 
        "style": "creative",
        "preview": "🧑‍💻",
        "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=512&h=512&fit=crop&crop=face"
    },
    "ryan_patel": {
        "name": "Ryan Patel",
        "description": "Sales, 28, Indian, approachable",
        "gender": "male",
        "style": "friendly",
        "preview": "😊",
        "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=512&h=512&fit=crop&crop=face"
    },
    "robert_williams": {
        "name": "Robert Williams",
        "description": "CEO, 55, distinguished, gray hair",
        "gender": "male",
        "style": "senior",
        "preview": "👨‍🦳",
        "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=512&h=512&fit=crop&crop=face"
    },
    "alex_kim": {
        "name": "Alex Kim",
        "description": "Tech Lead, 32, Korean, casual",
        "gender": "male",
        "style": "tech",
        "preview": "💻",
        "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=512&h=512&fit=crop&crop=face"
    },
    "omar_hassan": {
        "name": "Omar Hassan",
        "description": "Consultant, 38, Middle Eastern, professional",
        "gender": "male",
        "style": "consultant",
        "preview": "📊",
        "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=512&h=512&fit=crop&crop=face"
    },
    
    # Female Professionals
    "sarah_anderson": {
        "name": "Sarah Anderson",
        "description": "Senior Partner, 40s, blonde, power suit",
        "gender": "female",
        "style": "executive",
        "preview": "👩‍💼",
        "image_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop&crop=face"
    },
    "emily_zhang": {
        "name": "Emily Zhang",
        "description": "Marketing Director, 32, Asian, elegant",
        "gender": "female",
        "style": "marketing",
        "preview": "💼",
        "image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=512&h=512&fit=crop&crop=face"
    },
    "jessica_lee": {
        "name": "Jessica Lee",
        "description": "Design Lead, 29, creative, trendy",
        "gender": "female",
        "style": "creative",
        "preview": "🎨",
        "image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=512&h=512&fit=crop&crop=face"
    },
    "amanda_torres": {
        "name": "Amanda Torres",
        "description": "Client Relations, 27, Latina, warm",
        "gender": "female",
        "style": "friendly",
        "preview": "😄",
        "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=512&h=512&fit=crop&crop=face"
    },
    "catherine_brooks": {
        "name": "Catherine Brooks",
        "description": "Managing Director, 50, authoritative",
        "gender": "female",
        "style": "senior",
        "preview": "👩‍🦳",
        "image_url": "https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=512&h=512&fit=crop&crop=face"
    },
    "priya_sharma": {
        "name": "Priya Sharma",
        "description": "Product Manager, 33, Indian, dynamic",
        "gender": "female",
        "style": "tech",
        "preview": "🚀",
        "image_url": "https://images.unsplash.com/photo-1598550874175-4d0ef436c909?w=512&h=512&fit=crop&crop=face"
    },
    "michelle_wong": {
        "name": "Michelle Wong",
        "description": "Finance Director, 35, professional",
        "gender": "female",
        "style": "finance",
        "preview": "📈",
        "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=512&h=512&fit=crop&crop=face"
    },
    "nina_rodriguez": {
        "name": "Nina Rodriguez",
        "description": "Account Executive, 26, energetic",
        "gender": "female",
        "style": "sales",
        "preview": "⚡",
        "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=512&h=512&fit=crop&crop=face"
    },
}

# Free Edge-TTS voices
FREE_VOICES = {
    "en_male_professional": {"name": "English Male (Professional)", "voice_id": "en-US-GuyNeural"},
    "en_female_professional": {"name": "English Female (Professional)", "voice_id": "en-US-JennyNeural"},
    "en_male_friendly": {"name": "English Male (Friendly)", "voice_id": "en-US-DavisNeural"},
    "en_female_friendly": {"name": "English Female (Friendly)", "voice_id": "en-US-AriaNeural"},
    "en_gb_male": {"name": "British Male", "voice_id": "en-GB-RyanNeural"},
    "en_gb_female": {"name": "British Female", "voice_id": "en-GB-SoniaNeural"},
    "ms_male": {"name": "Malay Male", "voice_id": "ms-MY-OsmanNeural"},
    "ms_female": {"name": "Malay Female", "voice_id": "ms-MY-YasminNeural"},
    "zh_male": {"name": "Chinese Male", "voice_id": "zh-CN-YunxiNeural"},
    "zh_female": {"name": "Chinese Female", "voice_id": "zh-CN-XiaoxiaoNeural"},
}


# ============================================================================
# FACE DOWNLOADER
# ============================================================================

class FaceDownloader:
    """Downloads and manages avatar face images."""
    
    def __init__(self):
        self.face_dir = "assets/avatars/faces"
        os.makedirs(self.face_dir, exist_ok=True)
    
    def get_face_path(self, avatar_key: str) -> Optional[str]:
        """Get path to avatar face image, download if needed."""
        filepath = os.path.join(self.face_dir, f"{avatar_key}.jpg")
        
        if os.path.exists(filepath):
            return filepath
        
        # Try local AVATAR_FACES first
        url = None
        avatar = AVATAR_FACES.get(avatar_key)
        if avatar:
            url = avatar.get("image_url")
        else:
            # Fallback to avatar_library
            try:
                from modules.avatar_library import get_avatar_by_id
                lib_avatar = get_avatar_by_id(avatar_key)
                if lib_avatar:
                    url = lib_avatar.thumbnail_url
            except ImportError:
                print("Could not import avatar_library")
        
        if not url:
            print(f"No URL found for avatar key: {avatar_key}")
            return None
        
        # Download from URL
        try:
            # Add headers for some sites specifically (like randomuser or generated photos)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Resize to optimal size for LivePortrait/SadTalker (512x512)
                # Ensure dimensions are multiples of 2 for video codecs
                img = img.resize((512, 512), Image.LANCZOS)
                img.save(filepath, "JPEG", quality=95)
                return filepath
            else:
                print(f"Download failed: Status {response.status_code} for {url}")
        except Exception as e:
            print(f"Download failed for {avatar_key}: {e}")
        
        return None
    
    def download_all_faces(self) -> Dict[str, str]:
        """Download all avatar faces."""
        paths = {}
        for key in AVATAR_FACES.keys():
            path = self.get_face_path(key)
            if path:
                paths[key] = path
        return paths
    
    def get_available_faces(self) -> List[str]:
        """Get list of available downloaded faces."""
        available = []
        for key in AVATAR_FACES.keys():
            filepath = os.path.join(self.face_dir, f"{key}.jpg")
            if os.path.exists(filepath):
                available.append(key)
        return available


# ============================================================================
# LIP-SYNC VIDEO GENERATOR
# Priority: Sync Labs (FREE 1-min) > Replicate > Local Animated
# ============================================================================

class LipSyncVideoGenerator:
    """
    Generates talking face videos with REAL lip-sync.
    
    Priority order:
    1. Sync Labs API (FREE tier: up to 1 minute videos!) - REAL LIP-SYNC
    2. Replicate API (needs credits) - REAL LIP-SYNC
    3. Local animated fallback (always works, but no lip-sync)
    
    Get FREE Sync Labs API key at: https://sync.so/keys
    """
    
    def __init__(self):
        self.output_dir = "assets/studio/avatar_videos"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Check for API keys
        self.sync_labs_key = os.environ.get("SYNC_LABS_API_KEY")
        self.replicate_token = os.environ.get("REPLICATE_API_TOKEN")
        self.did_api_key = os.environ.get("DID_API_KEY") # Added D-ID API key
        
    def generate_talking_video(self, face_image_path: str, audio_path: str, output_path: str) -> Dict[str, Any]:
        """
        Generate talking video using available APIs or fallback.
        
        Priority Order:
        1. LivePortrait (FREE, emotion-aware, no watermark) 
        2. D-ID (High quality, watermark on free tier)
        3. Sync Labs (Free, real lip-sync)
        4. Replicate (Paid)
        5. Local animated fallback
        """
        try:
            # 1. Try LivePortrait (BEST: Free + No Watermark + Emotions)
            if self.replicate_token:  # LivePortrait requires Replicate
                path, error = self._try_liveportrait(face_image_path, audio_path, output_path)
                if path:
                    return {
                        "success": True, 
                        "video_path": path, 
                        "avatar": "Custom Avatar", 
                        "voice": "Generated Audio", 
                        "error": None,
                        "provider": "LivePortrait (FREE, Emotion-Aware)"
                    }
                else:
                    print(f"LivePortrait Error: {error}") # Fallthrough
            
            # 2. Try D-ID (High Quality but watermark on free)
            if self.did_api_key:
                path, error = self._try_did(face_image_path, audio_path, output_path)
                if path:
                    return {
                        "success": True, 
                        "video_path": path, 
                        "avatar": "Custom Avatar", 
                        "voice": "Generated Audio", 
                        "error": None,
                        "provider": "D-ID (High Quality)"
                    }
                else:
                    print(f"D-ID Error: {error}") # Fallthrough
            
            # 3. Try Sync Labs (Free Unlimited)
            if self.sync_labs_key:
                path, error = self._try_sync_labs(face_image_path, audio_path, output_path)
                if path:
                    return {
                        "success": True, 
                        "video_path": path, 
                        "avatar": "Custom Avatar", 
                        "voice": "Generated Audio", 
                        "error": None,
                        "provider": "Sync Labs (Real Lip-Sync)"
                    }
            
            # 4. Try Replicate
            if self.replicate_token:
                path, error = self._try_replicate(face_image_path, audio_path, output_path)
                if path:
                    return {
                        "success": True, 
                        "video_path": path, 
                        "avatar": "Custom Avatar", 
                        "voice": "Generated Audio", 
                        "error": None,
                        "provider": "Replicate"
                    }
            
            # 4. Fallback
            path, error = self._create_animated_fallback(face_image_path, audio_path, output_path)
            if path:
                return {
                    "success": True,
                    "video_path": path,
                    "avatar": "Custom Avatar",
                    "voice": "Generated Audio",
                    "error": None,
                    "provider": "Local Animated Fallback"
                }
            else:
                return {"success": False, "error": error or "Failed to generate video with fallback."}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def _try_did(self, face_path: str, audio_path: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Try D-ID API for professional talking head generation."""
        try:
            import requests
            import time
            
            # 1. Upload files to get public URLs
            img_url = self._upload_file(face_path)
            audio_url = self._upload_file(audio_path)
            
            if not img_url or not audio_url:
                return None, "Failed to upload files for D-ID"
            
            # 2. Create Talk
            url = "https://api.d-id.com/talks"
            headers = {
                "Authorization": f"Basic {self.did_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "source_url": img_url,
                "script": {
                    "type": "audio",
                    "audio_url": audio_url
                },
                "config": {
                    "fluent": True,
                    "pad_audio": "0.0"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 201:
                return None, f"D-ID Creation Error: {response.text}"
            
            talk_id = response.json().get("id")
            
            # 3. Poll for completion
            for _ in range(60): # 2 mins max
                time.sleep(2)
                status_resp = requests.get(f"{url}/{talk_id}", headers=headers)
                status_data = status_resp.json()
                
                status = status_data.get("status")
                
                if status == "done":
                    result_url = status_data.get("result_url")
                    if result_url:
                        # Download
                        v_resp = requests.get(result_url)
                        with open(output_path, "wb") as f:
                            f.write(v_resp.content)
                        return output_path, None
                elif status == "error":
                    return None, f"D-ID Error: {status_data}"
                    
            return None, "D-ID generation timed out"
            
        except Exception as e:
            return None, f"D-ID Exception: {e}"
 
    def _try_liveportrait(self, face_image_path: str, audio_path: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        LivePortrait - Emotion-aware talking head via Replicate.
        
        Features:
        - Natural facial expressions and emotions
        - Realistic head movements
        - High-fidelity lip-sync
        - FREE (Replicate community tier)
        - NO watermarks (open source)
        """
        try:
            import replicate
            
            with open(face_image_path, "rb") as img_file:
                image_data = img_file
                
                with open(audio_path, "rb") as aud_file:
                    audio_data = aud_file
                    
                    # Run LivePortrait model on Replicate
                    output = replicate.run(
                        "fofr/live-portrait:e09003d6ee26c56a6e268c7bfe3dc5d8b4e4d98a56a24fce1e4fb4fa2d63c201",
                        input={
                            "source_image": image_data,
                            "driving_video": audio_data,
                            "flag_do_crop": True,
                            "flag_pasteback": True,
                            "flag_stitching": True,
                            "flag_relative": True
                        }
                    )
            
            # Download result
            if output:
                import requests
                video_response = requests.get(str(output), timeout=300)
                with open(output_path, "wb") as f:
                    f.write(video_response.content)
                return output_path, None
            else:
                return None, "LivePortrait returned no output"
                
        except Exception as e:
            return None, f"LivePortrait error: {str(e)}"

    def _try_sync_labs(self, face_path: str, audio_path: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Try Sync Labs API for REAL lip-sync using official SDK.
        FREE tier: up to 1 minute videos!
        """
        try:
            from sync import Sync
            
            # First, we need to create a video from the static image
            # We'll create a simple loop video for lip-sync
            temp_video = self._create_static_video_from_image(face_path)
            if not temp_video:
                return None, "Failed to create video from image"
            
            client = Sync(api_key=self.sync_labs_key)
            
            # Upload files to temporary host to get public URLs
            # Sync Labs requires public URLs for best reliability
            video_url = self._upload_file(temp_video)
            audio_url = self._upload_file(audio_path)
            
            if not video_url or not audio_url:
                return None, "Failed to upload files for processing"
                
            # Create generation
            response = client.generations.create(
                model="lipsync-2",
                input=[
                    {"type": "video", "url": video_url},
                    {"type": "audio", "url": audio_url}
                ],
                options={"output_format": "mp4"}
            )
            
            job_id = response.id
            
            # Poll for completion
            for _ in range(150):  # Max 5 minutes (free tier can be slow)
                time.sleep(2)
                job = client.generations.get(job_id)
                
                if job.status == "COMPLETED":
                    output_url = job.output_url
                    # Try to find output URL in various fields just in case
                    if not output_url and hasattr(job, 'output'):
                        output_url = job.output[0].url if isinstance(job.output, list) else job.output
                    
                    if output_url:
                        import requests
                        video_response = requests.get(output_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        
                        # Cleanup temp video
                        try:
                            os.remove(temp_video)
                        except:
                            pass
                        
                        return output_path, None
                    return None, "No output URL in response"
                
                elif job.status == "FAILED":
                    return None, f"Sync Labs generation failed: {job.error}"
            
            return None, "Sync Labs generation timed out"
            
        except Exception as e:
            return None, f"Sync Labs error: {str(e)}"

    def _upload_file(self, file_path: str) -> Optional[str]:
        """Upload file to temporary host (Catbox.moe) to get public URL."""
        try:
            import requests
            # Catbox.moe is reliable for temporary public hosting
            with open(file_path, 'rb') as f:
                response = requests.post(
                    'https://catbox.moe/user/api.php',
                    data={'reqtype': 'fileupload'},
                    files={'fileToUpload': f}
                )
            
            if response.status_code == 200:
                url = response.text
                if url.startswith('http'):
                    return url
            return None
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    def _create_static_video_from_image(self, image_path: str) -> Optional[str]:
        """Create a short video from a static image for lip-sync."""
        try:
            from moviepy import ImageClip
            
            output_path = os.path.join(self.output_dir, f"temp_video_{int(time.time())}.mp4")
            
            # Create a 5-second video from the image
            clip = ImageClip(image_path, duration=5)
            clip = clip.set_fps(25)
            
            clip.write_videofile(
                output_path,
                fps=25,
                codec='libx264',
                audio=False,
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error creating video from image: {e}")
            return None
    
    def _try_replicate(self, face_path: str, audio_path: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Try Replicate API for lip-sync."""
        try:
            import replicate
            
            # Read files as base64
            with open(face_path, "rb") as f:
                face_data = base64.b64encode(f.read()).decode()
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            output = replicate.run(
                "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a8f95957bd844003b401ca4e4a9b33baa574c549d376",
                input={
                    "source_image": f"data:image/jpeg;base64,{face_data}",
                    "driven_audio": f"data:audio/mp3;base64,{audio_data}",
                    "preprocess": "crop",
                    "still_mode": True
                }
            )
            
            if output:
                # Download result
                response = requests.get(output, timeout=60)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    return output_path, None
            
            return None, "Replicate returned no result"
            
        except Exception as e:
            return None, f"Replicate error: {str(e)}"
    
    def _create_animated_fallback(self, face_path: str, audio_path: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Create an animated video locally when no API available.
        Uses zoom, pan, and subtle movement effects.
        NOTE: This does NOT do real lip-sync, just animation.
        """
        try:
            from moviepy import AudioFileClip, ImageClip, CompositeVideoClip
            import numpy as np
            
            # Load audio to get duration
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # Load face image
            face_img = Image.open(face_path)
            face_img = face_img.convert('RGB')
            
            # Video settings
            fps = 24
            video_w, video_h = 720, 1280  # Portrait
            
            # Create frames with animation
            frames = []
            total_frames = int(duration * fps)
            
            for frame_num in range(total_frames):
                t = frame_num / fps
                progress = t / duration
                
                # Create background
                frame = Image.new('RGB', (video_w, video_h), (20, 25, 35))
                
                # Subtle zoom effect (1.0 to 1.08)
                zoom = 1.0 + 0.08 * progress
                
                # Subtle "breathing" effect
                breath = abs(np.sin(t * 3.5)) * 0.02
                zoom += breath
                
                # Calculate avatar size
                base_size = int(video_w * 0.85)
                avatar_size = int(base_size * zoom)
                
                # Resize face
                face_resized = face_img.resize((avatar_size, avatar_size), Image.LANCZOS)
                
                # Center position with subtle movement
                y_offset = int(np.sin(t * 2) * 8)
                x = (video_w - avatar_size) // 2
                y = 120 + y_offset - int(progress * 30)
                
                # Paste face
                frame.paste(face_resized, (x, y))
                frames.append(np.array(frame))
            
            # Create video with moviepy
            from moviepy import ImageSequenceClip
            
            video = ImageSequenceClip(frames, fps=fps)
            video = video.set_audio(audio)
            
            video.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            return output_path, None
            
        except Exception as e:
            return None, f"Local fallback error: {str(e)}"


# ============================================================================
# FREE TALKING AVATAR STUDIO
# ============================================================================

class FreeTalkingAvatarStudio:
    """
    100% FREE Talking Avatar Video Generator.
    Uses:
    - Edge-TTS (free unlimited voice)
    - Local animated fallback (always works)
    - Replicate API (if key provided)
    - Unsplash stock photos (free faces)
    """
    
    def __init__(self):
        self.face_downloader = FaceDownloader()
        self.lip_sync = LipSyncVideoGenerator()
        self.output_dir = "assets/studio/avatar_videos"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Premium compositor for professional scenes
        try:
            from modules.premium_video_compositor import PremiumVideoCompositor, PREMIUM_PRESENTERS, VIRTUAL_STUDIOS
            self.compositor = PremiumVideoCompositor()
            self.premium_mode = True
            self.presenters = PREMIUM_PRESENTERS
            self.studios = VIRTUAL_STUDIOS
        except ImportError:
            self.compositor = None
            self.premium_mode = False
            self.presenters = {}
            self.studios = {}
    
    async def _generate_voice_async(self, text: str, voice_id: str, output_path: str) -> bool:
        """Generate voice audio."""
        if not EDGE_TTS_AVAILABLE:
            return False
        try:
            communicate = edge_tts.Communicate(text, voice_id)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"Voice generation failed: {e}")
            return False
    
    def generate_voice(self, text: str, voice_key: str, output_path: str) -> bool:
        """Generate voice audio synchronously."""
        voice = FREE_VOICES.get(voice_key, FREE_VOICES["en_male_professional"])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(
                self._generate_voice_async(text, voice["voice_id"], output_path)
            )
        finally:
            loop.close()
        
        return success
    
    def generate_talking_video(
        self,
        script: str,
        avatar_key: str = "david_miller",
        voice_key: str = "en_male_professional",
        presenter_key: str = None,
        studio_key: str = "modern_office"
    ) -> Dict:
        """
        Generate a talking avatar video with lip-sync.
        
        If presenter_key is provided, uses PREMIUM MODE:
        - Composites presenter with virtual studio
        - Sends professional scene to D-ID
        
        Otherwise uses BASIC MODE:
        - Downloads simple face
        - Uses D-ID or fallback
        
        Returns:
            {
                "success": bool,
                "video_path": str or None,
                "avatar": str,
                "voice": str,
                "provider": str,
                "error": str or None
            }
        """
        timestamp = int(time.time())
        
        # Step 1: Get face/scene image
        if presenter_key and self.premium_mode:
            # PREMIUM MODE: Compose professional scene
            scene_path, error = self.compositor.compose_scene(presenter_key, studio_key)
            if not scene_path:
                return {"success": False, "error": f"Scene composition failed: {error}"}
            face_path = scene_path
            presenter_info = self.presenters.get(presenter_key, {})
            avatar_name = presenter_info.get("name", presenter_key)
        else:
            # BASIC MODE: Use simple face
            face_path = self.face_downloader.get_face_path(avatar_key)
            if not face_path:
                return {"success": False, "error": f"Could not download face for {avatar_key}"}
            avatar_info = AVATAR_FACES.get(avatar_key, {})
            avatar_name = avatar_info.get("name", avatar_key)
        
        # Step 2: Generate voice
        audio_path = os.path.join(self.output_dir, f"audio_{timestamp}.mp3")
        voice_success = self.generate_voice(script, voice_key, audio_path)
        if not voice_success:
            return {"success": False, "error": "Voice generation failed"}
        
        # Step 3: Generate lip-synced video
        video_path = os.path.join(self.output_dir, f"talking_{presenter_key or avatar_key}_{timestamp}.mp4")
        
        result = self.lip_sync.generate_talking_video(
            face_image_path=face_path,
            audio_path=audio_path,
            output_path=video_path
        )
        
        # Cleanup audio file
        try:
            os.remove(audio_path)
        except:
            pass
        
        if result.get("success"):
            voice_info = FREE_VOICES.get(voice_key, {})
            
            return {
                "success": True,
                "video_path": result.get("video_path"),
                "avatar": avatar_name,
                "voice": voice_info.get("name", voice_key),
                "provider": result.get("provider", "Talking Head AI"),
                "error": None
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Video generation failed")
            }
    
    def get_available_avatars(self) -> Dict:
        """Get all available avatars."""
        return AVATAR_FACES
    
    def get_available_voices(self) -> Dict:
        """Get all available voices."""
        return FREE_VOICES
    
    def download_all_faces(self) -> int:
        """Pre-download all avatar faces. Returns count."""
        paths = self.face_downloader.download_all_faces()
        return len(paths)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FREE TALKING AVATAR STUDIO")
    print("=" * 60)
    print(f"Avatars: {len(AVATAR_FACES)}")
    print(f"Voices: {len(FREE_VOICES)}")
    print()
    
    print("AVAILABLE AVATARS:")
    for key, avatar in AVATAR_FACES.items():
        print(f"  {avatar['preview']} {avatar['name']} - {avatar['description']}")
    
    print()
    print("AVAILABLE VOICES:")
    for key, voice in FREE_VOICES.items():
        print(f"  🎤 {voice['name']}")
    
    print()
    print("DEPENDENCIES:")
    print(f"  Edge-TTS: {'✅' if EDGE_TTS_AVAILABLE else '❌'}")
    print(f"  Gradio Client: {'✅' if GRADIO_CLIENT_AVAILABLE else '❌'}")
