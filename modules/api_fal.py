"""
Fal.ai API Integration
Provides high-speed, cost-effective Image and Video generation.
"""
import os
import fal_client

def is_configured() -> bool:
    """Check if the Fal.ai API key is available in the environment."""
    return bool(os.getenv("FAL_KEY"))

def generate_image(prompt: str, image_size: str = "landscape_16_9") -> dict:
    """Generate an image using FLUX.1 [schnell] for ultra-fast, cheap B-Roll."""
    if not is_configured():
        return {
            "success": False, 
            "error": "Fal API key not found. Please add FAL_KEY to your .env file."
        }
        
    try:
        # Using the insanely fast and cheap FLUX.1 [schnell] model
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_inference_steps": 4, # Standard for schnell
            },
            with_logs=True
        )
        
        if result and "images" in result and result["images"]:
            return {
                "success": True,
                "image_url": result["images"][0]["url"],
            }
        else:
            return {"success": False, "error": "No image returned from Fal.ai"}
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Fal API Error: {str(e)}"
        }

def generate_video(prompt: str, image_url: str = None) -> dict:
    """Generate a short B-Roll video clip using Kling 1.5 Standard (Cost-Optimized)."""
    if not is_configured():
        return {"success": False, "error": "Fal API key missing."}
        
    try:
        arguments = {"prompt": prompt}
        
        # Switch to Text-to-Video endpoint if no image is provided,
        # otherwise use Image-to-Video endpoint. (Cost Optimized Kling 1.5)
        model_endpoint = "fal-ai/kling-video/v1/standard/text-to-video" if not image_url else "fal-ai/kling-video/v1/standard/image-to-video"
        
        if image_url:
            arguments["image_url"] = image_url
            
        result = fal_client.subscribe(
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
    if not is_configured():
        return {"success": False, "error": "Fal API key missing."}
        
    try:
        # Sync Lipsync 2.0 (High quality, $3/min)
        result = fal_client.subscribe(
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
