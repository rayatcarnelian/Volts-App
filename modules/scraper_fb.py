import time
import random
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pickle
from dotenv import load_dotenv
from modules import database as db

# --- SAFETY CONSTANTS ---
MIN_DELAY = 15 
MAX_DELAY = 45

class FacebookHunter:
    def __init__(self):
        # DEBUG: Check environment loading
        load_dotenv() 
        cwd = os.getcwd()
        env_path = os.path.join(cwd, ".env")
        print(f"DEBUG: CWD is {cwd}")
        print(f"DEBUG: .env exists: {os.path.exists(env_path)}")
        email = os.getenv("FB_EMAIL")
        print(f"DEBUG: Loaded FB_EMAIL: {email[:3]}***" if email else "DEBUG: FB_EMAIL is None")
        
        self.driver = None
        self.cookies_path = "fb_cookies.pkl"

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

    def _setup_driver(self, headless=True):
        options = Options()
        
        # METHOD CHANGE: Use specific User-Agent instead of Device Emulation
        # Nokia UA was "Unsupported". Modern Mobile UA gets "WebLite" (React).
        # Desktop UA is the safest middle ground for mbasic.
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        options.add_argument(f"--user-agent={ua}")
        options.add_argument("--window-size=1920,1080") # High-Res for Desktop Site triggers
        
        options.add_argument("--disable-notifications")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-popup-blocking")
        
        # Anti-Detect
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        if headless:
            options.add_argument("--headless=new")
        
        # Use webdriver_manager to get the robust standard driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def human_delay(self):
        """Waits for a random amount of time to simulate human reading."""
        sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(sleep_time)

    def load_cookies(self):
        if os.path.exists(self.cookies_path):
            try:
                cookies = pickle.load(open(self.cookies_path, "rb"))
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                return True
            except:
                return False
        return False

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def _load_cookies_if_present(self):
        """Helper to inject cookies before navigation"""
        if os.path.exists("cookies.txt"):
             # Navigate to domain first to allow cookie setting
             try:
                 if "facebook.com" not in self.driver.current_url:
                     self.driver.get("https://mbasic.facebook.com/")
                 self.load_netscape_cookies("cookies.txt")
                 self._log("Cookies Injected", "info")
                 time.sleep(1)
             except Exception as e:
                 print(f"Cookie load warning: {e}")

    def login_manual(self):
        """
        Attempts to log in.
        1. Priority: Load 'cookies.txt' (Netscape format) if it exists. This bypasses 2FA/Captchas.
        2. Fallback: Auto-fill creds (Updated for Bloks UI).
        3. Manual: Wait for user.
        """
        self._log("Initiating Auth Sequence...", "info")
        
        # 1. COOKIE INJECTION (The "Nuclear" Option)
        cookie_file = "cookies.txt"
        if os.path.exists(cookie_file):
             self._log(f"Found {cookie_file}. Injecting...", "info")
             try:
                 self.driver.get("https://mbasic.facebook.com/") # Domain context needed
                 self.load_netscape_cookies(cookie_file)
                 self.driver.get("https://mbasic.facebook.com/")
                 time.sleep(3)
                 if self.is_logged_in():
                      st.success("Cookie Injection Successful!")
                      return
                 else:
                      st.warning("Injected cookies might be stale.")
             except Exception as e:
                 st.error(f"Cookie Import Failed: {e}")

        # 2. AUTO-LOGIN
        email = os.getenv("FB_EMAIL")
        password = os.getenv("FB_PASS")
        
        # Ensure we are on login page
        if "login" not in self.driver.current_url and "mbasic" not in self.driver.current_url:
             self.driver.get("https://mbasic.facebook.com/")
        
        # Check for specific "Continue" or "Log In" buttons (Bloks UI)
        try:
            # "Continue as [Name]"
            continue_btns = self.driver.find_elements(By.XPATH, "//div[@aria-label='Continue'] | //span[contains(text(), 'Continue')]")
            if continue_btns:
                continue_btns[0].click()
                time.sleep(5)
                if self.is_logged_in(): return

            # "Log In" button (often a div in Bloks)
            login_divs = self.driver.find_elements(By.XPATH, "//div[@role='button'][@aria-label='Log in']")
            
            if email and password:
                self._log("Attempting Auto-Login...", "info")
                
                # Fill Email
                try: 
                    # Try explicitly locating the input
                    email_field = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.NAME, "email")))
                    email_field.clear()
                    email_field.send_keys(email)
                except: pass

                # Fill Pass
                try:
                    pass_field = self.driver.find_element(By.NAME, "pass")
                    pass_field.clear()
                    pass_field.send_keys(password)
                    time.sleep(1)
                    
                    # CLICK LOGIN
                    # Priority 1: The Bloks "Log in" Div
                    if login_divs:
                        login_divs[0].click()
                    else:
                        # Priority 2: Standard Name
                        try: self.driver.find_element(By.NAME, "login").click()
                        except: pass_field.send_keys(Keys.RETURN)
                        
                    self._log("Credentials Submitted...", "info")
                    time.sleep(8)
                    
                    if self.is_logged_in():
                        self._log("Auto-Login Successful!", "info")
                        self.save_cookies()
                        return
                    
                except Exception as e:
                    print(f"Login Fill Error: {e}")

        except Exception as e:
            print(f"Pre-login check error: {e}")

        # 3. MANUAL FALLBACK
        self._log("Manual Login Required.", "warning")
        if "--headless" in str(self.driver.capabilities):
             self._log("Cannot manual login in Headless mode. Restarting Visible...", "error")
             self.driver.quit()
             self._setup_driver(headless=False)
             self.driver.get("https://mbasic.facebook.com/")
        
        # st.stop() # Removed for CLI compat
        return 

    def is_logged_in(self):
        """Checks if the user is currently logged in."""
        # Check for logout link, specific cookie, or absence of login form
        if "Log Out" in self.driver.page_source or "m_group_stories_container" in self.driver.page_source:
             return True
        # Privacy token or Settings often indicate login
        if "privacy/mutation_token" in self.driver.page_source:
             return True
        return False

    def load_netscape_cookies(self, cookie_file):
        """Parses a Netscape format cookie file and adds to driver."""
        try:
            with open(cookie_file, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip(): continue
                    parts = line.split('\t')
                    if len(parts) >= 6:
                        domain = parts[0]
                        # Clean domain for selenium (must match current page or start with dot)
                        # We are on .facebook.com usually
                        
                        cookie = {
                            'domain': domain,
                            'name': parts[5],
                            'value': parts[6].strip(),
                            'path': parts[2],
                            'expiry': int(parts[4]) if parts[4].strip() else None,
                            'secure': parts[3] == 'TRUE'
                        }
                        try: self.driver.add_cookie(cookie)
                        except: pass
        except Exception as e:
            self._log(f"Netscape Load Error: {e}", "error")

    def hunt_group(self, group_url, keywords=[], max_scrolls=3):
        if not self.driver:
            self._setup_driver(headless=True) # Default start
            
        # --- URL SANITIZATION ---
        if group_url:
            import re
            match = re.search(r'(https?://[^\s]+)', group_url)
            if match:
                group_url = match.group(1)

            if "https://" in group_url and "https://" in group_url[8:]:
                 group_url = group_url.split("https://")[1]
                 group_url = "https://" + group_url
                 match_double = re.findall(r'https?://', group_url)
                 if len(match_double) > 1:
                     if "facebook.com" in group_url:
                         start = group_url.find("facebook.com")
                         group_url = "https://" + group_url[start:]
            
        # REGEX DOMAIN FIX (Prevents "web.mbasic" errors)
        if group_url:
             import re
             if "://" in group_url: group_url = group_url.split("://")[1]
             
             # Locate facebook.com (with optional prefixes) and everything after
             match = re.search(r'(?:www\.|web\.|m\.|mbasic\.)?facebook\.com(.*)', group_url)
             
             if match:
                 path = match.group(1)
                 group_url = f"https://mbasic.facebook.com{path}"
             else:
                 if "facebook.com" in group_url:
                     group_url = f"https://mbasic.facebook.com/{group_url.split('facebook.com')[-1]}"
            
        # 1. Force Cookie Injection
        self._load_cookies_if_present()

        # 2. Navigation
        try:
             if "/share/" in group_url:
                 st.toast("Resolving Share Link...", icon="🔗")
         
             st.info(f"Targeting: {group_url}")
             self.driver.get(group_url)
             time.sleep(5) 
        except Exception as e:
             st.error(f"Navigation Error: {e}")
             return 0

        # 3. Login Check
        if "log in" in self.driver.title.lower() or "login_try_number" in self.driver.page_source:
             st.warning("Session Expired/Invalid. Triggering Auth...")
             self.login_manual()
             # Retry nav
             self.driver.get(group_url)
             time.sleep(5)
        
        # 4. Join Check
        if "Join Group" in self.driver.page_source and "m_group_stories_container" not in self.driver.page_source:
            st.warning("You might need to JOIN this group to see posts.")

        # -------------------------------------------------
        # HYBRID SCRAPING LOGIC
        # -------------------------------------------------
        leads = []
        leads_count = 0
        scroll_attempts = 0
        
        # Detect Mode
        is_desktop = "www.facebook.com" in self.driver.current_url or "web.facebook.com" in self.driver.current_url or "_9dls" in self.driver.page_source
        st.write(f"DEBUG: Mode Detected: {'Desktop (Comet)' if is_desktop else 'Mobile (mbasic)'}")

        # 1. Wait for Feed
        try:
            if is_desktop:
                 # Desktop Wait: Wait for 'Actions for this post' to confirm REAL content
                 st.toast("Desktop: Waiting for Posts...", icon="⏳")
                 WebDriverWait(self.driver, 20).until(
                     EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Actions for this post']"))
                 )
                 time.sleep(4) # Allow full React hydration
            else:
                 # mbasic Wait
                 WebDriverWait(self.driver, 10).until(
                     EC.presence_of_element_located((By.CSS_SELECTOR, "#m_group_stories_container"))
                 )
        except:
             if "unsupported-interstitial" in self.driver.page_source:
                   st.error("Blocked: Unsupported Browser.")
             else:
                   st.warning(f"Timeout waiting for {'Desktop' if is_desktop else 'mbasic'} feed.")
                   # Debug Snapshot
                   with open("fb_debug_source.html", "w", encoding="utf-8") as f:
                       f.write(self.driver.page_source)
                   self.driver.save_screenshot("fb_debug_fail.png")
                   return 0

        st.toast("Feed Detected. Hunting...", icon="🤐")
        
        while scroll_attempts < max_scrolls:
            
            if is_desktop:
                # --- DESKTOP SCRAPING ---
                # Check for 'aria-posinset' which marks actual feed items in virtualized lists
                # This bypasses the 'role=article' issue where it might be missing or applied to skeletons
                raw_articles = self.driver.find_elements(By.XPATH, "//div[@aria-posinset]")
                
                if not raw_articles:
                     # Fallback to 'Actions for this post' button's container logic (approximate)
                     # or generic Comect class
                     raw_articles = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'x1yztbdb')]")

                articles = []
                for a in raw_articles:
                    try:
                        # Ensure it's not a skeleton
                        lid = a.get_attribute("aria-label") or ""
                        if "Loading" in lid or not a.text.strip():
                            continue
                        articles.append(a)
                    except: pass
                
                if not articles:
                     # Final fallback
                     articles = self.driver.find_elements(By.XPATH, "//div[@role='article']")

                for article in articles:
                    try:
                        text = article.text
                        if not text: continue
                        
                        match = False
                        if not keywords or "*" in keywords or keywords == [""]:
                            match = True
                        else:
                            for k in keywords:
                                if k.lower() in text.lower(): 
                                    match = True; break
                        
                        if match:
                            # Contextual Info
                            author = "Unknown" 
                            profile_link = "N/A"
                            
                            try:
                                header = article.find_element(By.XPATH, ".//strong | .//h2//span | .//h3//span")
                                author = header.text
                                
                                # Try to find profile link in parent 'a' tag or nearby
                                try:
                                    # Look for 'a' tag that contains this header or is parent
                                    # Desktop often has: h2 > span > a  OR  strong > a
                                    parent_a = article.find_element(By.XPATH, ".//strong/a | .//h2//a | .//h3//a")
                                    profile_link = parent_a.get_attribute("href")
                                    if "hovercard" in profile_link: # Clean up hovercard params
                                        profile_link = profile_link.split("?")[0]
                                except: pass
                            except: pass
                            
                            # Email Extraction (Regex)
                            import re
                            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                            email = emails[0] if emails else "N/A"
                            
                            if len(text) > 20: # Filter noise
                                author_clean = author if len(author) < 50 else "Unknown"
                                leads.append({"Source": "Facebook (Desktop)", "Name": author_clean, "Profile": profile_link, "Context": text[:100], "Status": "New", "Email": email})
                                leads_count += 1
                                st.toast(f"Found: {author_clean}", icon="⚡")
                                # Pass profile_link and email to DB
                                db.add_lead_v2(name=author_clean, company=email, source=f"Facebook Group ({group_url})", location="Facebook", link=profile_link, notes=text[:500], status="New")
                    except: pass
                    
            else:
                # --- MBASIC SCRAPING ---
                articles = self.driver.find_elements(By.CSS_SELECTOR, "article, div[role='article'], #m_group_stories_container > div") 
                for article in articles:
                    try:
                        text = article.text
                        if not text: continue
                        
                        match = False
                        if not keywords or "*" in keywords or keywords == [""]:
                            match = True
                        else:
                            for k in keywords:
                                if k.lower() in text.lower(): 
                                    match = True; break
                        
                        if match:
                            author = "Unknown"
                            profile_link = "N/A"
                            try:
                                 header = article.find_element(By.CSS_SELECTOR, "strong, h3 a")
                                 author = header.text
                                 
                                 # Get href from the name link
                                 try:
                                     # check if header itself is 'a' (h3 a) or inside strong
                                     if header.tag_name == 'a':
                                         profile_link = header.get_attribute("href")
                                     else:
                                         # try children
                                         link_el = header.find_element(By.TAG_NAME, "a")
                                         profile_link = link_el.get_attribute("href")
                                 except: pass
                            except: pass
                            
                            # Fallback post link
                            post_link = "Unknown"
                            try:
                                link_el = article.find_element(By.PARTIAL_LINK_TEXT, "Full Story")
                                post_link = link_el.get_attribute("href")
                                if profile_link == "N/A": profile_link = post_link # Better than nothing
                            except: pass
                            
                            # Email Extraction
                            import re
                            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                            email = emails[0] if emails else "N/A"
                            
                            if len(text) > 20:
                                leads.append({"Source": "Facebook (Mobile)", "Name": author, "Profile": profile_link, "Context": text[:100], "Status": "New", "Email": email})
                                leads_count += 1
                                st.toast(f"Found: {author}", icon="⚡")
                                db.add_lead_v2(name=author, company=email, source=f"Facebook Group ({group_url})", location="Facebook (Mobile)", link=profile_link, notes=text[:500], status="New")
                            
                    except: pass
            
            # PAGINATION
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                if not is_desktop:
                    next_btn = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'See more posts')]")
                    if next_btn:
                        next_btn[0].click()
                        st.toast(f"Navigating to Page {scroll_attempts + 2}...", icon="⏭️")
                        time.sleep(3)
                    else: break
            except: break
                
            scroll_attempts += 1
            
        return leads_count

    def hunt_marketplace(self, city_url, query, limit=10):
        if not self.driver:
            self._setup_driver(headless=False) # Marketplace often needs visible mode

        # 1. Construct URL
        # e.g. https://www.facebook.com/marketplace/singapore/search?query=sofa
        base_url = "https://www.facebook.com/marketplace"
        
        # Clean City URL
        if city_url:
            if "facebook.com/marketplace" in city_url:
                # User pasted full URL like https://www.facebook.com/marketplace/nyc/
                # We need to strip standard query params if any, or just append search
                if "?" in city_url:
                    target_url = f"{city_url}&query={query}"
                else:
                    target_url = f"{city_url.rstrip('/')}/search?query={query}"
            else:
                # Assume it's a slug? No, safer to ask for full URL. 
                # Fallback to search global
                target_url = f"{base_url}/search?query={query}"
        else:
            target_url = f"{base_url}/search?query={query}"
            
        st.toast(f"Navigating: {query}...", icon="🛒")
        self.driver.get(target_url)
        
        # 2. Wait for Load
        try:
            # Wait for main grid or feed
            # Try multiple selectors for robustness
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='main'] | //div[@aria-label='Collection of Marketplace items'] | //div[contains(@class, 'x1illiih')]"))
            )
        except:
            st.warning("Marketplace feed did not load generally. Check valid City URL.")
            
        time.sleep(5) # Allow React hydration
        
        listings_found = 0
        scroll_attempts = 0
        self.seen_links = set()
        
        while listings_found < limit and scroll_attempts < 10:
            # 3. Find Items
            try:
                # Generic link finder within main role
                links = self.driver.find_elements(By.XPATH, "//a[@role='link']")
                
                valid_items = []
                for a in links:
                    href = a.get_attribute("href")
                    if href and "/marketplace/item/" in href:
                        if href not in self.seen_links:
                            valid_items.append(a)
                            self.seen_links.add(href)
                        
                st.write(f"DEBUG: Found {len(valid_items)} new items in view.")
                
                for item in valid_items:
                    if listings_found >= limit: break
                    
                    try:
                        link = item.get_attribute("href")
                        
                        # Extract Price and Title
                        # Marketplace DOM is messy but usually consistent in order:
                        # 0: Price
                        # 1: Title
                        # 2: Location
                        text_content = [line.strip() for line in item.text.split("\n") if line.strip()]
                        
                        price = "N/A"
                        title = "Unknown Item"
                        location = "Marketplace"
                        
                        if len(text_content) >= 2:
                            # Positional Logic
                            potential_price = text_content[0]
                            potential_title = text_content[1]
                            
                            # Validate Price (Rough check)
                            has_digit = any(char.isdigit() for char in potential_price)
                            is_short = len(potential_price) < 20
                            
                            if has_digit and is_short:
                                price = potential_price
                                title = potential_title
                                if len(text_content) > 2:
                                    location = text_content[2]
                            else:
                                # Fallback to heuristic search if position 0 isn't price
                                # e.g. "Featured" tag might be first
                                for line in text_content:
                                    # Check for common currencies including MYR
                                    is_currency = any(c in line for c in ["$", "RM", "MYR", "€", "£"])
                                    if any(char.isdigit() for char in line) and len(line) < 15 and (is_currency or line[0].isdigit()):
                                        if price == "N/A": price = line
                                    elif len(line) > 3 and title == "Unknown Item":
                                        title = line
                        
                        # Fallbacks
                        if title == "Unknown Item": 
                            if len(text_content) > 0: 
                                # Don't just grab the first line if it's already the price
                                if text_content[0] != price:
                                    title = text_content[0]
                                elif len(text_content) > 1:
                                    title = text_content[1]
                                else:
                                    title = "Untitled Listing"
                            else: title = f"Item {listings_found+1}"

                        # Final Safety Check
                        if title == price:
                            title = "Untitled Listing"

                        # Save
                        st.toast(f"Found: {title} ({price})", icon="📦")
                        # Save
                        st.toast(f"Found: {title} ({price})", icon="📦")
                        # Use add_lead_v2 directly for reliability
                        db.add_lead_v2(
                            name=title, 
                            company=price, 
                            source=f"Facebook Marketplace ({query})", 
                            location=location, 
                            link=link,
                            status="New"
                        )
                        listings_found += 1
                        
                    except Exception as e:
                        print(f"Item Parse Error: {e}")
                        
            except Exception as e:
                print(f"Marketplace Scan Error: {e}")
                
            # Scroll
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_attempts += 1
            
        return listings_found 

    def auto_comment(self, post_url, comment_text):
        """
        Attempts to comment on a post. 
        Uses mbasic for simplicity and stealth.
        """
        if not self.driver:
            self._setup_driver(headless=True) # mbasic works best headless usually
            
        # 1. Convert to mbasic URL
        # Remove www, web, m
        import re
        if "facebook.com" in post_url:
            # Strip domain to get path
            path_match = re.search(r'facebook\.com(.*)', post_url)
            if path_match:
                path = path_match.group(1)
                target_url = f"https://mbasic.facebook.com{path}"
            else:
               target_url = post_url
        else:
            target_url = post_url # hope for the best
            
        self._log(f"Navigating to {target_url}...", "info")
        self.driver.get(target_url)
        self.human_delay()
        
        # 2. Check Login
        if "login" in self.driver.current_url or "Log In" in self.driver.title:
            self._log("Login required...", "warning")
            self.login_manual()
            self.driver.get(target_url)
            time.sleep(3)
            
        # 3. Find Comment Box
        # mbasic usually has a form with action='/a/comment.php...'
        # Input name is usually 'comment_text'
        try:
            # Look for the textarea or input
            comment_box = self.driver.find_element(By.NAME, "comment_text")
            
            # Fill
            comment_box.send_keys(comment_text)
            self.human_delay()
            
            # Submit
            # Usually a button with value="Comment" or type="submit"
            submit_btn = self.driver.find_element(By.XPATH, "//input[@type='submit'][@value='Comment']")
            submit_btn.click()
            
            time.sleep(5)
            
            # Verification
            if comment_text[:20] in self.driver.page_source:
                self._log("Comment verified visible.", "success")
                return True
            else:
                self._log("Comment posted but verification uncertain.", "warning")
                return True
                
        except Exception as e:
            self._log(f"Comment Failed: {e}", "error")
            # Snapshot for debug
            self.driver.save_screenshot("comment_fail.png")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
