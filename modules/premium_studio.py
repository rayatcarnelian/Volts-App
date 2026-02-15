"""
PREMIUM STUDIO ENGINE
Enterprise-grade image generation rivaling Midjourney, DALL-E 3, and Adobe Firefly.

Features:
- FLUX.1 integration via Replicate (schnell/dev/pro quality tiers)
- AI-powered prompt enhancement (Gemini)
- Style reference (match aesthetics from reference image)
- Structure reference (preserve layouts/compositions)
- Image variations (4x grid generation)
- Outpainting/expand (extend image boundaries)
- 2x/4x upscaling (Real-ESRGAN)
"""

import os
import time
import json
import base64
import requests
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class GenerationConfig:
    """Configuration for image generation."""
    # Quality modes
    MODE_QUICK = "schnell"      # 2-4 seconds, good quality
    MODE_QUALITY = "dev"        # 10-15 seconds, great quality  
    MODE_ULTRA = "pro"          # 20-30 seconds, maximum quality
    
    # Aspect ratios (width, height)
    ASPECT_SQUARE = (1024, 1024)
    ASPECT_LANDSCAPE_16_9 = (1344, 768)
    ASPECT_LANDSCAPE_3_2 = (1216, 832)
    ASPECT_PORTRAIT_9_16 = (768, 1344)
    ASPECT_PORTRAIT_2_3 = (832, 1216)
    
    # Interior design style presets
    STYLE_PRESETS = {
        "luxury_modern": "ultra realistic, luxury modern interior design, high-end finishes, natural materials, warm lighting, architectural photography, 8k, professional",
        "minimalist": "minimalist interior design, clean lines, neutral palette, scandinavian influence, natural light, serene atmosphere, architectural digest style",
        "art_deco": "art deco interior design, geometric patterns, gold accents, velvet textures, glamorous, sophisticated, dramatic lighting",
        "industrial": "industrial loft interior, exposed brick, metal fixtures, concrete floors, edison bulbs, urban chic, raw materials",
        "tropical_luxury": "tropical luxury resort interior, natural materials, rattan, teak wood, lush greenery, ocean views, bali style",
        "boutique_hotel": "boutique hotel suite, designer furniture, curated art, premium materials, ambient lighting, five star luxury",
        "penthouse": "penthouse interior, floor to ceiling windows, city skyline view, contemporary furniture, marble finishes, ultra luxury",
        "japanese_zen": "japanese zen interior, tatami, shoji screens, natural wood, minimalist, peaceful, wabi-sabi aesthetic"
    }


# ============================================================================
# PROMPT ENHANCEMENT ENGINE (Like DALL-E 3 + ChatGPT)
# ============================================================================

class PromptEnhancer:
    """
    AI-powered prompt enhancement that transforms simple descriptions
    into detailed, optimized prompts for maximum image quality.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except:
                pass
    
    def enhance(self, simple_prompt: str, style_preset: str = None) -> str:
        """
        Transforms a simple prompt into a detailed, professional prompt.
        Like how DALL-E 3 uses ChatGPT to expand prompts.
        """
        if not self.model:
            return self._fallback_enhance(simple_prompt, style_preset)
        
        try:
            system_prompt = """You are an expert prompt engineer for AI image generation.
Your task is to expand a simple description into a detailed, professional prompt.

Rules:
1. Keep the core concept but add rich details
2. Include photography terms (lighting, composition, lens)
3. Add material and texture descriptions
4. Specify atmosphere and mood
5. Include quality modifiers (8k, professional, award-winning)
6. Maximum 100 words
7. Output ONLY the enhanced prompt, nothing else

