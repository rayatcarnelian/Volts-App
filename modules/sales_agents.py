"""
SMART SALES AGENT TEAM
Autonomous AI agents that intelligently engage leads based on their profile and score.
Decides WHEN and HOW to reach out - not every lead gets the same treatment.
"""

import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class SalesAgentTeam:
    """
    A team of specialized AI sales agents that work autonomously.
    Each agent has a different role and engagement strategy.
    """
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            
    def analyze_lead_intent(self, lead_data):
        """
        Determines the best engagement strategy for a lead.
        Returns: action_plan with recommended approach.
        """
        if not self.model:
            return self._fallback_strategy(lead_data)
            
        prompt = f"""You are a luxury interior design sales strategist. Analyze this lead and recommend the BEST engagement approach.

LEAD PROFILE:
- Name: {lead_data.get('name', 'Unknown')}
- Score: {lead_data.get('total_score', 0)}/100
- Source: {lead_data.get('source', 'Unknown')}
- Bio/Headline: {lead_data.get('bio', 'No info')}
- Email: {lead_data.get('email', 'N/A')}
- Phone: {lead_data.get('phone', 'N/A')}

Based on this profile, provide a JSON response with:
{{
    "priority": "high/medium/low",
    "engagement_type": "personalized_video/design_concept/quick_message/skip",
    "channel": "whatsapp/email/linkedin/phone",
    "timing": "immediate/next_day/next_week",
    "personalization_angle": "what specific hook to use based on their profile",
    "design_style_suggestion": "if creating visual content, what style matches them",
    "opening_line": "suggested first message (1 sentence)"
}}

Return ONLY valid JSON, no explanation."""

        try:
            response = self.model.generate_content(prompt)
            # Parse JSON from response
            text = response.text.strip()
            # Handle markdown code blocks
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            return json.loads(text)
        except Exception:
            # Silently fallback to heuristic strategy
            return self._fallback_strategy(lead_data)
    
    def _fallback_strategy(self, lead_data):
        """Heuristic-based strategy when AI is unavailable."""
        score = lead_data.get('total_score', 0)
        
        if score >= 80:
            return {
                "priority": "high",
                "engagement_type": "personalized_video",
                "channel": "whatsapp",
                "timing": "immediate",
                "personalization_angle": "Reference their company/position",
                "design_style_suggestion": "Luxury commercial",
                "opening_line": "I've created something inspired by your work..."
            }
        elif score >= 50:
            return {
                "priority": "medium",
                "engagement_type": "design_concept",
                "channel": "email",
                "timing": "next_day",
                "personalization_angle": "Industry-specific value prop",
                "design_style_suggestion": "Modern professional",
                "opening_line": "Your profile caught my attention..."
            }
        else:
            return {
                "priority": "low",
                "engagement_type": "quick_message",
                "channel": "email",
                "timing": "next_week",
                "personalization_angle": "Generic value offer",
                "design_style_suggestion": "Standard portfolio",
                "opening_line": "I help professionals like you..."
            }
    
    def generate_outreach_script(self, lead_data, strategy):
        """Creates a personalized outreach script based on strategy."""
        if not self.model:
            return self._template_script(lead_data, strategy)
            
        prompt = f"""Write a sophisticated, personalized outreach message for:

LEAD: {lead_data.get('name')}
BIO: {lead_data.get('bio', 'No info')}
STRATEGY: {strategy.get('personalization_angle')}
CHANNEL: {strategy.get('channel')}

Rules:
- If WhatsApp: Keep under 50 words, casual but professional
- If Email: 3 short paragraphs max, include subject line
- If LinkedIn: 1-2 sentences, connection request style
- Reference something specific from their profile
- Do NOT be salesy or pushy
- Position as offering value, not asking for something
- Tone: Confident, sophisticated, intriguing

Return the message only, no explanation."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return self._template_script(lead_data, strategy)
    
    def _template_script(self, lead_data, strategy):
        """Fallback templates."""
        name = lead_data.get('name', 'there').split()[0]  # First name
        
        if strategy.get('channel') == 'whatsapp':
            return f"Hi {name}, I came across your profile and was impressed. I've put together a concept that might interest you - mind if I share?"
        elif strategy.get('channel') == 'email':
            return f"""Subject: A Design Vision for You

Hi {name},

I noticed your work and created something inspired by it.

Would you be open to a quick look?

Best regards"""
        else:
            return f"Hi {name}, your work caught my attention. Would love to connect and share some ideas."


class ContentGenerationAgent:
    """
    Agent responsible for generating personalized visual content.
    Works with FLUX, Minimax, and HeyGen APIs.
    """
    
    def __init__(self):
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        self.heygen_key = os.getenv("HEYGEN_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
    
    def generate_design_prompt(self, lead_data, style_hint=None):
        """
        Creates a hyper-personalized FLUX prompt based on lead profile.
        """
        if not self.model:
            return self._default_prompt(style_hint)
            
        prompt = f"""Generate a FLUX image generation prompt for a luxury interior design concept.

TARGET CLIENT:
- Name: {lead_data.get('name')}
- Industry/Role: {lead_data.get('bio', 'Unknown')}
- Source: {lead_data.get('source', 'Unknown')}
- Style Hint: {style_hint or 'Luxury modern'}

Create a detailed prompt that would generate an interior design image that would IMPRESS this specific client.
Consider their industry, likely taste, and what would resonate with them.

Rules:
- 1-2 sentences max
- Include: space type, materials, lighting, mood
- Style: photorealistic, 8K, editorial photography
- Do NOT include names or text in the image

