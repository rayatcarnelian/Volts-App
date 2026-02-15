import time
import random
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MapsHunter:
    def __init__(self, browser_type="Edge"):
        self.driver = None
        self.browser_type = browser_type

    def _log(self, message, level="info"):
        """Helper to log to Streamlit or Console."""
        try:
            import streamlit as st
            # Check if running in Streamlit context
            # A simple heuristic is checking if we can access the session state or if no warning is thrown
            # But the warnings appearing in the log confirm it's tricky.
            # Best way: Check runtime.
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
        import os
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options as EdgeOptions
        import undetected_chromedriver as uc
        
        # Helper to launch Edge
        def launch_edge():
            self._log("Initializing Engine (Edge)...", "info")
            options = EdgeOptions()
            options.add_argument("--guest")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--log-level=3")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-allow-origins=*")
            # Cloud Compatibility
            options.add_argument("--headless=new")
            return webdriver.Edge(options=options)

        # Helper to launch Chrome
        def launch_chrome():
            self._log("Initializing Engine (Chrome)...", "info")
            options = uc.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # Cloud Compatibility
            options.add_argument("--headless=new")
            # Cleanup patcher
            patcher_path = os.path.join(os.environ.get('APPDATA'), 'undetected_chromedriver', 'undetected_chromedriver.exe')
            if os.path.exists(patcher_path):
                try: os.remove(patcher_path)
                except: pass
            try:
                return uc.Chrome(options=options, use_subprocess=True)
            except Exception:
                print("Falling back to pinned Chrome version 144...")
                # Re-create options
                options = uc.ChromeOptions()
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless=new")
                return uc.Chrome(options=options, use_subprocess=True, version_main=144)

        try:
            if self.browser_type == "Chrome":
                try:
                    self.driver = launch_chrome()
                    return
                except:
                    self._log("Chrome failed. Falling back to Edge.", "warning")
            
            # Default or Fallback to Edge
            self.driver = launch_edge()
            return

        except Exception as e:
            # Final Hail Mary: Try Chrome if Edge failed and wasn't tried yet
            if self.browser_type != "Chrome":
                try:
                    self.driver = launch_chrome()
                    return
                except: pass
            
            self._log(f"ALL DRIVERS FAILED. Critical Error: {e}", "error")
            raise e

    def scan(self, keyword, limit=50):
        leads = []
        try:
            if not self.driver:
                self._setup_driver()
                
            self.driver.get("https://www.google.com/maps")
            
            wait = WebDriverWait(self.driver, 20)
            
            # Check for Consent Modal (common in some regions)
            try:
                consent_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Accept all') or contains(text(), 'Accept all')]"))
                )
                consent_button.click()
                time.sleep(2)
            except:
                pass

            # Robust Search Box Finding
            search_box = None
            selectors = [
                (By.ID, "searchboxinput"),
                (By.NAME, "q"),
                (By.CSS_SELECTOR, "input#searchboxinput"),
                (By.XPATH, "//input[@id='searchboxinput']"),
            ]

            for by, val in selectors:
                try:
                    search_box = wait.until(EC.element_to_be_clickable((by, val)))
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                self._log("Failed to locate Google Maps search bar. Saving debug screenshot...", "error")
                try:
                    self.driver.save_screenshot("maps_debug_error.png")
                    st.image("maps_debug_error.png") # Image still needs st, wrap it?
                except: pass
                return []

            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.ENTER)
            
            # Wait for results to load
            self._log(f"Searching for '{keyword}'...", "info")
            time.sleep(3) 

            # Smart Wait for Results
            try:
                # Wait for at least one result link
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/maps/place']")))
            except:
                self._log("Slow network or no results found yet...", "warning")

            # Scroll Logic (Smart Scroll)
            self._log(f"Loading results (Target: {limit})...", "info")
            feed = None
            try:
                feed = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            except:
                pass

            # Dynamic Scroll Loop
            unique_links = {} # Map href -> element
            attempts = 0
            stuck_count = 0
            last_count = 0
            
            # We scroll until we have enough unique links OR give up
            while len(unique_links) < limit and attempts < limit: 
                # Scroll action
                try:
                    if feed:
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    else:
                        search_box.send_keys(Keys.PAGE_DOWN)
                        search_box.send_keys(Keys.PAGE_DOWN)
                    time.sleep(2) # Allow load
                except:
                    pass
                
                # Collect currently visible links
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place']")
                for l in links:
                    h = l.get_attribute("href")
                    # Basic normalization to avoid session-based dupes
                    if h:
                        clean_h = h.split('?')[0] # Remove query params for uniqueness check
                        if clean_h not in unique_links:
                            unique_links[clean_h] = l
                
                count = len(unique_links)
                if count == last_count:
                    stuck_count += 1
                    # If stuck, try to wiggle or zoom? Just wait longer.
                    if stuck_count > 2:
                        try: 
                            search_box.send_keys(Keys.PAGE_DOWN)
                            time.sleep(1)
                        except: pass
                else:
                    stuck_count = 0
                    
                last_count = count
                
                if count >= limit:
                    break
                    
                attempts += 1
                self._log(f"Scrolling... Found {count}/{limit} unique targets...", "info")
            
            # Convert back to list
            final_links = list(unique_links.values())[:limit]
            
            self._log(f"Found {len(final_links)} unique targets. Extracting details...", "info")
            
            try:
                import streamlit as st
                progress_bar = st.progress(0)
            except: progress_bar = None
            
            # Extract Details
            results_data = []
            seen_names = set()

            for idx, link in enumerate(final_links):
                try:
                    # Scroll into view to ensure clickable
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    time.sleep(0.5)
                    
                    # Capture current header to check for changes
                    try:
                        old_header = self.driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
                    except:
                        old_header = ""

                    # Click
                    self.driver.execute_script("arguments[0].click();", link)
                    time.sleep(1.5) # Wait for panel animation
                        
                    # Wait for header to potentially change if it was already there
                    # Or just wait for presence
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf")))
                    except:
                        pass
                    
                    # Extract Data
                    name = "Unknown"
                    phone = "N/A"
                    website = "N/A"
                    address = "N/A"
                    
                    # 1. Name
                    try:
                        name_el = self.driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf")
                        name = name_el.text
                    except:
                        try: name = self.driver.find_element(By.TAG_NAME, "h1").text
                        except: pass
                        
                    if "Results" in name or name == "Unknown":
                        continue
                        
                    # Dedup by name immediate check
                    if name in seen_names:
                        continue
                    seen_names.add(name)

                    # 2. Address
                    try:
                        addr_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']")
                        address = addr_btn.get_attribute("aria-label").replace("Address: ", "")
                    except: pass
                    
                    # 3. Phone
                    try:
                        phone_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']")
                        phone = phone_btn.get_attribute("aria-label").replace("Phone: ", "")
                    except: pass
                    
                    # 4. Website
                    # 4. Website
                    try:
                        # Strategy 1: Standard Authority Link
                        web_btn = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                        website = web_btn.get_attribute("href")
                    except:
                        try:
                            # Strategy 2: Aria Label (New Layout)
                            web_btn = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label^='Website']")
                            website = web_btn.get_attribute("href")
                        except:
                            try:
                                # Strategy 3: Text Content (Fallback)
                                web_btn = self.driver.find_element(By.XPATH, "//a[.//div[text()='Website']]")
                                website = web_btn.get_attribute("href")
                            except:
                                pass
                    
                    results_data.append({
                        "Name": name,
                        "Phone": phone,
                        "Website": website if website and website != "N/A" else link.get_attribute("href"),
                        "Email": "N/A", 
                        "Address": address,
                        "Source": "Google Maps",
                        "Notes": f"Extracted via '{keyword}'"
                    })
                    
                    if progress_bar: progress_bar.progress((len(results_data))/limit)
                    else: print(f"[{len(results_data)}/{limit}] Extracted {name}")
                    
                    if len(results_data) >= limit:
                        break
                    
                except Exception as e:
                    continue

             # -------------------------------------------------
            # TURBO MODE: Parallel Email Hunting
            # -------------------------------------------------
            self._log(f"Hunting emails for {len(results_data)} leads...", "info")
            
            import concurrent.futures
            
            # Helper for threading
            def process_email(item):
                website = item.get("Website", "N/A")
                if website != "N/A" and "google.com/maps" not in website:
                    item["Email"] = self._hunt_email(website)
                else:
                    item["Email"] = "N/A"
                return item

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                leads = list(executor.map(process_email, results_data))
            
            return leads
            
        except Exception as e:
            self._log(f"Maps Scan error: {e}", "error")
            return []

    def _hunt_email(self, url):
        """
        Visits the URL and scans for email addresses using regex.
        Fast timeout to avoid hanging.
        """
        import requests
        from bs4 import BeautifulSoup
        import re
        
        try:
            # Fake headers to avoid 403
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Regex for email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            # Scan text
            emails = re.findall(email_pattern, soup.get_text())
            
            if not emails:
                # Try finding mailto links
                mailto = soup.select("a[href^=mailto]")
                for m in mailto:
                    href = m.get('href')
                    if href:
                        found = re.findall(email_pattern, href)
                        if found:
                            emails.extend(found)
                            
            # Return first unique valid email (filter out generic trash if needed)
            valid_emails = [e for e in set(emails) if not e.endswith(('.png', '.jpg', '.gif'))]
            
            if valid_emails:
                return valid_emails[0]
            else:
                return "N/A"
        except:
            return "N/A"
            
    def close(self):
        if self.driver:
            self.driver.quit()
