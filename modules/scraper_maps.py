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
        import platform
        from selenium import webdriver

        is_cloud = platform.system() == "Linux"

        # ── Cloud (Railway / Linux) ──────────────────────────────
        # Uses the system-installed Chromium from packages.txt
        def launch_cloud_chromium():
            self._log("Initializing Engine (Cloud Chromium)...", "info")
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.chrome.service import Service as ChromeService

            options = ChromeOptions()
            # Use system chromium binary
            options.binary_location = "/usr/bin/chromium"
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--remote-allow-origins=*")
            options.add_argument("--log-level=3")

            service = ChromeService(executable_path="/usr/bin/chromedriver")
            return webdriver.Chrome(service=service, options=options)

        # ── Local Windows: Edge ──────────────────────────────────
        def launch_edge():
            self._log("Initializing Engine (Edge)...", "info")
            from selenium.webdriver.edge.options import Options as EdgeOptions
            options = EdgeOptions()
            options.add_argument("--guest")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--log-level=3")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-allow-origins=*")
            options.add_argument("--headless=new")
            return webdriver.Edge(options=options)

        # ── Local Windows: Chrome (undetected) ───────────────────
        def launch_chrome():
            self._log("Initializing Engine (Chrome)...", "info")
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless=new")
            # Cleanup patcher
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                patcher_path = os.path.join(appdata, 'undetected_chromedriver', 'undetected_chromedriver.exe')
                if os.path.exists(patcher_path):
                    try: os.remove(patcher_path)
                    except: pass
            try:
                return uc.Chrome(options=options, use_subprocess=True)
            except Exception:
                print("Falling back to pinned Chrome version 144...")
                options = uc.ChromeOptions()
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless=new")
                return uc.Chrome(options=options, use_subprocess=True, version_main=144)

        try:
            # Cloud always uses system Chromium
            if is_cloud:
                self.driver = launch_cloud_chromium()
                return

            # Local: user preferred browser
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
            if not is_cloud and self.browser_type != "Chrome":
                try:
                    self.driver = launch_chrome()
                    return
                except: pass

            self._log(f"ALL DRIVERS FAILED. Critical Error: {e}", "error")
            raise e

    def scan(self, keyword, limit=50):
        """
        Robust Scanning logic:
        1. Scrolls to find 'limit' unique links (HREFs).
        2. Visits each HREF directly to ensure data load (bypassing StaleElement issues).
        """
        leads = []
        try:
            if not self.driver:
                self._setup_driver()
                
            # Direct Search URL
            self._log(f"Searching for '{keyword}'...", "info")
            self.driver.get(f"https://www.google.com/maps/search/{keyword}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Consent
            try:
                consent = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Accept all')]")))
                consent.click()
            except: pass
            
            time.sleep(3)

            # --- PHASE 1: COLLECT LINKS ---
            self._log(f"Phase 1: Collecting {limit} targets...", "info")
            
            unique_links = {} # clean_url -> full_url
            attempts = 0
            
            # Basic feed finder
            feed = None
            try:
                feed = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            except: pass
            
            # Scroll Loop
            # We allow more scroll attempts to ensure we find enough agents
            while len(unique_links) < limit and attempts < (limit * 2):
                # Scroll
                try:
                    if feed:
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    else:
                        # Fallback for main body
                        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                except: pass
                
                time.sleep(1.5)
                
                # Check links
                els = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place']")
                for e in els:
                    href = e.get_attribute("href")
                    if href:
                        clean = href.split('?')[0]
                        if clean not in unique_links:
                             unique_links[clean] = href
                
                # Update progress in log occasionally
                if attempts % 5 == 0:
                    self._log(f"Found {len(unique_links)} potential targets...", "info")
                
                if len(unique_links) >= limit:
                    break
                    
                attempts += 1
                
            target_urls = list(unique_links.values())[:limit]
            self._log(f"Phase 2: Extracting data from {len(target_urls)} targets...", "info")

            # --- PHASE 2: VISIT & EXTRACT ---
            import streamlit as st
            progress_bar = st.progress(0)
            
            results_data = [] # Local collection
            
            for i, url in enumerate(target_urls):
                try:
                    self.driver.get(url)
                    time.sleep(1.5) # Wait for details
                    
                    # Name
                    name = "Unknown"
                    try:
                        name = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
                    except: pass
                    
                    # Address, Phone, Website
                    address = "N/A"
                    phone = "N/A"
                    website = "N/A"
                    
                    try:
                        address = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']").get_attribute("aria-label").replace("Address: ", "")
                    except: pass
                    
                    try:
                        phone = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']").get_attribute("aria-label").replace("Phone: ", "")
                    except: pass
                    
                    try:
                        website = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']").get_attribute("href")
                    except: 
                        try: website = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label^='Website']").get_attribute("href")
                        except: pass
                    
                    # Store
                    results_data.append({
                        "Name": name,
                        "Phone": phone,
                        "Website": website if website else url,
                        "Email": "N/A",
                        "Address": address,
                        "Source": "Google Maps",
                        "Notes": f"Extracted via {keyword}"
                    })
                    
                    progress_bar.progress((i + 1) / len(target_urls))
                    
                except Exception as e:
                    self._log(f"Failed to extract {url}: {e}", "warning")
                    continue
            
            # --- EMAIL HUNTING ---
            if results_data:
                self._log(f"Hunting emails for {len(results_data)} leads...", "info")
                import concurrent.futures
                
                def process_email(item):
                    website = item.get("Website", "N/A")
                    if website != "N/A" and "google.com/maps" not in website:
                        item["Email"] = self._hunt_email(website)
                    return item

                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    leads = list(executor.map(process_email, results_data))
                
                return leads
            else:
                return []
            
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