Return ONLY the prompt, no explanation."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return self._default_prompt(style_hint)
    
    def _default_prompt(self, style_hint):
        """Fallback prompt."""
        style = style_hint or "luxury modern"
        return f"Ultra-luxury {style} interior, marble floors, gold accents, floor-to-ceiling windows with city view, editorial photography, 8K, photorealistic, dramatic lighting"
    
    def generate_image(self, prompt, lead_id=None, save_dir="assets/studio/"):
        """
        Generates an image using FLUX via Replicate.
        """
        if not self.replicate_token:
            return None, "Replicate API token missing"
            
        import replicate
        import requests
        
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": f"interior design photography, {prompt}",
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "output_quality": 90
                }
            )
            
            image_url = str(output)
            
            # Download and save
            timestamp = int(time.time())
            filename = f"concept_{lead_id or 'gen'}_{timestamp}.jpg"
            filepath = os.path.join(save_dir, filename)
            
            img_data = requests.get(image_url).content
            with open(filepath, 'wb') as f:
                f.write(img_data)
                
            return filepath, None
            
        except Exception as e:
            return None, str(e)
    
    def animate_to_video(self, image_path, motion_prompt=None, save_dir="assets/studio/videos/"):
        """
        Animates a static image into a video using Minimax.
        """
        if not self.replicate_token:
            return None, "Replicate API token missing"
            
        import replicate
        import requests
        
        os.makedirs(save_dir, exist_ok=True)
        
        # Default cinematic motion
        if not motion_prompt:
            motion_prompt = "Slow dolly forward through the space, revealing luxury details, cinematic lighting"
        
        try:
            output = replicate.run(
                "minimax/video-01",
                input={
                    "first_frame_image": open(image_path, "rb"),
                    "prompt": motion_prompt,
                    "prompt_optimizer": True
                }
            )
            
            video_url = str(output)
            
            timestamp = int(time.time())
            filename = f"animation_{timestamp}.mp4"
            filepath = os.path.join(save_dir, filename)
            
            with requests.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
            return filepath, None
            
        except Exception as e:
            return None, str(e)


class VoiceAgent:
    """
    Agent responsible for voice synthesis and cloning.
    Uses ElevenLabs for high-quality voice output.
    """
    
    def __init__(self):
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default Rachel
        
    def generate_voiceover(self, text, output_path="temp_voice.mp3"):
        """
        Generates a voiceover using ElevenLabs API.
        """
        if not self.elevenlabs_key:
            # Fallback to Edge-TTS
            return self._fallback_tts(text, output_path)
            
        import requests
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            return output_path, None
            
        except Exception as e:
            return self._fallback_tts(text, output_path)
    
    def _fallback_tts(self, text, output_path):
        """Fallback to Edge-TTS if ElevenLabs unavailable."""
        import asyncio
        import edge_tts
        
        async def _generate():
            communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
            await communicate.save(output_path)
            
        try:
            asyncio.run(_generate())
            return output_path, None
        except Exception as e:
            return None, str(e)


class AutonomousOrchestrator:
    """
    Master orchestrator that runs the autonomous content factory.
    Processes leads, decides strategies, and queues content generation.
    """
    
    def __init__(self):
        self.sales_team = SalesAgentTeam()
        self.content_agent = ContentGenerationAgent()
        self.voice_agent = VoiceAgent()
        
    def process_high_value_leads(self, leads_df, min_score=70, limit=10):
        """
        Processes high-value leads and generates personalized content.
        Returns a report of actions taken.
        """
        import modules.database as db
        
        results = []
        
        # Filter to high-value leads without content
        high_value = leads_df[leads_df['total_score'] >= min_score].head(limit)
        
        for idx, lead in high_value.iterrows():
            lead_data = lead.to_dict()
            
            # 1. Analyze and get strategy
            strategy = self.sales_team.analyze_lead_intent(lead_data)
            
            # 2. Decide action based on strategy
            action_result = {
                "lead_id": lead_data.get('id'),
                "name": lead_data.get('name'),
                "score": lead_data.get('total_score'),
                "strategy": strategy,
                "content_created": []
            }
            
            # 3. Generate content based on engagement type
            if strategy.get('engagement_type') == 'personalized_video':
                # Generate image + video
                prompt = self.content_agent.generate_design_prompt(lead_data, strategy.get('design_style_suggestion'))
                img_path, err = self.content_agent.generate_image(prompt, lead_data.get('id'))
                
                if img_path:
                    action_result['content_created'].append({"type": "image", "path": img_path})
                    
                    # Animate to video
                    vid_path, _ = self.content_agent.animate_to_video(img_path)
                    if vid_path:
                        action_result['content_created'].append({"type": "video", "path": vid_path})
                        
            elif strategy.get('engagement_type') == 'design_concept':
                # Generate image only
                prompt = self.content_agent.generate_design_prompt(lead_data, strategy.get('design_style_suggestion'))
                img_path, _ = self.content_agent.generate_image(prompt, lead_data.get('id'))
                
                if img_path:
                    action_result['content_created'].append({"type": "image", "path": img_path})
            
            # 4. Generate outreach script
            script = self.sales_team.generate_outreach_script(lead_data, strategy)
            action_result['outreach_script'] = script
            
            results.append(action_result)
            
        return results
    
    def get_daily_priority_queue(self, leads_df):
        """
        Creates a prioritized queue of leads for daily outreach.
        """
        queue = []
        
        for idx, lead in leads_df.iterrows():
            lead_data = lead.to_dict()
            strategy = self.sales_team.analyze_lead_intent(lead_data)
            
            if strategy.get('priority') in ['high', 'medium']:
                queue.append({
                    "lead": lead_data,
                    "strategy": strategy,
                    "priority_score": 100 if strategy.get('priority') == 'high' else 50
                })
        
        # Sort by priority
        queue.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return queue
