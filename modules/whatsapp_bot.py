import pyautogui
import time
import pyperclip
import os
from modules.ai_engine import AIGhostwriter

class WhatsAppBot:
    def __init__(self):
        self.ai = AIGhostwriter()
        # Safety: Fail-safe if mouse hits corner
        pyautogui.FAILSAFE = True
        
    def open_app(self):
        """Opens WhatsApp Desktop App."""
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write('WhatsApp')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3) # Wait for app to load

    def find_and_call(self, lead_name):
        """Searches for a lead and clicks the call button."""
        print(f"Finding {lead_name}...")
        
        # 1. Search
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        pyautogui.write(lead_name)
        time.sleep(1.5)
        
        # 2. Select first result (Down Arrow + Enter)
        pyautogui.press('down')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(1)
        
        # 3. Find Call Button
        # We look for the phone icon on screen
        try:
            # We assume there is an asset 'assets/wa_call_icon.png'
            # If not, we just blindly click top right? No, safer to alert.
            icon_loc = pyautogui.locateOnScreen("assets/wa_call_icon.png", confidence=0.8)
            
            if icon_loc:
                print(f"Call Button Found at {icon_loc}")
                center = pyautogui.center(icon_loc)
                pyautogui.click(center)
                return True
            else:
                print("Call Button NOT found. Make sure screen is visible.")
                return False
                
        except Exception as e:
            print(f"Visual Error: {e}")
            # Fallback: Tab navigation? Risky.
            return False

    def generate_reply(self, incoming_text):
        """Generates a reply using the Business AI."""
        return self.ai.generate_content(incoming_text)
        
if __name__ == "__main__":
    bot = WhatsAppBot()
    # Test Run
    # bot.open_app()
    # bot.find_and_call("Test Lead")
