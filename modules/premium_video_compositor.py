"""
PREMIUM VIDEO COMPOSITOR
Merges professional presenters with virtual studio backgrounds.
This is the "secret sauce" that makes AI videos look like HeyGen/Synthesia.
"""

import os
from typing import Optional, Tuple
from PIL import Image
import requests
from io import BytesIO

# Professional half-body presenters (Unsplash stock)
PREMIUM_PRESENTERS = {
    "exec_male_1": {
        "name": "Marcus Chen - Executive",
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=768&h=1024&fit=crop&crop=face,top",
        "style": "Executive in navy suit",
        "crop": "half_body"
    },
    "exec_female_1": {
        "name": "Sarah Williams - CEO",
        "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=768&h=1024&fit=crop&crop=face,top",
        "style": "Professional executive",
        "crop": "half_body"
    },
    "tech_male_1": {
        "name": "David Park - Tech Lead",
        "url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=768&h=1024&fit=crop&crop=face,top",
        "style": "Casual tech professional",
        "crop": "half_body"
    },
    "tech_female_1": {
        "name": "Emily Zhang - Product Manager",
        "url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=768&h=1024&fit=crop&crop=face,top",
        "style": "Modern professional",
        "crop": "half_body"
    },
    "business_male_1": {
        "name": "James Anderson - Sales Director",
        "url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=768&h=1024&fit=crop&crop=face,top",
        "style": "Business suit",
        "crop": "half_body"
    }
}

# Virtual studio backgrounds (High-quality)
VIRTUAL_STUDIOS = {
    "modern_office": {
        "name": "Modern Office",
        "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&h=1080&fit=crop",
        "description": "Bright, airy modern office"
    },
    "luxury_home": {
        "name": "Luxury Home Office",
        "url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&h=1080&fit=crop",
        "description": "High-end residential office"
    },
    "newsroom": {
        "name": "News Studio",
        "url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=1920&h=1080&fit=crop",
        "description": "Professional broadcast studio"
    },
    "tech_office": {
        "name": "Tech Startup",
        "url": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1920&h=1080&fit=crop",
        "description": "Silicon Valley vibe"
    },
    "neutral_gray": {
        "name": "Neutral Studio",
        "url": None,  # We'll generate this solid color
        "description": "Clean gray background",
        "color": (45, 52, 64)
    }
}


class PremiumVideoCompositor:
    """Composes professional presenters with virtual studios."""
    
    def __init__(self):
        self.cache_dir = "assets/premium_studio"
        self.presenters_dir = os.path.join(self.cache_dir, "presenters")
        self.studios_dir = os.path.join(self.cache_dir, "studios")
        
        os.makedirs(self.presenters_dir, exist_ok=True)
        os.makedirs(self.studios_dir, exist_ok=True)
    
    def download_asset(self, url: str, save_path: str) -> bool:
        """Download an asset with caching."""
        if os.path.exists(save_path):
            return True
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(save_path, "JPEG", quality=95)
                return True
        except Exception as e:
            print(f"Download failed: {e}")
        return False
    
    def get_presenter_path(self, presenter_key: str) -> Optional[str]:
        """Get path to presenter image, download if needed."""
        presenter = PREMIUM_PRESENTERS.get(presenter_key)
        if not presenter:
            return None
        
        filepath = os.path.join(self.presenters_dir, f"{presenter_key}.jpg")
        
        if self.download_asset(presenter["url"], filepath):
            return filepath
        return None
    
    def get_studio_path(self, studio_key: str) -> Optional[str]:
        """Get path to studio background, download or generate if needed."""
        studio = VIRTUAL_STUDIOS.get(studio_key)
        if not studio:
            return None
        
        filepath = os.path.join(self.studios_dir, f"{studio_key}.jpg")
        
        # Special case: solid color backgrounds
        if studio.get("url") is None and studio.get("color"):
            if not os.path.exists(filepath):
                img = Image.new('RGB', (1920, 1080), studio["color"])
                img.save(filepath, "JPEG", quality=95)
            return filepath
        
        if self.download_asset(studio["url"], filepath):
            return filepath
        return None
    
    def remove_background(self, image_path: str) -> Optional[Image.Image]:
        """Remove background from presenter image using rembg."""
        try:
            from rembg import remove
            
            with open(image_path, 'rb') as f:
                input_data = f.read()
            
            # Remove background
            output_data = remove(input_data)
            
            # Convert to PIL Image with transparency
            img = Image.open(BytesIO(output_data))
            return img.convert("RGBA")
            
        except ImportError:
            print("rembg not installed. Using original image.")
            img = Image.open(image_path)
            return img.convert("RGBA")
        except Exception as e:
            print(f"Background removal failed: {e}")
            img = Image.open(image_path)
            return img.convert("RGBA")
    
    def compose_scene(
        self, 
        presenter_key: str, 
        studio_key: str,
        output_path: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Compose a professional scene: Presenter + Studio Background.
        
        Returns:
            (output_path, error_message)
        """
        try:
            # Get assets
            presenter_path = self.get_presenter_path(presenter_key)
            studio_path = self.get_studio_path(studio_key)
            
            if not presenter_path or not studio_path:
                return None, "Failed to load presenter or studio"
            
            # Load studio background
            studio = Image.open(studio_path).convert("RGB")
            studio = studio.resize((1920, 1080), Image.LANCZOS)
            
            # Load and remove background from presenter
            presenter_rgba = self.remove_background(presenter_path)
            
            # Scale presenter to fit nicely in frame (about 60-70% of height)
            target_height = int(1080 * 0.75)
            aspect = presenter_rgba.width / presenter_rgba.height
            target_width = int(target_height * aspect)
            presenter_rgba = presenter_rgba.resize((target_width, target_height), Image.LANCZOS)
            
            # Position presenter (slightly right of center, bottom aligned)
            x_pos = (1920 - target_width) // 2 + 100  # Slightly right
            y_pos = 1080 - target_height - 50  # 50px from bottom
            
            # Composite
            studio.paste(presenter_rgba, (x_pos, y_pos), presenter_rgba)
            
            # Save
            if not output_path:
                output_path = os.path.join(
                    self.cache_dir, 
                    f"scene_{presenter_key}_{studio_key}.jpg"
                )
            
            studio.save(output_path, "JPEG", quality=95)
            return output_path, None
            
        except Exception as e:
            return None, f"Composition error: {str(e)}"
    
    def preview_all_combinations(self, max_combos: int = 3):
        """Generate preview images of presenter+studio combinations."""
        combos = []
        for p_key in list(PREMIUM_PRESENTERS.keys())[:2]:  # First 2 presenters
            for s_key in list(VIRTUAL_STUDIOS.keys())[:2]:  # First 2 studios
                path, error = self.compose_scene(p_key, s_key)
                if path:
                    combos.append(path)
                    if len(combos) >= max_combos:
                        return combos
        return combos


if __name__ == "__main__":
    print("=" * 60)
    print("PREMIUM VIDEO COMPOSITOR")
    print("=" * 60)
    
    compositor = PremiumVideoCompositor()
    
    print("\nAvailable Presenters:")
    for key, info in PREMIUM_PRESENTERS.items():
        print(f"  - {info['name']}")
    
    print("\nAvailable Studios:")
    for key, info in VIRTUAL_STUDIOS.items():
        print(f"  - {info['name']}")
    
    print("\nGenerating test composition...")
    output, error = compositor.compose_scene("exec_male_1", "modern_office")
    
    if output:
        print(f"SUCCESS! Saved to: {output}")
    else:
        print(f"ERROR: {error}")
