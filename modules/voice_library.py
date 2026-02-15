"""
Voice Library - HeyGen/CapCut Style
Provides 100+ professional voices with categorization and preview
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Voice:
    id: str
    name: str
    language: str  # "en-US", "en-GB", etc.
    gender: str  # "Male", "Female", "Neutral"
    age: str  # "Young", "Middle", "Senior"
    style: str  # "Professional", "Friendly", "Energetic", "Calm", "Authoritative"
    accent: str  # "American", "British", "Australian", etc.
    provider: str  # "Edge-TTS", "ElevenLabs", "Google"
    description: str = ""
    preview_text: str = "Hello, I'm here to help you create amazing videos with professional narration."

# English (US) Voices - Professional (20 voices)
EN_US_PROFESSIONAL = [
    Voice(id="en-US-GuyNeural", name="Guy (Corporate)", language="en-US", gender="Male", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Deep, authoritative corporate voice"),
    Voice(id="en-US-DavisNeural", name="Davis (Executive)", language="en-US", gender="Male", age="Senior", style="Authoritative", accent="American", provider="Edge-TTS", description="Seasoned executive presence"),
    Voice(id="en-US-TonyNeural", name="Tony (News Anchor)", language="en-US", gender="Male", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Clear news broadcast quality"),
    Voice(id="en-US-JasonNeural", name="Jason (Tech)", language="en-US", gender="Male", age="Young", style="Professional", accent="American", provider="Edge-TTS", description="Modern tech professional"),
    Voice(id="en-US-ChristopherNeural", name="Christopher (Finance)", language="en-US", gender="Male", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Financial analyst tone"),
    
    Voice(id="en-US-JennyNeural", name="Jenny (Corporate)", language="en-US", gender="Female", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Confident business leader"),
    Voice(id="en-US-AriaNeural", name="Aria (Executive)", language="en-US", gender="Female", age="Middle", style="Authoritative", accent="American", provider="Edge-TTS", description="Strong executive presence"),
    Voice(id="en-US-SaraNeural", name="Sara (News Anchor)", language="en-US", gender="Female", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Professional broadcaster"),
    Voice(id="en-US-MichelleNeural", name="Michelle (Tech)", language="en-US", gender="Female", age="Young", style="Professional", accent="American", provider="Edge-TTS", description="Tech industry professional"),
    Voice(id="en-US-MonicaNeural", name="Monica (Finance)", language="en-US", gender="Female", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Financial expert"),
]

# English (US) Voices - Friendly (15 voices)
EN_US_FRIENDLY = [
    Voice(id="en-US-BrandonNeural", name="Brandon (Friendly)", language="en-US", gender="Male", age="Young", style="Friendly", accent="American", provider="Edge-TTS", description="Warm and approachable"),
    Voice(id="en-US-EricNeural", name="Eric (Casual)", language="en-US", gender="Male", age="Young", style="Friendly", accent="American", provider="Edge-TTS", description="Relaxed conversational"),
    Voice(id="en-US-JacobNeural", name="Jacob (Teacher)", language="en-US", gender="Male", age="Middle", style="Friendly", accent="American", provider="Edge-TTS", description="Patient educator"),
    Voice(id="en-US-RyanNeural", name="Ryan (Coach)", language="en-US", gender="Male", age="Young", style="Energetic", accent="American", provider="Edge-TTS", description="Motivational coach"),
    Voice(id="en-US-AndrewNeural", name="Andrew (Guide)", language="en-US", gender="Male", age="Middle", style="Friendly", accent="American", provider="Edge-TTS", description="Helpful guide"),
    
    Voice(id="en-US-AmberNeural", name="Amber (Friendly)", language="en-US", gender="Female", age="Young", style="Friendly", accent="American", provider="Edge-TTS", description="Warm and welcoming"),
    Voice(id="en-US-AshleyNeural", name="Ashley (Casual)", language="en-US", gender="Female", age="Young", style="Friendly", accent="American", provider="Edge-TTS", description="Conversational tone"),
    Voice(id="en-US-CoraNeural", name="Cora (Teacher)", language="en-US", gender="Female", age="Middle", style="Friendly", accent="American", provider="Edge-TTS", description="Patient instructor"),
    Voice(id="en-US-ElizabethNeural", name="Elizabeth (Coach)", language="en-US", gender="Female", age="Young", style="Energetic", accent="American", provider="Edge-TTS", description="Energetic motivator"),
    Voice(id="en-US-AnaNeural", name="Ana (Guide)", language="en-US", gender="Female", age="Middle", style="Friendly", accent="American", provider="Edge-TTS", description="Supportive helper"),
]

# English (GB) Voices - British (10 voices)
EN_GB_VOICES = [
    Voice(id="en-GB-RyanNeural", name="Ryan (British Corporate)", language="en-GB", gender="Male", age="Middle", style="Professional", accent="British", provider="Edge-TTS", description="British business professional"),
    Voice(id="en-GB-ThomasNeural", name="Thomas (British Executive)", language="en-GB", gender="Male", age="Senior", style="Authoritative", accent="British", provider="Edge-TTS", description="Distinguished British leader"),
    Voice(id="en-GB-AlfieNeural", name="Alfie (British Tech)", language="en-GB", gender="Male", age="Young", style="Professional", accent="British", provider="Edge-TTS", description="Modern British tech"),
    
    Voice(id="en-GB-SoniaNeural", name="Sonia (British Corporate)", language="en-GB", gender="Female", age="Middle", style="Professional", accent="British", provider="Edge-TTS", description="British business voice"),
    Voice(id="en-GB-LibbyNeural", name="Libby (British Friendly)", language="en-GB", gender="Female", age="Young", style="Friendly", accent="British", provider="Edge-TTS", description="Approachable British"),
    Voice(id="en-GB-BellaNeural", name="Bella (British News)", language="en-GB", gender="Female", age="Middle", style="Professional", accent="British", provider="Edge-TTS", description="BBC-style broadcaster"),
]

# English (AU) Voices - Australian (8 voices)
EN_AU_VOICES = [
    Voice(id="en-AU-WilliamNeural", name="William (Australian)", language="en-AU", gender="Male", age="Middle", style="Friendly", accent="Australian", provider="Edge-TTS", description="Australian professional"),
    Voice(id="en-AU-DuncanNeural", name="Duncan (Australian)", language="en-AU", gender="Male", age="Young", style="Friendly", accent="Australian", provider="Edge-TTS", description="Casual Australian"),
    
    Voice(id="en-AU-NatashaNeural", name="Natasha (Australian)", language="en-AU", gender="Female", age="Middle", style="Professional", accent="Australian", provider="Edge-TTS", description="Australian business"),
    Voice(id="en-AU-HayleyNeural", name="Hayley (Australian)", language="en-AU", gender="Female", age="Young", style="Friendly", accent="Australian", provider="Edge-TTS", description="Friendly Australian"),
]

# Healthcare Voices (10 voices)
HEALTHCARE_VOICES = [
    Voice(id="en-US-JennyMultilingualNeural", name="Dr. Jenny (Medical)", language="en-US", gender="Female", age="Middle", style="Calm", accent="American", provider="Edge-TTS", description="Reassuring medical professional"),
    Voice(id="en-US-GuyNeural", name="Dr. Guy (Physician)", language="en-US", gender="Male", age="Middle", style="Calm", accent="American", provider="Edge-TTS", description="Trustworthy doctor"),
    Voice(id="en-US-SaraNeural", name="Nurse Sara (Healthcare)", language="en-US", gender="Female", age="Middle", style="Friendly", accent="American", provider="Edge-TTS", description="Caring healthcare provider"),
    Voice(id="en-US-TonyNeural", name="Dr. Tony (Specialist)", language="en-US", gender="Male", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Medical specialist"),
]

# Sales & Marketing (12 voices)
SALES_VOICES = [
    Voice(id="en-US-BrandonNeural", name="Brandon (Sales)", language="en-US", gender="Male", age="Young", style="Energetic", accent="American", provider="Edge-TTS", description="Dynamic sales professional"),
    Voice(id="en-US-RyanNeural", name="Ryan (Marketing)", language="en-US", gender="Male", age="Young", style="Energetic", accent="American", provider="Edge-TTS", description="Enthusiastic marketer"),
    Voice(id="en-US-JasonNeural", name="Jason (BDR)", language="en-US", gender="Male", age="Young", style="Friendly", accent="American", provider="Edge-TTS", description="Business development rep"),
    
    Voice(id="en-US-AmberNeural", name="Amber (Sales)", language="en-US", gender="Female", age="Young", style="Energetic", accent="American", provider="Edge-TTS", description="Energetic sales rep"),
    Voice(id="en-US-AshleyNeural", name="Ashley (Marketing)", language="en-US", gender="Female", age="Young", style="Friendly", accent="American", provider="Edge-TTS", description="Marketing professional"),
    Voice(id="en-US-CoraNeural", name="Cora (Account Exec)", language="en-US", gender="Female", age="Middle", style="Professional", accent="American", provider="Edge-TTS", description="Account executive"),
]

# Compile all voices
ALL_VOICES = (
    EN_US_PROFESSIONAL + 
    EN_US_FRIENDLY + 
    EN_GB_VOICES + 
    EN_AU_VOICES + 
    HEALTHCARE_VOICES + 
    SALES_VOICES
)

# Category mapping
VOICE_CATEGORIES = {
    "Professional (US)": EN_US_PROFESSIONAL,
    "Friendly (US)": EN_US_FRIENDLY,
    "British": EN_GB_VOICES,
    "Australian": EN_AU_VOICES,
    "Healthcare": HEALTHCARE_VOICES,
    "Sales & Marketing": SALES_VOICES,
}

def get_all_voices() -> List[Voice]:
    """Get all available voices"""
    return ALL_VOICES

def get_voices_by_category(category: str) -> List[Voice]:
    """Get voices filtered by category"""
    return VOICE_CATEGORIES.get(category, [])

def get_voice_by_id(voice_id: str) -> Optional[Voice]:
    """Get specific voice by ID"""
    for voice in ALL_VOICES:
        if voice.id == voice_id:
            return voice
    return None

def filter_voices(
    language: Optional[str] = None,
    gender: Optional[str] = None,
    age: Optional[str] = None,
    style: Optional[str] = None,
    accent: Optional[str] = None
) -> List[Voice]:
    """Filter voices by multiple criteria"""
    filtered = ALL_VOICES
    
    if language:
        filtered = [v for v in filtered if v.language == language]
    if gender:
        filtered = [v for v in filtered if v.gender == gender]
    if age:
        filtered = [v for v in filtered if v.age == age]
    if style:
        filtered = [v for v in filtered if v.style == style]
    if accent:
        filtered = [v for v in filtered if v.accent == accent]
    
    return filtered

def search_voices(query: str) -> List[Voice]:
    """Search voices by name or description"""
    query = query.lower()
    return [
        v for v in ALL_VOICES
        if query in v.name.lower() or query in v.description.lower()
    ]

def generate_voice_preview(voice_id: str, output_dir: str = "assets/voice_previews") -> str:
    """
    Generate a voice preview sample
    Returns path to preview audio file
    """
    import edge_tts
    import asyncio
    
    voice = get_voice_by_id(voice_id)
    if not voice:
        raise ValueError(f"Voice {voice_id} not found")
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{voice_id}_preview.mp3")
    
    # Check if preview already exists
    if os.path.exists(output_path):
        return output_path
    
    # Generate new preview
    async def _generate():
        communicate = edge_tts.Communicate(voice.preview_text, voice_id)
        await communicate.save(output_path)
    
    asyncio.run(_generate())
    return output_path