Focus on interior design and architecture photography style."""

            user_msg = f"Enhance this prompt: {simple_prompt}"
            if style_preset:
                user_msg += f"\nStyle direction: {style_preset}"
            
            response = self.model.generate_content(
                f"{system_prompt}\n\n{user_msg}"
            )
            
            enhanced = response.text.strip()
            # Clean up any quotes or formatting
            enhanced = enhanced.strip('"\'')
            return enhanced
            
        except Exception as e:
            return self._fallback_enhance(simple_prompt, style_preset)
    
    def _fallback_enhance(self, prompt: str, style_preset: str = None) -> str:
        """Fallback enhancement using templates."""
        base = f"ultra realistic interior design photograph, {prompt}"
        
        if style_preset and style_preset in GenerationConfig.STYLE_PRESETS:
            base = f"{base}, {GenerationConfig.STYLE_PRESETS[style_preset]}"
        else:
            base = f"{base}, professional architectural photography, natural lighting, high detail, 8k resolution, award winning design"
        
        return base


# ============================================================================
# FLUX.1 IMAGE GENERATOR (Via Replicate with HuggingFace fallback)
# ============================================================================

class FluxGenerator:
    """
    FLUX.1 image generation via Replicate API.
    Falls back to HuggingFace free tier if Replicate fails (out of credits).
    """
    
    # Replicate model IDs for FLUX.1 variants
    MODELS = {
        "schnell": "black-forest-labs/flux-schnell",
        "dev": "black-forest-labs/flux-dev", 
        "pro": "black-forest-labs/flux-1.1-pro"
    }
    
    # HuggingFace free FLUX.1 endpoint
    HF_FLUX_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        self.hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        self.client = None
        self.use_free_fallback = False
        
        if self.api_token:
            try:
                import replicate
                self.client = replicate.Client(api_token=self.api_token)
            except ImportError:
                pass
    
    def generate(
        self,
        prompt: str,
        mode: str = "schnell",
        width: int = 1024,
        height: int = 1024,
        num_outputs: int = 1,
        guidance_scale: float = 3.5,
        num_inference_steps: int = None,
        seed: int = None
    ) -> List[str]:
        """
        Generate images using FLUX.1 via Replicate, with HuggingFace fallback.
        """
        # Try Replicate first
        if self.client and not self.use_free_fallback:
            try:
                return self._generate_replicate(prompt, mode, width, height, num_outputs, guidance_scale, num_inference_steps, seed)
            except Exception as e:
                error_str = str(e).lower()
                # Check for credit/billing errors
                if "402" in error_str or "credit" in error_str or "billing" in error_str or "insufficient" in error_str:
                    print("[FALLBACK] Replicate out of credits. Switching to local fallback.")
                    # We want to propagate this info to the UI if possible, or just fail gracefully with a clearer fallback.
                    # For now, let's trigger the fallback but maybe warn the user.
                    self.use_free_fallback = True
                else:
                    raise e
        
        # Fallback to HuggingFace free tier (or local if that fails)
        return self._generate_huggingface(prompt, width, height)
    
    def _generate_replicate(
        self, prompt: str, mode: str, width: int, height: int,
        num_outputs: int, guidance_scale: float, num_inference_steps: int, seed: int
    ) -> List[str]:
        """Generate via Replicate API."""
        model_id = self.MODELS.get(mode, self.MODELS["schnell"])
        
        input_params = {
            "prompt": prompt,
            "aspect_ratio": self._get_aspect_ratio(width, height),
            "output_format": "jpg",
            "output_quality": 95
        }
        
        if mode != "schnell":
            input_params["guidance"] = guidance_scale
            if num_inference_steps:
                input_params["num_inference_steps"] = num_inference_steps
        
        if seed is not None:
            input_params["seed"] = seed
        
        if mode == "pro":
            input_params["num_outputs"] = min(num_outputs, 4)
        
        output = self.client.run(model_id, input=input_params)
        
        if isinstance(output, list):
            return [str(url) for url in output]
        elif hasattr(output, '__iter__'):
            return [str(url) for url in output]
        else:
            return [str(output)]
    
    def _generate_huggingface(self, prompt: str, width: int, height: int) -> List[str]:
        """Generate via HuggingFace free inference API."""
        import io
        
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": min(width, 1024),  # HF free tier max
                    "height": min(height, 1024)
                }
            }
            
            # Try HuggingFace API
            try:
                response = requests.post(
                    self.HF_FLUX_URL,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 200:
                    # Save image and return path
                    os.makedirs("assets/studio/premium", exist_ok=True)
                    timestamp = int(time.time())
                    filepath = f"assets/studio/premium/hf_flux_{timestamp}.jpg"
                    
                    img = Image.open(io.BytesIO(response.content))
                    img.save(filepath, "JPEG", quality=95)
                    
                    return [filepath]  # Return local path instead of URL
            except Exception:
                pass

        # If we reach here, HF failed or no token. Use local fallback.
        return self._generate_local_fallback(prompt, width, height)
    
    def _generate_local_fallback(self, prompt: str, width: int, height: int) -> List[str]:
        """Generate a local placeholder/mock image when all APIs fail."""
        # Create a sophisticated placeholder
        os.makedirs("assets/studio/premium", exist_ok=True)
        timestamp = int(time.time())
        filepath = f"assets/studio/premium/local_{timestamp}.jpg"
        
        # Check if we have any stock images to use
        import glob
        stock_images = glob.glob("assets/stock/*.jpg") + glob.glob("assets/concepts/*.jpg")
        
        # Create a gradient placeholder with text overlay (Concept Card)
        img = Image.new('RGB', (width, height), (30, 35, 45))
        
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Gradient Background
        for i in range(height):
            r = int(20 + (i / height) * 20)
            g = int(25 + (i / height) * 30)
            b = int(40 + (i / height) * 40)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Grid Pattern
        for x in range(0, width, 100):
            for y in range(0, height, 100):
                 draw.rectangle([x, y, x+1, y+1], fill=(60, 60, 80))
        
        # Central Box
        margin_x = int(width * 0.1)
        margin_y = int(height * 0.3)
        draw.rectangle(
            [margin_x, margin_y, width - margin_x, height - margin_y],
            outline=(200, 180, 140), width=3
        )
        
        # Text
        try:
            # Try to load a font, otherwise default
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_text = ImageFont.truetype("arial.ttf", 30)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_title = ImageFont.load_default()
            font_text = font_title
            font_small = font_title
            
        # Draw Title
        draw.text((margin_x + 20, margin_y + 20), "OFFLINE MODE: CONCEPT", fill=(200, 180, 140), font=font_title)
        
        # Draw Prompt (wrapped)
        import textwrap
        wrapper = textwrap.TextWrapper(width=40)
        lines = wrapper.wrap(prompt)
        y_text = margin_y + 100
        for line in lines[:5]: # Max 5 lines
            draw.text((margin_x + 20, y_text), line, fill=(220, 220, 220), font=font_text)
            y_text += 40
            
        # Bottom warning
        draw.text((margin_x + 20, height - margin_y - 50), "⚠️ Replicate/HF API Key missing or out of credits.", fill=(255, 100, 100), font=font_small)
        
        img.save(filepath, "JPEG", quality=95)
        return [filepath]
    
    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Convert dimensions to aspect ratio string."""
        ratio = width / height
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 3/2) < 0.1:
            return "3:2"
        elif abs(ratio - 2/3) < 0.1:
            return "2:3"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        else:
            return "1:1"


