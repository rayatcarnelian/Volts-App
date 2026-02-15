import os
import time
import pyautogui
import streamlit as st

class WinBridge:
    def __init__(self):
        # Fail-safe for pyautogui
        pyautogui.FAILSAFE = True

    def dial_number(self, phone_number):
        """
        Opens 'tel:' and uses pygetwindow to focus the app before pressing Enter.
        """
        if not phone_number: return False
        
        try:
            # 1. Launch App
            print(f"[DEBUG] Launching tel:{phone_number}")
            clean_num = phone_number.replace(" ", "").replace("-", "")
            os.startfile(f"tel:{clean_num}")
            
            # 2. Wait for Window (Smart Wait)
            target_window = None
            import pygetwindow as gw
            
            # Allow time for window to spawn
            attempts = 0
            while attempts < 10:
                time.sleep(0.5)
                # Look for common names
                windows = gw.getWindowsWithTitle('Phone Link') + gw.getWindowsWithTitle('Call')
                if windows:
                    target_window = windows[0]
                    break
                attempts += 1
                
            if target_window:
                try:
                    if target_window.isMinimized:
                        target_window.restore()
                    target_window.activate()
                    time.sleep(0.5) # Wait for focus
                except:
                    print("[WARN] Could not force focus, hoping for the best.")
            else:
                print("[WARN] 'Phone Link' window not detected. Sending 'Enter' blindly.")
            
            # 3. Confirm Dial
            pyautogui.press('enter')
            return True
        except Exception as e:
            st.error(f"Bridge Error: {e}")
            return False

    def check_audio_config(self):
        """
        Simple heuristic or instructions.
        """
        return "Ensure 'Phone Link' is using your Output Device."
