import time
import random
import os
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

class InstagramHunter:
    def __init__(self):
        self.driver = None

    def _log(self, message, level="info"):
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

    def _setup_driver(self, force_standard=False):
        import platform
        
        # 0. STRICT MODE: If force_standard is ON, we do NOT touch undetected-chromedriver
        if force_standard:
            self._init_standard_selenium(platform.system())
            return
            
        # 1. Try Undetected Chromedriver
        try:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            if platform.system() == "Linux":
                options.add_argument('--headless=new')

            self._log("Attempting to start Undetected Chromedriver...", "info")
            # FIX: Enforce version 144 matches system Chrome
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)
            self.driver.set_page_load_timeout(60)
            return
            
        except Exception as e:
            self._log(f"Undetected Driver failed: {e}. Falling back to Standard Selenium...", "warning")
            # Fallback
            self._init_standard_selenium(platform.system())

    def _init_standard_selenium(self, system_platform):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--start-maximized')
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            
            # Anti-detection flags for standard selenium
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if system_platform == "Linux":
                options.add_argument('--headless=new')
            
            self._log("Attempting to start Standard Selenium Driver...", "info")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            
            # Additional stealth via CDP
            try:
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                        })
                    """
                })
            except:
                pass
            self._log("Standard Selenium Driver started successfully.", "info")
            
        except Exception as e2:
            self._log(f"Critical Error: Driver initialization failed. {e2}", "error")
            raise e2

    def login(self, username=None, password=None, retry_count=0, force_standard=False):
        try:
            if not self.driver:
                # If force_standard is explicitly requested (e.g. from UI), respect it
                # Otherwise simple retry logic determines it
                use_standard = force_standard or (retry_count > 0)
                self._setup_driver(force_standard=use_standard)
            
            st.toast("Navigating to Instagram Login...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)
            
            # Priority: Arguments > Env Vars
            final_user = username if username else os.getenv("INSTA_USER")
            final_pass = password if password else os.getenv("INSTA_PASS")

            if not final_user or not final_pass:
                st.error("Credentials missing. Please update .env or provide them manually.")
                return False

            # Attempt to handle cookie banners (Same as before)
            try:
                popups = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept') or contains(text(), 'Decline')]"))
                )
                if popups:
                    popups[0].click()
                    time.sleep(2)
            except:
                pass

            # Auto-fill
            try:
                print("Waiting for username input...")
                user_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                pass_input = self.driver.find_element(By.NAME, "password")
                
                # Clear fields just in case
                user_input.clear()
                user_input.send_keys(final_user)
                
                pass_input.clear()
                pass_input.send_keys(final_pass)
                
                login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_btn.click()
                st.toast("Credentials submitted...")
                time.sleep(5)
                
                # Verification
                try:
                    WebDriverWait(self.driver, 15).until(
                        lambda d: "accounts/onetap" in d.current_url or "challenge" in d.current_url or "login" not in d.current_url
                    )
                    st.success("Login Successful")
                    return True
                except:
                    # If we are still on login page, it failed.
                    if "login" in self.driver.current_url:
                        # Check for error message
                        try:
                            err = self.driver.find_element(By.ID, "slfErrorAlert")
                            st.warning(f"Instagram says: {err.text}")
                        except:
                            st.warning("Login verification timed out. Inspecting screenshot.")
                        
                        self.driver.save_screenshot("login_failed.png")
                        st.image("login_failed.png", caption="Login Failure Screen")
                        return False
                    
                    # If URL changed but not to known success, assume success (e.g. 2FA)
                    return True
                
            except Exception as e:
                # If we haven't retried yet and it crashed, try switching drivers
                # But if we were FORCED to standard, don't loop endlessly
                if retry_count == 0 and not force_standard:
                    print(f"Login crashed ({e}). Switching to Standard Driver and retrying...")
                    st.warning("Browser engine unstable. Switching to Standard Mode...")
                    self.close()
                    # Recursive retry with forced standard driver
                    return self.login(username, password, retry_count=1, force_standard=True)
                
                msg = f"Login interaction failed: {e}"
                print(msg)
                st.warning(msg)
                try:
                    self.driver.save_screenshot("login_crash.png")
                    st.image("login_crash.png", caption="Crash State")
                except:
                    pass
                return False

        except Exception as e:
            if retry_count == 0 and not force_standard:
                print(f"Driver init crashed ({e}). Retrying with Standard Driver...")
                self.close()
                return self.login(username, password, retry_count=1, force_standard=True)
                
            st.error(f"Driver/Browser Error: {e}")
            return False

    def scrape_hashtag(self, hashtag, max_posts=10, username=None, password=None, use_safe_mode=False):
        # Initial implementation - detailed logic to be refined
        if not self.driver:
            # Pass credentials down to login
            login_success = self.login(username=username, password=password, force_standard=use_safe_mode)
            if not login_success:
                 return []
            
        leads = []
        try:
            tag = hashtag.replace("#", "")
            st.toast(f"Scraping #{tag}...")
            self.driver.get(f"https://www.instagram.com/explore/tags/{tag}/")
            time.sleep(5)
            
            # --- REAL SCRAPING LOGIC ---
            # Wait for grid to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/p/')]"))
                )
            except:
                st.warning("No posts found or page failed to load.")
                
            # Scroll and Collect
            unique_links = set()
            scroll_count = 0
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while len(unique_links) < max_posts and scroll_count < 5:
                # Collect
                posts = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
                new_found = 0
                for p in posts:
                    href = p.get_attribute("href")
                    if href and href not in unique_links:
                        unique_links.add(href)
                        new_found += 1
                        
                status_text.text(f"Found {len(unique_links)} posts...")
                progress_bar.progress(min(len(unique_links) / max_posts, 1.0))
                
                if len(unique_links) >= max_posts:
                    break
                    
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(3, 6))
                scroll_count += 1
                
            st.success(f"Found {len(unique_links)} unique posts. Extracting details...")
            
            for i, link in enumerate(unique_links):
                if i >= max_posts: break
                leads.append({
                    "Username": "Unknown (Visit to see)",
                    "Link": link,
                    "Source": "Instagram",
                    "Status": "New"
                })
                
            return leads
            
        except Exception as e:
            st.error(f"Scraping failed: {e}")
            return []
            
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
