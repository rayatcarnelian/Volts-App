"""
Fal.ai API Integration
Provides high-speed, cost-effective Image and Video generation.
"""
import os

def get_user_fal_key() -> str:
    """Retrieves the user's personal Fal key directly from the DB or Environment."""
    key = os.getenv("FAL_KEY")
    
    try:
        import streamlit as st
        from modules.db_supabase import get_user_setting
        
        # Pull straight from the secure DB so it survives session reloads
        if 'user' in st.session_state and st.session_state['user']:
            user_id = st.session_state['user']['id']
            db_key = get_user_setting(user_id, "FAL_KEY")
            if db_key:
                key = db_key
    except Exception as e:
        print(f"Error resolving User FAL Key: {e}")
        pass
        
    return key


def generate_image(prompt: str, image_size: str = "landscape_16_9") -> dict:
    """Generate an image using FLUX.1 [schnell] for ultra-fast, cheap B-Roll."""
    key = get_user_fal_key()
    if not key:
        return {
            "success": False, 
            "error": "Fal API key not found. Please add it in Settings."
        }
        
    try:
        import fal_client
        import concurrent.futures
        client = fal_client.SyncClient(key=key)
        
        args = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 4,
        }
        
        # Wrapped in a ThreadPoolExecutor to prevent infinite hangs 
        # when Fal AI drops the stream silently due to safety filters
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                client.subscribe,
                "fal-ai/flux/schnell",
                arguments=args,
                with_logs=True
            )
            # FLUX [schnell] renders in 2-4 seconds. If it takes >45s, 
            # it's guaranteed to be a silent server hang or safety block.
            result = future.result(timeout=45)
        
        if result and "images" in result and result["images"]:
            return {
                "success": True,
                "image_url": result["images"][0]["url"],
            }
        else:
            return {"success": False, "error": "No image returned from Fal.ai."}
            
    except concurrent.futures.TimeoutError:
        return {
            "success": False,
            "error": "Fal AI Timeout: Your prompt may have triggered a safety filter or the server is unresponsive."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Fal API Error: {str(e)}"
        }

def generate_video(prompt: str, image_url: str = None) -> dict:
    """Generate a short B-Roll video clip."""
    key = get_user_fal_key()
    if not key:
        return {"success": False, "error": "Fal API key missing."}
        
    try:
        import fal_client
        client = fal_client.SyncClient(key=key)
        
        arguments = {"prompt": prompt}
        
        # Switch to Text-to-Video endpoint if no image is provided,
        # otherwise use Image-to-Video endpoint. (Wan 2.1 - Ultra Fast & Cost Effective)
        model_endpoint = "fal-ai/wan-t2v" if not image_url else "fal-ai/wan-i2v"
        
        if image_url:
            arguments["image_url"] = image_url
            
        result = client.subscribe(
            model_endpoint,
            arguments=arguments,
            with_logs=True
        )
        
        if result and "video" in result and result["video"]:
            return {
                "success": True,
                "video_url": result["video"]["url"]
            }
        else:
            return {"success": False, "error": "No video returned from Fal.ai"}
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Fal API Video Error: {str(e)}"
        }

def generate_avatar_sync(video_url: str, audio_url: str) -> dict:
    """Lip-sync a base avatar video to a new audio track using Sync Lipsync."""
    key = get_user_fal_key()
    if not key:
        return {"success": False, "error": "Fal API key missing."}
        
    try:
        import fal_client
        client = fal_client.SyncClient(key=key)
        
        # Sync Lipsync 2.0 (High quality, $3/min)
        result = client.subscribe(
            "fal-ai/sync-lipsync",
            arguments={
                "video_url": video_url,
                "audio_url": audio_url,
                "sync_mode": "cut_off" # Trims to match whichever is shortest
            },
            with_logs=True
        )
        
        if result and "video" in result and result["video"]:
             return {
                "success": True,
                "video_url": result["video"]["url"]
            }
        else:
             return {"success": False, "error": "Lip-sync rendering failed on Fal.ai"}
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Fal API Avatar Sync Error: {str(e)}"
        }
