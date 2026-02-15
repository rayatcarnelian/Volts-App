
import asyncio
import os
import edge_tts
import nest_asyncio

# Apply nest_asyncio to allow re-entrant event loops for Streamlit compatibility
nest_asyncio.apply()

class FreeVoice:
    """
    Zero-Cost Neural Text-to-Speech using Mircosoft Edge's Online TTS service.
    No API Key required.
    """
    
    def __init__(self):
        # High quality English voices
        self.voices = {
            'female_1': 'en-US-AriaNeural',
            'female_2': 'en-US-JennyNeural',
            'male_1': 'en-US-GuyNeural',
            'male_2': 'en-US-ChristopherNeural'
        }
        self.output_dir = "assets/generated_voice"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def _generate_audio(self, text, voice, output_path):
        """Async generation wrapper"""
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
    def generate(self, text, voice_style='female_1', text_id="temp"):
        """
        Generates TTS audio and returns the file path.
        Synchronous wrapper for easy calling from synchronous imperative code.
        """
        voice = self.voices.get(voice_style, 'en-US-AriaNeural')
        # Use timestamp to avoid file locking issues on Windows
        import time
        filename = f"{text_id}_{int(time.time()*1000)}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Check if there's already an event loop running (Streamlit)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.run_until_complete(self._generate_audio(text, voice, filepath))
                        else:
                            loop.run_until_complete(self._generate_audio(text, voice, filepath))
                    except RuntimeError:
                        asyncio.run(self._generate_audio(text, voice, filepath))
                    
                    # If successful, break retry loop
                    return filepath
                except Exception as e:
                    print(f"TTS Attempt {attempt+1} failed: {e}")
                    import time
                    time.sleep(1)
            
            return None # Failed after retries
        except Exception as e:
            print(f"Error generating Free Voice: {e}")
            return None

if __name__ == "__main__":
    fv = FreeVoice()
    path = fv.generate("This is a zero cost neural voice test.", "female_1", "test_run")
    print(f"Generated at: {path}")
