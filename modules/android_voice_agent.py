import time
import speech_recognition as sr
import pygame
from modules.android_bridge import AndroidBridge
from modules.ai_engine import AIGhostwriter
from modules.free_voice import FreeVoice

class TitanAndroidAgent:
    def __init__(self):
        self.bridge = AndroidBridge()
        self.ai = AIGhostwriter()
        self.tts = FreeVoice()
        self.recognizer = sr.Recognizer()
        self.mic_index = None # Default
        
        # Initialize Audio Player
        pygame.mixer.init()

    def speak(self, text):
        """Generates and plays audio via PC speakers."""
        print(f"AI: {text}")
        audio_path = self.tts.generate(text, voice_style='female_1')
        if audio_path:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

    def listen(self):
        """Listens via PC Mic for User/Client voice."""
        with sr.Microphone() as source:
            print("Listening...")
            # Adjust for ambient noise once at start? Or every time?
            # self.recognizer.adjust_for_ambient_noise(source) 
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                print(f"Heard: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except Exception as e:
                print(f"Mic Error: {e}")
                return None

    def start_call(self, phone_number):
        # 1. Connect
        ok, msg = self.bridge.connect()
        if not ok:
            print(f"Bridge Error: {msg}")
            return

        # 2. Dial
        print(f"Dialing {phone_number}...")
        self.bridge.dial(phone_number)
        
        print(">>> PLEASE TURN ON SPEAKERPHONE ON ANDROID <<<")
        self.speak("Hello. I am connecting to the network.") # Test Audio

        # 3. Conversation Loop
        conversation_active = True
        silence_count = 0
        
        while conversation_active:
            user_input = self.listen()
            
            if user_input:
                silence_count = 0
                
                # Check for exit words
                if "bye" in user_input.lower() or "stop" in user_input.lower():
                    self.speak("Goodbye!")
                    conversation_active = False
                    break
                    
                # Generate Reply
                reply = self.ai.generate_content(f"The user said: {user_input}. Reply efficiently.")
                self.speak(reply)
            else:
                silence_count += 1
                if silence_count > 4:
                    print("Silence...")
                    # Optional: Break if too long?
        
        # 4. End
        self.bridge.end_call()
        print("Call Ended.")

if __name__ == "__main__":
    agent = TitanAndroidAgent()
    target = input("Enter number to call (e.g. 0123456789): ")
    agent.start_call(target)
