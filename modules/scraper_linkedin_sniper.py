import time
import random
import re
from bs4 import BeautifulSoup
import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import modules.db_supabase as db
import sys

# --- ENCODING FIX FOR WINDOWS ---
if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

class LinkedInSniper:
    def __init__(self):
        self.driver = None

    def _log(self, message, level="info"):
        """Helper to log to Streamlit or Console."""
        try:
            import streamlit as st
            if level == "info":
                try: st.toast(message, icon="ℹ️")
                except: print(f"[INFO] {message}")
            elif level == "warning":
                try: st.warning(message)
                except: print(f"[WARN] {message}")
            elif level == "error":
                try: st.error(message)
                except: print(f"[ERROR] {message}")
        except:
            print(f"[{level.upper()}] {message}")

    def _setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--no-first-run")
        # FIX: Enforce version 144 matches system Chrome
        self.driver = uc.Chrome(options=options, version_main=144)
        self.driver.set_window_size(1280, 800)

    def human_delay(self):
        # Reduced delay for speed (Risk: Higher ban chance, but User requested speed)
        time.sleep(random.uniform(2, 5))

    def check_login(self):
        """Checks if logged in, otherwise waits for user."""
        if not self.driver:
            self._setup_driver()
            
        self.driver.get("https://www.linkedin.com/feed/")
        self.human_delay()
        
        if "login" in self.driver.current_url or "signup" in self.driver.current_url:
            print("[ALERT] Not logged in! Please log in manually in the opened browser window.")
            # Wait for user to login
            while "feed" not in self.driver.current_url:
                time.sleep(2)
                print("Waiting for login...", end="\r")
            print("\n[SUCCESS] Login detected! Proceeding...")

    def scrape_profile_details(self, profile_url):
        """
        Visits profile and extracts:
        1. Follower Count / Connections
        2. About / Bio
        3. Contact Info (Email/Phone)
        """
        self.driver.get(profile_url)
        # Use a shorter explicit wait instead of long sleep if page loads fast
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except: pass
        self.human_delay()
        
        # DEBUG: Check where we are
        print(f"Visiting: {self.driver.title}")
        if "authwall" in self.driver.current_url or "login" in self.driver.current_url:
             print("⚠️  Redirected to Authwall! Login might be invalid.")
             self._log("LinkedIn blocked the view (Authwall). Please re-login manually in the browser.", "error")
             return None, None, None, None
        
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        # --- 1. Follower / Connections ---
        connections = "N/A"
        try:
             # Look for the top card list of items (usually where location and connections are)
             # Varies, but often ul class='pv-top-card--list'
             top_card_list = soup.select("ul.pv-top-card--list > li")
             for li in top_card_list:
                 text = li.get_text().strip()
                 if "connections" in text or "followers" in text:
                     connections = text.replace("\n", " ").strip()
                     break
        except: pass
        
        # --- 2. Location (Update if better) ---
        location = "N/A"
        try:
            # Often the first item in the list or separate header
             loc_node = soup.select_one("div.pv-text-details__left-panel span.text-body-small")
             if loc_node:
                 location = loc_node.get_text().strip()
        except: pass
        
        # --- 3. About / Bio ---
        about_text = "N/A"
        try:
            # Main About section
            about_section = soup.select_one("div#about") 
            if about_section:
                # The content is usually in the sibling or deeper details
                # Safe bet: get the text of the container that follows it or parent
                parent = about_section.find_parent("section")
                if parent:
                     # Remove the "About" header text to just get the body
                     about_text = parent.get_text().replace("About", "").strip()
        except: pass

        # --- 4. Contact Info Extraction ---
        email = None
        phone = None
        
        try:
            # 1. Click "Contact Info" (The Overlay)
            contact_btn = None
            try:
                # Wait for button to be clickable
                contact_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "top-card-text-details-contact-info"))
                )
            except:
                try: 
                    contact_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[id*='contact-info']"))
                    )
                except:
                    pass
            
            if contact_btn:
                contact_btn.click()
                
                # Wait for modal content instead of hard sleep
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] section.pv-contact-info__contact-type"))
                    )
                except: 
                    time.sleep(2) # Fallback
                
                # Parse the overlay
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                
                # Regex fallback on the whole overlay text
                overlay = soup.select_one("div[role='dialog']") or soup.select_one("div#artdeco-modal-outlet")
                if overlay:
                    text = overlay.text
                    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
                    if email_match:
                        email = email_match.group(0)
                        
                    phone_match = re.search(r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}', text)
                    if phone_match:
                        phone = phone_match.group(0)
                
                # Close overlay
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
                    close_btn.click()
                except:
                    action = self.driver.find_element(By.TAG_NAME, 'body')
                    action.send_keys(Keys.ESCAPE)
                    
        except Exception as e:
            print(f"Extraction Error (Contact Info): {e}")

        # Fallback check for email in bio/about
        if not email:
            # Brute force regex on collected about text or whole page
            email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', about_text)
            if email_match:
                email = email_match.group(0)
        
        return email, phone, connections, about_text, location

    def enrich_leads(self, limit=5):
        """Main method to process X-Ray leads."""
        
        # Get pending leads
        conn = db.get_connection()
        query = """
            SELECT l.id, l.name, lp.profile_url 
            FROM leads l
            JOIN linkedin_profiles lp ON l.id = lp.lead_id
            WHERE l.source = 'LinkedIn X-Ray' AND l.master_status = 'New'
            LIMIT ?
        """
        leads = conn.execute(query, (limit,)).fetchall()
        conn.close()
        
        if not leads:
            print("No new LinkedIn X-Ray leads to enrich.")
            return 0
            
        self.check_login()
        
        enriched_count = 0
        for lead in leads:
            print(f"Sniper Visiting: {lead['name']}...")
            
            # Scrape extended details + contact info
            email, phone, connections, about, location = self.scrape_profile_details(lead['profile_url'])
            
            # Save Contact Info
            if email or phone:
                print(f"[*] Contact Found: {email} | {phone}")
                db.update_lead_contact(lead['id'], email, phone)
            
            # Save Profile Details (Connections, Bio, Location)
            # Only if we found something useful
            if connections != "N/A" or about != "N/A":
                print(f"[+] Profile Data: {connections} | Bio Length: {len(about) if about else 0}")
                db.update_linkedin_details(lead['id'], connections, about, location)
                
            enriched_count += 1
            self._log(f"Scraped: {lead['name']}", "info")
                
            self.human_delay()
            
        return enriched_count

    def close(self):
        if self.driver:
            self.driver.quit()
