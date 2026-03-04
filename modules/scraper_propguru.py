import time
import random
import pickle
import os
import streamlit as st
from bs4 import BeautifulSoup
# import undetected_chromedriver as uc # Lazy loaded
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import modules.db_supabase as db

# --- SAFETY CONSTANTS ---
MIN_DELAY = 10
MAX_DELAY = 30

class PropGuruHunter:
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
            # Fallback safe print for Windows
            safe_msg = str(message).encode('ascii', 'replace').decode('ascii')
            print(f"[{level.upper()}] {safe_msg}")

    def _setup_driver(self, headless=True):
        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        if headless:
            options.add_argument("--headless=new")
            
        # FIX: Enforce version 144 matches system Chrome
        self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)

    def save_cookies(self):
        """Saves current session cookies."""
        import pickle
        try:
            cookies = self.driver.get_cookies()
            with open("propguru_cookies.pkl", "wb") as f:
                pickle.dump(cookies, f)
            print("Session Saved (Cookies).")
        except Exception as e:
            print(f"Cookie Save Error: {e}")

    def load_cookies(self):
        """Loads saved session cookies."""
        import pickle
        import os
        if not os.path.exists("propguru_cookies.pkl"): return False
        try:
            # Need to visit domain first
            self.driver.get("https://www.propertyguru.com.my/404") 
            with open("propguru_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try: self.driver.add_cookie(cookie)
                    except: pass
            print("Session Loaded.")
            return True
        except Exception as e:
            print(f"Cookie Load Error: {e}")
            return False

    def human_delay(self):
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    def _random_scroll(self):
        """Scrolls down the page to mimic human behavior."""
        total_height = int(self.driver.execute_script("return document.body.scrollHeight"))
        # Scroll in chunks
        for i in range(1, total_height, random.randint(400, 800)):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(random.uniform(0.1, 0.4))
        # Scroll back up a bit
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def construct_search_url(self, query, location, sort="date_desc"):
        import urllib.parse
        # Updated Location Mapping (2026)
        loc_map = {
            "kuala-lumpur": "58jok",
            "selangor": "45nk1",
            "penang": "5qvq6",
            "johor": "v2xvv"
        }
        
        region_code = loc_map.get(location.lower(), "58jok") # Default KL
        base_url = f"https://www.propertyguru.com.my/property-for-sale/in-{location.lower()}-{region_code}"
        
        if query:
            encoded_query = urllib.parse.quote(query)
            # The original construct_search_url also had a 'sort' parameter.
            # The provided edit only considers 'freetext'.
            # Let's stick to what the edit provides for the query part.
            return f"{base_url}?freetext={encoded_query}"
        
        return base_url

    def hunt_listings(self, query="Balcony", location="kuala-lumpur", limit=30, user_id=None):
        """
        Scrapes property listings for agent contacts.
        Autogenerates URL based on query/loc.
        """
        if not self.driver:
            self._setup_driver()

        listings_found = 0
        search_url = self.construct_search_url(query, location)
        print(f"Target URL: {search_url}")
        
        try:
            # Attempt Session Load First
            if self.load_cookies():
                 self.driver.get(search_url)
                 time.sleep(3)
            else:
                 self.driver.get(search_url)
                 
            # CLOUDFLARE CHECK (Initial)
            # This check is now integrated into the main loop for each page load
            
            listings_found = 0
            current_page = 1
            
            while listings_found < limit:
                # Construct Page URL (Page 1 is base, Page 2 is /2)
                if current_page > 1:
                    target_url = f"{search_url}/{current_page}"
                else:
                    target_url = search_url
                    
                self.driver.get(target_url)
                time.sleep(random.uniform(3, 5))
                
                # Check for Cloudflare/Access Denied
                # Check for Cloudflare/Access Denied
                if "Access denied" in self.driver.title or "Cloudflare" in self.driver.page_source:
                    self._log(">>> CLOUDFLARE DETECTED <<<", "error")
                    self._log("Please solve the CAPTCHA in the browser window manually.", "warning")
                    self._log("Waiting 30 seconds for you to solve it...", "info")
                    time.sleep(30)
                    if "propertyguru" in self.driver.title.lower():
                        self.save_cookies()
                
                # SCROLLING (Natural)
                self._random_scroll()
                
                # PARSING
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                
                # Updated Selectors (Jan 2026)
                cards = soup.select('div[da-id="parent-listing-card-v2-regular"]')
                
                if not cards:
                    # Save debug html if empty
                    with open("propguru_empty_debug.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    break
                    
                for card in cards:
                    if listings_found >= limit: break
                    
                    try:
                        # EXTRACTION
                        # Agent Name
                        # Selector: span[da-id="listing-card-v2-agent-name"]
                        agent_node = card.select_one('span[da-id="listing-card-v2-agent-name"]')
                        agent_name = agent_node.text.strip() if agent_node else "Unknown Agent"
                        
                        # Agent Link / Profile
                        # Selector: a[da-id="listing-card-v2-profile-cta"]
                        link_node = card.select_one('a[da-id="listing-card-v2-profile-cta"]')
                        link = link_node['href'] if link_node else ""
                        if link and not link.startswith("http"):
                            link = "https://www.propertyguru.com.my" + link
                            
                        # Title
                        # Selector: h3[da-id="listing-card-v2-title"]
                        title_node = card.select_one('h3[da-id="listing-card-v2-title"]')
                        title = title_node.text.strip() if title_node else "Property Listing"
                        
                        # Phone - Attempt to find in other attributes or assume N/A
                        phone = "N/A"
                        # Future: Click 'Contact' button to reveal phone
                        
                        # Price
                        # Selector: div[da-id="listing-card-v2-price"]
                        price_node = card.select_one('div[da-id="listing-card-v2-price"]')
                        price = price_node.text.strip() if price_node else "N/A"
                        
                        # Area
                        # Selector: div[da-id="listing-card-v2-area"]
                        area_node = card.select_one('div[da-id="listing-card-v2-area"]')
                        area = area_node.text.strip() if area_node else "N/A"
                        
                        # Save if we found something useful
                        # We save even without phone if we have a profile link, but here we prioritize phone/name
                        success = db.add_lead_v2(
                            name=agent_name,
                            phone=phone,
                            source="PropertyGuru",
                            bio=f"Listing: {title}\nLink: {link}",
                            profile_url=link,
                            price=price,
                            area=area,
                            status="New",
                            user_id=user_id
                        )
                        
                        if success:
                            listings_found += 1
                            self._log(f"Saved: {agent_name} | {price} | {area}", "info")
                            
                    except Exception as e:
                        self._log(f"Card Processing Error: {e}", "error") 
                
                # Next Page Logic
                current_page += 1
                self.human_delay()

        except Exception as e:
            print(f"CRITICAL HUNTER ERROR: {str(e).encode('utf-8', errors='ignore').decode('utf-8')}")
            import traceback
            traceback.print_exc()
        
        return listings_found

    def close(self):
        if self.driver:
            self.driver.quit()
