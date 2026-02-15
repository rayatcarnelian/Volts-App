import webbrowser
import time
import urllib.parse
import os
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

class WhatsAppSniper:
    def __init__(self):
        self.driver = None

    def send_manual(self, phone, message):
        """Safe Mode: Opens WhatsApp Web with pre-filled message"""
        try:
            # Clean phone
            phone = phone.replace("+", "").replace("-", "").strip()
            encoded_msg = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
            webbrowser.open(url)
            return True
        except Exception as e:
            st.error(f"WA Manual Error: {e}")
            return False

    def send_auto(self, phone_list, message, media_path=None, delay=30):
        """Risky Mode: Auto-sends using Selenium"""
        if not self.driver:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument("--user-data-dir=./wa_session") # Persist session
            try:
                self.driver = uc.Chrome(options=options, use_subprocess=True)
            except Exception:
                print("Falling back to pinned Chrome version 144...")
                # Re-create options
                options = uc.ChromeOptions()
                options.add_argument("--user-data-dir=./wa_session")
                self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)
            self.driver.get("https://web.whatsapp.com")
            st.warning("Please scan QR code if not logged in. Waiting 20s...")
            time.sleep(20)

        for phone in phone_list:
            try:
                phone = phone.replace("+", "").replace("-", "").strip()
                encoded_msg = urllib.parse.quote(message)
                self.driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}")
                
                # Wait for load
                time.sleep(10)
                
                # Click Send (This selector handles the enter key or button)
                # Using action chains or finding the send button is volatile in WA Web
                # Safest is sending ENTER key to the input box which should be focused
                
                # Attach Media if provided
                if media_path:
                    try:
                        # Paperclip button
                        clip = self.driver.find_element(By.CSS_SELECTOR, "span[data-icon='plus']")
                        clip.click()
                        time.sleep(1)
                        
                        # Input file. WhatsApp Web usually uses the same input for Photos & Videos
                        # Sometimes labeled as 'Photos & videos'
                        # We try to find the input that accepts images/videos
                        image_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                        image_input.send_keys(os.path.abspath(media_path))
                        time.sleep(5) # Videos take longer to preview/load
                        
                        # Send button (Green circle)
                        send_btn = self.driver.find_element(By.CSS_SELECTOR, "span[data-icon='send']")
                        send_btn.click()
                        time.sleep(3)
                        
                    except Exception as img_e:
                        st.warning(f"Could not attach media: {img_e}")

                action = self.driver.switch_to.active_element
                action.send_keys(Keys.ENTER)
                
                st.toast(f"Sent to {phone}", icon="✅")
                time.sleep(delay)
                
            except Exception as e:
                st.error(f"Failed to send to {phone}: {e}")

    def close(self):
        if self.driver:
            self.driver.quit()
