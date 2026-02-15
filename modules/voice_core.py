import speech_recognition as sr
import edge_tts
import asyncio
import os
import pygame
import time
import sounddevice as sd
import numpy as np
from modules.ai_engine import AIGhostwriter

class NativeEar:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        # Adjust for ambient noise
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen(self, timeout=5):
        """Listens for a phrase."""
        try:
            with self.mic as source:
                print("Listening...")
                # We use a short timeout to keep the loop snappy
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None # Detected sound but couldn't parse
        except Exception as e:
            print(f"Ear Error: {e}")
            return None

class NativeMouth:
    def __init__(self):
        pygame.mixer.init()
        self.voice_map = {
            "Agent Smith (Male)": "en-US-ChristopherNeural",
            "Sarah (Female)": "en-US-AriaNeural",
            "Jarvis (Robot)": "en-US-EricNeural",
            "British Butler": "en-GB-RyanNeural",
            "Australian Guide": "en-AU-NatashaNeural"
        }
        self.current_voice = "en-US-ChristopherNeural"

    def set_voice(self, voice_name_key):
        if voice_name_key in self.voice_map:
            self.current_voice = self.voice_map[voice_name_key]

    async def speak(self, text):
        """Generates and plays TTS."""
        if not text: return
        
        output_file = "temp_voice.mp3"
        try:
            communicate = edge_tts.Communicate(text, self.current_voice)
            await communicate.save(output_file)
            
            # Play
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            # Cleanup
            pygame.mixer.music.unload()
            # os.remove(output_file) # Optional, keep for debug for now
            return True
        except Exception as e:
            print(f"Mouth Error: {e}")
            return False

class SalesBrain:
    def __init__(self):
        self.ai = AIGhostwriter()
        self.persona = """
        You are an AI Sales Assistant calling on behalf of 'Volts', an interior design tech company.
        Your goal is to book a demo. 
        Keep responses SHORT (1-2 sentences max). 
        Speak naturally.
        If they say hello, introduce yourself.
        If they ask about price, suggest a demo.
        """
        self.knowledge_base = ""

    def load_knowledge(self, text):
        self.knowledge_base = text

    def think(self, user_input, history):
        prompt = f"""
        {self.persona}
        KNOWLEDGE BASE: {self.knowledge_base}
        
        CONVERSATION HISTORY:
        {history}
        
        PROSPECT SAID: "{user_input}"
        
        YOUR RESPONSE (Text only, no emojis, maintain conversation flow):
        """
        response = self.ai.generate_content(prompt)
        return response.replace("*", "").replace('"', '').strip()
