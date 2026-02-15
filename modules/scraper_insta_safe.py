import time
import random
import os
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

class InstagramHunterSafe:
    def __init__(self):
        self.driver = None

    def _setup_driver(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options
            
            print(">>> DEBUG: STARTING CHROME DRIVER (JS-INJECTION MODE) <<<")
            
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-gpu')               # CRITICAL FIX
            options.add_argument('--disable-software-rasterizer') # CRITICAL FIX
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            
            print(">>> CHROME DRIVER READY <<<")
            
        except Exception as e2:
            st.error(f"Critical Error: Driver initialization failed. {e2}")
            raise e2

    def login(self, username=None, password=None):
        try:
            if not self.driver:
                self._setup_driver()
            
            st.toast("Navigating to Instagram Login (Safe Mode)...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)
            
            # Priority: Arguments > Env Vars
            final_user = username if username else os.getenv("INSTA_USER")
            final_pass = password if password else os.getenv("INSTA_PASS")

            if not final_user or not final_pass:
                st.error("Credentials missing. Please update .env or provide them manually.")
                return False

            # Attempt to handle cookie banners
            try:
                popups = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept') or contains(text(), 'Decline')]"))
                )
                if popups:
                    popups[0].click()
                    time.sleep(2)
            except:
                pass

            # Auto-fill using JS Injection (CRITICAL FIX FOR CRASH)
            try:
                print("Waiting for username input...")
                user_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                pass_input = self.driver.find_element(By.NAME, "password")
                
                print("Injecting Credentials via JS...")
                # 1. Inject Username
                self.driver.execute_script("arguments[0].value = arguments[1];", user_input, final_user)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", user_input)
                
                # 2. Inject Password
                self.driver.execute_script("arguments[0].value = arguments[1];", pass_input, final_pass)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", pass_input)
                
                time.sleep(1)
                
                # 3. Click Login via JS
                login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                self.driver.execute_script("arguments[0].click();", login_btn)
                
                st.toast("Credentials submitted...", icon="🚀")
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
                        
                        self.driver.save_screenshot("login_failed_safe.png")
                        st.image("login_failed_safe.png", caption="Login Failure Screen")
                        return False
                    
                    return True
                
            except Exception as e:
                msg = f"Login interaction failed: {e}"
                print(msg)
                st.warning(msg)
                try:
                    self.driver.save_screenshot("login_crash_safe.png")
                    st.image("login_crash_safe.png", caption="Crash State")
                except:
                    pass
                return False

        except Exception as e:
            st.error(f"Driver/Browser Error: {e}")
            return False

    def scrape_hashtag(self, hashtag, max_posts=10, username=None, password=None):
        if not self.driver:
            login_success = self.login(username=username, password=password)
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
            
            # basic extraction from links (Visiting each is riskier but more accurate. 
            # For 'Safe' mode, let's just return the links and maybe try to get authors if possible from grid? 
            # Grid doesn't usually show author. 
            # Let's visit the first few or just return Links.)
            
            # To be safe and fast, we will just return the links for now, 
            # or maybe visit a few if the user wants 'Enriched' data.
            # But the user complained about 'Manual Login'. Let's Ensure we at least get the links.
            
            for i, link in enumerate(unique_links):
                if i >= max_posts: break
                leads.append({
                    "Username": "Unknown (Visit to see)",
                    "Link": link,
                    "Source": "Instagram (Safe Browser)",
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
