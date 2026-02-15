import pyautogui
import time
import os

class VisualBridge:
    def __init__(self):
        pyautogui.FAILSAFE = True

    def open_whatsapp(self):
        """Brings WhatsApp to focus."""
        print("Opening WhatsApp...")
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write('WhatsApp')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2) # Wait for load

    def call_contact(self, contact_name):
        """Searches and clicks call."""
        # 1. Focus Search
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # 2. Type Name
        pyautogui.write(contact_name)
        time.sleep(1.5)
        
        # 3. Select Contact (Down + Enter)
        pyautogui.press('down')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(1)
        
        # 4. Click Call Button (Top Right region usually)
        # Since looking for image is flaky without exact screenshots, 
        # we will ask the user to help OR try valid TAB sequences.
        # But for 'Visual' bot, we can try to find an image if provided.
        # Check if we have the asset.
        
        if os.path.exists("assets/wa_call_icon.png"):
             try:
                 loc = pyautogui.locateCenterOnScreen("assets/wa_call_icon.png", confidence=0.8)
                 if loc:
                     pyautogui.click(loc)
                     return "Calling defined contact."
             except:
                 pass
        
        # Fallback: Inform User
        print("\n>>> AUTOMATION HALTED: PLEASE CLICK THE CALL BUTTON MANUALLY <<<")
        return "Waiting for user to click call..."

    def end_call(self):
        # WhatsApp End Call hotkey? 
        # Usually not standard global. 
        # We might need to ask user to hang up or look for red button.
        print("\n>>> PLEASE HANG UP MANUALLY <<<")
