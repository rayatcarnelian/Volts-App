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
        self._is_cloud = False

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
        """On Windows: launch Edge via Selenium. On Linux (Railway): no-op (uses HTTP-based scan)."""
        import platform
        from selenium import webdriver

        if platform.system() == "Linux":
            # Cloud mode — no browser needed, scan() will use HTTP-based approach
            self._log("Cloud mode: Using HTTP-based scraping (no browser needed)", "info")
            self.driver = None
            self._is_cloud = True
            return

        # === LOCAL (Windows) — Use Edge ===
        self._log("Initializing Engine (Edge)...", "info")
        self._is_cloud = False
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
        self.driver = webdriver.Edge(options=options)

    def _cloud_scan(self, keyword, limit=50):
        """HTTP-based Google Maps scraping for cloud environments (no browser)."""
        import re
        import requests
        from bs4 import BeautifulSoup
        from duckduckgo_search import DDGS
        import streamlit as st

        results = []
        self._log(f"Cloud Scan: Searching for '{keyword}' via DuckDuckGo...", "info")

        try:
            # Use DuckDuckGo to find businesses matching the keyword
            ddgs = DDGS()
            search_results = list(ddgs.text(
                f"{keyword} site:google.com/maps/place OR {keyword} business contact",
                max_results=limit * 3  # Over-fetch to filter
            ))

            self._log(f"Found {len(search_results)} search results, extracting data...", "info")

            progress_bar = st.progress(0)
            processed = 0

            for i, result in enumerate(search_results):
                if len(results) >= limit:
                    break

                title = result.get("title", "Unknown Business")
                body = result.get("body", "")
                url = result.get("href", "")

                # Skip non-business results
                if not title or len(title) < 3:
                    continue

                # Extract phone from search snippet
                phone = "N/A"
                phone_match = re.search(r'[\+]?[\d\s\-\(\)]{7,15}', body)
                if phone_match:
                    phone = phone_match.group().strip()

                # Try to find email from the website if available
                email = "N/A"
                website = url if "google.com/maps" not in url else "N/A"

                # Extract address from snippet
                address = "N/A"
                if body:
                    # Common address patterns
                    addr_match = re.search(r'(?:\d+[\w\s,]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Dr|Drive|Lane|Way|Jln|Jalan)[\w\s,]*)', body)
                    if addr_match:
                        address = addr_match.group().strip()

                results.append({
                    "Name": title.split(" - ")[0].split(" | ")[0].strip(),
                    "Phone": phone,
                    "Website": website if website != "N/A" else url,
                    "Email": email,
                    "Address": address,
                    "Source": "Google (Cloud)",
                    "Notes": f"Extracted via '{keyword}'"
                })

                processed += 1
                progress_bar.progress(min(processed / limit, 1.0))

            # Email hunting for results with websites
            if results:
                self._log(f"Hunting emails for {len(results)} leads...", "info")
                import concurrent.futures

                def process_email(item):
                    website = item.get("Website", "N/A")
                    if website != "N/A" and "google.com" not in website:
                        item["Email"] = self._hunt_email(website)
                    return item

                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    results = list(executor.map(process_email, results))

        except Exception as e:
            self._log(f"Cloud scan error: {e}", "error")
            raise

        return results

    def scan(self, keyword, limit=50):
        """
        Robust Scanning logic:
        1. Scrolls to find 'limit' unique links (HREFs).
        2. Visits each HREF directly to ensure data load (bypassing StaleElement issues).
        """
        leads = []
        try:
            if not self.driver and not getattr(self, '_is_cloud', False):
                self._setup_driver()

            # Route to cloud scan if on Linux (no browser)
            if getattr(self, '_is_cloud', False):
                return self._cloud_scan(keyword, limit)
                
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
            raise  # Let the error surface in the UI

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
