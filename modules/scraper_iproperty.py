import time
import os
import random
import urllib.parse
from datetime import datetime, timedelta
import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import modules.db_supabase as db

class IPropertyHunter:
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

    def _setup_driver(self):
        try:
            print(">>> INITIALIZING IPROPERTY HUNTER (Undetected Mode) <<<")
            
            # Force Kill any lingering chrome processes programmatically if possible
            # os.system("taskkill /f /im chrome.exe") 

            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-popup-blocking")
            
            # Use a random/unique profile to avoid locks from crashed sessions
            import uuid
            cwd = os.getcwd()
            profile_dir = os.path.join(cwd, f"chrome_profile_iproperty_{uuid.uuid4().hex[:8]}")
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
            
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.page_load_strategy = 'eager'
            
            # Remove use_subprocess=True as it can sometimes cause connectivity issues
            try:
                self.driver = uc.Chrome(options=options)
            except Exception as e:
                print(f"Standard Init failed, retrying with version_main=144... ({e})")
                # MUST Re-create options as they cannot be reused
                options = uc.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-popup-blocking")
                options.add_argument(f"--user-data-dir={profile_dir}")
                options.page_load_strategy = 'eager'
                
                self.driver = uc.Chrome(options=options, version_main=144)
            
            self.driver.set_page_load_timeout(60)
            
        except Exception as e:
            self._log(f"Driver Init Failed: {e}", "error")
            raise e

    def hunt_listings(self, query="balcony", location="kuala-lumpur", days_back=30, limit=20, user_id=None):
        if not self.driver:
            self._setup_driver()

        loc_slug = location.lower().replace(" ", "-") if location else "kuala-lumpur"
        encoded_query = urllib.parse.quote(query)
        processed_links = set()
        listings_found = 0
        
        # Pagination Loop (Increased limit to skip duplicates)
        for page_num in range(1, 50):
            if listings_found >= limit: break
            
            # 1. Navigate to Page X
            target_url = f"https://www.iproperty.com.my/sale/{loc_slug}/?q={encoded_query}&page={page_num}"
            self._log(f"Navigating to Page {page_num}: {target_url}", "info")
            try:
                pass 
            except: pass
            
            try:
                self.driver.get(target_url)
            except Exception as e:
                self._log(f"Page load timeout/warning: {e}. Attempting to proceed...", "warning")
                try: self.driver.execute_script("window.stop();")
                except: pass
            
            time.sleep(5) # Wait for Cloudflare/Loading
            
            # Check Cloudflare
            if "challenge" in self.driver.title.lower():
                self._log("Cloudflare challenge detected. Waiting 10s...", "warning")
                time.sleep(10)

            # 2. Find Cards
            card_selector = "div[da-id*='listing-card'], div[class*='listing-card-v2']"
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, card_selector))
                )
            except:
                print("No listings found on this page.")
                if page_num > 1: break # Stop if no results on subsequent pages
            
            items = self.driver.find_elements(By.CSS_SELECTOR, card_selector)
            print(f"DEBUG: Found {len(items)} items on page {page_num}")
            
            for item in items:
                if listings_found >= limit: break
                try:
                    # Capture Text for Date Analysis
                    full_text = item.text.lower()
                    
                    # 3. Date Filter (Heuristic)
                    # Look for "posted today", "1 day ago", "28 jan"
                    is_recent = True
                    # (Simple logic: If 'month' or 'year' ago, skip. If 'today'/'days', keep.)
                    if "month ago" in full_text or "year ago" in full_text: 
                        is_recent = False
                    
                    # 4. Extract Data
                    try:
                        title_el = item.find_element(By.CSS_SELECTOR, "h2 a, a[class*='title'], a[da-id*='title']")
                        title = title_el.text
                        link = title_el.get_attribute("href")
                    except:
                        # Fallback
                        try:
                            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                            title = "Property Listing"
                        except: continue

                    if link in processed_links: continue
                    processed_links.add(link)
                    
                    # Only skip if we are SURE it's old. Otherwise scrape it.
                    # if not is_recent: 
                    #     print(f"Skipping old listing: {title}")
                    #     continue

                    # Price
                    try: 
                        price_el = item.find_element(By.CSS_SELECTOR, "div[da-id='listing-card-v2-price'], .listing-price")
                        price = price_el.text
                    except: price = "N/A"
                    
                    # Agent Info
                    agent_name = "Unknown Agent"
                    agent_url = ""
                    phone = ""
                    
                    try:
                        # Strategy: Find any link containing '/property-agent/'
                        # This is the most reliable way to get the agent's identity
                        agent_links = item.find_elements(By.CSS_SELECTOR, "a[href*='/property-agent/']")
                        if agent_links:
                            agent_url = agent_links[0].get_attribute("href")
                            # Extract name from URL or Text
                            # URL format: .../property-agent/jesslyn-choo-900744
                            # Text might be empty if it's wrapping an image
                            if agent_links[0].text.strip():
                                agent_name = agent_links[0].text.strip()
                            else:
                                # Fallback: Parse URL slug
                                slug = agent_url.split("/property-agent/")[-1]
                                parts = slug.split("-")[:-1] 
                                agent_name = " ".join(parts).title()
                                
                            # DEEP EXTRACTION: Visit Agent Profile to get Phone
                            # Only do this if we don't have a phone yet
                            if agent_url and not phone:
                                try:
                                    # Open a new tab to not disrupt the main flow
                                    self.driver.execute_script("window.open('');")
                                    self.driver.switch_to.window(self.driver.window_handles[-1])
                                    self.driver.get(agent_url)
                                    time.sleep(2) # Short wait for profile load
                                    
                                    # Try to find phone in the profile page
                                    # Usually a big "show number" button or a link
                                    # For now, just look for "tel:" links or whatsapp
                                    profile_links = self.driver.find_elements(By.TAG_NAME, "a")
                                    for pl in profile_links:
                                        href = pl.get_attribute("href") or ""
                                        if "tel:" in href:
                                            phone = href.replace("tel:", "")
                                            break
                                        if "wa.me" in href:
                                            phone = href.split("/")[-1].split("?")[0]
                                            break
                                    
                                    # Check for website
                                    # ...

                                    self.driver.close()
                                    self.driver.switch_to.window(self.driver.window_handles[0])
                                except Exception as ex:
                                    # print(f"Deep Extract Failed: {ex}")
                                    try: 
                                        self.driver.close() 
                                        self.driver.switch_to.window(self.driver.window_handles[0])
                                    except: pass

                        else:
                            # Fallback to text search if no link found
                            lines = item.text.split("\n")
                            if len(lines) > 2:
                                agent_name = lines[-3] # Rough guess
                                
                        # Phone Link Hunting (WhatsApp / Tel)
                        # Check all links in card again
                        all_links = item.find_elements(By.TAG_NAME, "a")
                        for cl in all_links:
                            href = cl.get_attribute("href") or ""
                            if "wa.me" in href or "whatsapp" in href:
                                phone = href.split("/")[-1].split("?")[0]
                                break
                            if "tel:" in href:
                                phone = href.replace("tel:", "")
                                break
                                
                    except Exception as e:
                        # print(f"Agent Parse Error: {e}")
                        pass
                    
                    if agent_name == "Unknown Agent":
                         agent_name = "Agent (See Link)"

                    # 5. Store
                    context = f"Selling: {title} ({price})\nLink: {link}"
                    
                    # Use add_lead_v2 with proper kwargs
                    is_new = db.add_lead_v2(
                        name=agent_name, 
                        phone=phone, 
                        source="iProperty", 
                        bio=context, 
                        link=agent_url,
                        status="New",
                        user_id=user_id
                    )
                    
                    if is_new:
                        print(f"[NEW] {agent_name} | {price}")
                        try: st.toast(f"New Agent: {agent_name}", icon="✨")
                        except: pass
                        listings_found += 1
                    else:
                        print(f"[DUPE] {agent_name} (Skipped)")
                    
                except Exception as e:
                    print(f"Item Error: {e}")
                    continue
            
            # Scroll to bottom to trigger any lazy loads or just human behavior
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
        return listings_found

    def close(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
