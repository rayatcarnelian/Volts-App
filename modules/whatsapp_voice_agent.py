import time
import sys
import os

# Add parent dir to path to find 'modules'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import speech_recognition as sr
import pygame
from modules.visual_bridge import VisualBridge
from modules.ai_engine import AIGhostwriter
from modules.free_voice import FreeVoice

class WhatsAppVoiceAgent:
    def __init__(self):
        self.bridge = VisualBridge()
        self.ai = AIGhostwriter()
        self.tts = FreeVoice()
        self.recognizer = sr.Recognizer()
        # OPTIMIZATION: Reduce pause threshold for faster response (default 0.8)
        self.recognizer.pause_threshold = 0.5
        self.recognizer.energy_threshold = 300 # Adjust accordingly
        
        # Initialize Audio
        pygame.mixer.init()

    def speak(self, text):
        """Plays audio via PC Speakers."""
        print(f"AI: {text}")
        # Use simple female voice for speed
        audio_path = self.tts.generate(text, voice_style='female_1')
        if audio_path:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

    def listen(self):
        """Listens via PC Mic."""
        with sr.Microphone() as source:
            print("Listening...")
            # Optional: Dynamic adjustment
            # self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Fast timeout. Phrase limit ensures we don't listen forever.
                audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio)
                print(f"Heard: {text}")
                return text
            except:
                return None

    def start_session(self, contact_name):
        # 1. Open WA
        self.bridge.open_whatsapp()
        
        # 2. Select Contact
        self.bridge.call_contact(contact_name)
        
        # 3. Wait for Connection (User verification)
        self.speak(f"I have selected {contact_name}. Please hit the call button.")
        
        print(">>> AI IS READY. START SPEAKING WHEN CALL CONNECTS <<<")
        # Give user 5 seconds to click call and pick up
        time.sleep(5) 
         
        # 4. Intro
        intro = "Hello, this is Volts Design. Am I speaking with the decision maker?"
        self.speak(intro)
        
        # 5. Loop
        active = True
        silence_count = 0
        
        # SALES PERSONA PROMPT
        base_instruction = (
            "You are a Top-Tier Sales Consultant for Volts Design (Luxury Interior Design). "
            "Your goal is to book a consultation or close the deal. "
            "Be friendly, confident, and professional. "
            "CRITICAL: Keep your response under 2 sentences. Be fast."
        )
        
        while active:
            # Update AI Prompt context to be a "Closer"
            # (Handled by AIGhostwriter internally reading business_profile.txt)
            
            user_text = self.listen()
            
            if user_text:
                silence_count = 0
                
                # Logic: Is user saying goodbye?
                if "bye" in user_text.lower():
                    self.speak("Goodbye, looking forward to working with you.")
                    active = False
                    break
                    
                # Generate Closing Reply
                full_prompt = f"{base_instruction}\nProspect said: '{user_text}'. Reply:"
                reply = self.ai.generate_content(full_prompt).replace("*", "")
                self.speak(reply)
            
            else:
                silence_count += 1
                if silence_count > 6:
                    print("Silence...")

        print("Session Ended.")

import sys

if __name__ == "__main__":
    agent = WhatsAppVoiceAgent()
    
    # Check if name passed via command line
    if len(sys.argv) > 1:
        target = " ".join(sys.argv[1:])
        # Clean up quotes if passed by shell
        target = target.replace('"', '').replace("'", "").strip()
        print(f"received Command: Call {target}")
    else:
        target = input("Enter Contact Name (exactly as saved in Phone): ")
        
    agent.start_session(target)