# ============================================================================
# STYLE REFERENCE (Like Adobe Firefly)
# ============================================================================

class StyleReference:
    """
    Extracts style characteristics from a reference image
    and applies them to new generations.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except:
                pass
    
    def extract_style(self, image_path: str) -> str:
        """
        Analyzes an image and extracts its style characteristics
        as a prompt modifier.
        """
        if not self.model:
            return self._fallback_style_analysis()
        
        try:
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            import google.generativeai as genai
            
            # Upload image to Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode()
            }
            
            prompt = """Analyze this interior design image and describe its style in terms that can be used as a prompt for AI image generation.

Include:
- Color palette (specific colors, warmth/coolness)
- Lighting style (natural/artificial, soft/dramatic)
- Material textures (wood type, stone, fabric)
- Architectural elements
- Mood/atmosphere
- Design era/movement

Output ONLY a comma-separated list of style descriptors, maximum 50 words.
Example: warm walnut wood tones, soft diffused natural lighting, cream travertine marble, mid-century modern furniture, cozy sophisticated atmosphere"""

            response = self.model.generate_content([prompt, image_part])
            return response.text.strip()
            
        except Exception as e:
            return self._fallback_style_analysis()
    
    def _fallback_style_analysis(self) -> str:
        """Fallback generic style descriptors."""
        return "professional interior photography, balanced lighting, sophisticated color palette, high-end finishes"


# ============================================================================
# IMAGE UPSCALER (Like Midjourney 2x/4x)
# ============================================================================

class ImageUpscaler:
    """
    Upscales images using Real-ESRGAN via Replicate.
    Supports 2x and 4x scaling with subtle or creative modes.
    """
    
    # Real-ESRGAN model on Replicate
    MODEL_ID = "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa"
    
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        self.client = None
        
        if self.api_token:
            try:
                import replicate
                self.client = replicate.Client(api_token=self.api_token)
            except ImportError:
                pass
    
    def upscale(
        self, 
        image_path: str,
        scale: int = 2,
        face_enhance: bool = False
    ) -> str:
        """
        Upscale an image by 2x or 4x using Real-ESRGAN.
        
        Args:
            image_path: Path to input image
            scale: 2 or 4 for upscale factor
            face_enhance: Whether to enhance faces (GFPGAN)
            
        Returns:
            URL of upscaled image
        """
        if not self.client:
            raise ValueError("Replicate API token not configured")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        input_params = {
            "image": f"data:image/jpeg;base64,{image_data}",
            "scale": scale,
            "face_enhance": face_enhance
        }
        
        try:
            output = self.client.run(self.MODEL_ID, input=input_params)
            return str(output)
        except Exception as e:
            raise RuntimeError(f"Upscaling failed: {str(e)}")


# ============================================================================
# IMAGE VARIATIONS (Like Midjourney V button)
# ============================================================================

class ImageVariator:
    """
    Generates variations of an existing image using img2img techniques.
    """
    
    # FLUX.1 img2img model
    MODEL_ID = "black-forest-labs/flux-redux-schnell"
    
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        self.client = None
        
        if self.api_token:
            try:
                import replicate
                self.client = replicate.Client(api_token=self.api_token)
            except ImportError:
                pass
    
    def create_variations(
        self,
        image_path: str,
        prompt: str = None,
        num_variations: int = 4,
        variation_strength: float = 0.7
    ) -> List[str]:
        """
        Generate variations of an image.
        
        Args:
            image_path: Path to source image
            prompt: Optional prompt to guide variations
            num_variations: Number of variations (1-4)
            variation_strength: 0.0 (subtle) to 1.0 (dramatic)
            
        Returns:
            List of variation image URLs
        """
        if not self.client:
            raise ValueError("Replicate API token not configured")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        input_params = {
            "redux_image": f"data:image/jpeg;base64,{image_data}",
            "aspect_ratio": "1:1",
            "output_format": "jpg"
        }
        
        if prompt:
            input_params["prompt"] = prompt
        
        try:
            results = []
            for i in range(num_variations):
                # Add seed variation for each
                input_params["seed"] = int(time.time()) + i
                output = self.client.run(self.MODEL_ID, input=input_params)
                if isinstance(output, list):
                    results.extend([str(url) for url in output])
                else:
                    results.append(str(output))
            return results[:num_variations]
        except Exception as e:
            raise RuntimeError(f"Variation generation failed: {str(e)}")


# ============================================================================
# OUTPAINTING / EXPAND (Like Adobe Firefly Generative Expand)
# ============================================================================

class ImageExpander:
    """
    Extends images beyond their original boundaries using AI.
    """
    
    # FLUX.1 fill model for inpainting/outpainting
    MODEL_ID = "black-forest-labs/flux-fill-pro"
    
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        self.client = None
        
        if self.api_token:
            try:
                import replicate
                self.client = replicate.Client(api_token=self.api_token)
            except ImportError:
                pass
    
    def expand(
        self,
        image_path: str,
        direction: str = "all",  # "left", "right", "top", "bottom", "all"
        expansion_pixels: int = 256,
        prompt: str = None
    ) -> str:
        """
        Expand an image in the specified direction(s).
        
        Args:
            image_path: Path to source image
            direction: Direction to expand
            expansion_pixels: How many pixels to add
            prompt: Optional prompt to guide expansion
            
        Returns:
            URL of expanded image
        """
        if not self.client:
            # Fallback: Use PIL to create a simple expansion
            return self._fallback_expand(image_path, direction, expansion_pixels)
        
        try:
            # For now, use the fill model with a mask
            # This is a simplified implementation
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            input_params = {
                "image": f"data:image/jpeg;base64,{image_data}",
                "prompt": prompt or "continue the image seamlessly, matching style and content",
                "output_format": "jpg"
            }
            
            output = self.client.run(self.MODEL_ID, input=input_params)
            return str(output) if not isinstance(output, list) else str(output[0])
            
        except Exception as e:
            return self._fallback_expand(image_path, direction, expansion_pixels)
    
    def _fallback_expand(self, image_path: str, direction: str, pixels: int) -> str:
        """Fallback using PIL mirroring."""
        img = Image.open(image_path)
        w, h = img.size
        
        if direction == "all":
            new_w, new_h = w + pixels * 2, h + pixels * 2
            new_img = Image.new('RGB', (new_w, new_h), (30, 30, 40))
            new_img.paste(img, (pixels, pixels))
        elif direction == "right":
            new_img = Image.new('RGB', (w + pixels, h), (30, 30, 40))
            new_img.paste(img, (0, 0))
        elif direction == "left":
            new_img = Image.new('RGB', (w + pixels, h), (30, 30, 40))
            new_img.paste(img, (pixels, 0))
        elif direction == "bottom":
            new_img = Image.new('RGB', (w, h + pixels), (30, 30, 40))
            new_img.paste(img, (0, 0))
        else:  # top
            new_img = Image.new('RGB', (w, h + pixels), (30, 30, 40))
            new_img.paste(img, (0, pixels))
        
        # Save
        output_path = image_path.replace('.jpg', '_expanded.jpg').replace('.png', '_expanded.png')
        new_img.save(output_path, quality=95)
        return output_path


# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

class PremiumStudio:
    """
    Master orchestrator combining all premium studio features.
    """
    
    def __init__(self):
        self.prompt_enhancer = PromptEnhancer()
        self.flux_generator = FluxGenerator()
        self.style_reference = StyleReference()
        self.upscaler = ImageUpscaler()
        self.variator = ImageVariator()
        self.expander = ImageExpander()
        self.config = GenerationConfig()
    
    def generate(
        self,
        prompt: str,
        mode: str = "schnell",
        aspect_ratio: str = "square",
        style_preset: str = None,
        style_reference_path: str = None,
        enhance_prompt: bool = True,
        negative_prompt: str = None,
        seed: int = None,
        save_dir: str = "assets/studio/premium"
    ) -> Dict:
        """
        Full-featured image generation.
        
        Args:
            prompt: Base prompt
            mode: "schnell", "dev", or "pro"
            aspect_ratio: "square", "landscape_16_9", "portrait_9_16", etc.
            style_preset: One of the style preset keys
            style_reference_path: Path to style reference image
            enhance_prompt: Whether to AI-enhance the prompt
            negative_prompt: Things to avoid (appended)
            seed: Random seed for reproducibility
            save_dir: Directory to save generated images
            
        Returns:
            Dict with generation results
        """
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time())
        
        # 1. Get dimensions from aspect ratio
        aspect_map = {
            "square": self.config.ASPECT_SQUARE,
            "landscape_16_9": self.config.ASPECT_LANDSCAPE_16_9,
            "landscape_3_2": self.config.ASPECT_LANDSCAPE_3_2,
            "portrait_9_16": self.config.ASPECT_PORTRAIT_9_16,
            "portrait_2_3": self.config.ASPECT_PORTRAIT_2_3
        }
        width, height = aspect_map.get(aspect_ratio, self.config.ASPECT_SQUARE)
        
        # 2. Enhance prompt if requested
        final_prompt = prompt
        if enhance_prompt:
            final_prompt = self.prompt_enhancer.enhance(prompt, style_preset)
        elif style_preset and style_preset in self.config.STYLE_PRESETS:
            final_prompt = f"{prompt}, {self.config.STYLE_PRESETS[style_preset]}"
        
        # 3. Add style reference if provided
        if style_reference_path and os.path.exists(style_reference_path):
            style_description = self.style_reference.extract_style(style_reference_path)
            final_prompt = f"{final_prompt}, style: {style_description}"
        
        # 4. Add negative prompt
        if negative_prompt:
            final_prompt = f"{final_prompt}. Avoid: {negative_prompt}"
        
        # 5. Generate image
        try:
            urls = self.flux_generator.generate(
                prompt=final_prompt,
                mode=mode,
                width=width,
                height=height,
                seed=seed
            )
            
            # 6. Download and save image (or use local path if fallback)
            saved_paths = []
            for i, result in enumerate(urls):
                # Check if result is a URL or a local path
                if result.startswith('http://') or result.startswith('https://'):
                    # It's a URL - download it
                    response = requests.get(result, timeout=60)
                    if response.status_code == 200:
                        filename = f"premium_{timestamp}_{i}.jpg"
                        filepath = os.path.join(save_dir, filename)
                        
                        img = Image.open(BytesIO(response.content))
                        img.save(filepath, "JPEG", quality=95)
                        saved_paths.append(filepath)
                else:
                    # It's a local path from fallback - use directly
                    if os.path.exists(result):
                        saved_paths.append(result)
                    else:
                        # Path doesn't exist, something went wrong
                        saved_paths.append(result)
            
            return {
                "success": True,
                "mode": mode,
                "original_prompt": prompt,
                "enhanced_prompt": final_prompt,
                "images": saved_paths,
                "urls": urls,
                "dimensions": (width, height),
                "timestamp": timestamp
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_prompt": prompt,
                "enhanced_prompt": final_prompt
            }
    
    def create_variations(self, image_path: str, prompt: str = None, count: int = 4) -> Dict:
        """Generate variations of an image."""
        try:
            urls = self.variator.create_variations(image_path, prompt, count)
            return {"success": True, "variations": urls}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upscale_image(self, image_path: str, scale: int = 2) -> Dict:
        """Upscale an image."""
        try:
            url = self.upscaler.upscale(image_path, scale)
            return {"success": True, "upscaled_url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def expand_image(self, image_path: str, direction: str = "all", prompt: str = None) -> Dict:
        """Expand an image's boundaries."""
        try:
            result = self.expander.expand(image_path, direction, prompt=prompt)
            return {"success": True, "expanded": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    studio = PremiumStudio()
    
    # Test prompt enhancement
    enhancer = PromptEnhancer()
    enhanced = enhancer.enhance("modern living room")
    print(f"Enhanced prompt: {enhanced[:100]}...")
    
    print("\nPremium Studio initialized successfully!")
    print(f"FLUX Generator ready: {studio.flux_generator.client is not None}")
    print(f"Prompt Enhancer ready: {studio.prompt_enhancer.model is not None}")
