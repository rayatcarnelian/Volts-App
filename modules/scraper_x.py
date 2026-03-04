
import time
import os
import pickle
import random
import urllib.parse
from datetime import datetime, timedelta
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import modules.db_supabase as db
from dotenv import load_dotenv

# Use undetected-chromedriver for bypass
import undetected_chromedriver as uc

load_dotenv()

class XHunter:
    def __init__(self):
        self.driver = None

    def _setup_driver(self):
        try:
            print(">>> INITIALIZING X HUNTER (Undetected Mode) <<<")
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-popup-blocking")
            
            # CRITICAL: Persistent Profile + safe args
            # Using a DIFFERENT profile dir to avoid corruption
            cwd = os.getcwd()
            profile_dir = os.path.join(cwd, "chrome_profile_x_safe")
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
            options.add_argument(f"--user-data-dir={profile_dir}")
            
            # Start Driver
            # Start Driver
            try:
                self.driver = uc.Chrome(options=options, use_subprocess=True)
            except Exception:
                print("Falling back to pinned Chrome version 144...")
                # Re-create options
                options = uc.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-popup-blocking")
                options.add_argument(f"--user-data-dir={profile_dir}")
                
                self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)

            self.driver.set_page_load_timeout(60)
            
        except Exception as e:
            st.error(f"Driver Init Failed: {e}")
            raise e

    def _login(self):
        """Attempts login and WAITS for user if needed."""
        if not self.driver:
            self._setup_driver()

        st.toast("Checking X Session...", icon="🔒")
        self.driver.get("https://x.com/home")
        time.sleep(5)
        
        # 1. Check if already logged in (Fast Path)
        if self._is_logged_in():
             st.success("Session Valid (Persistent Profile)")
             return True
             
        # 2. Needs Login - Try Auto-Nav
        st.toast("Authentication required. Navigating to Login...", icon="👋")
        self.driver.get("https://x.com/i/flow/login")
        time.sleep(5)
        
        user = os.getenv("X_USER")
        password = os.getenv("X_PASS")
        
        # 3. Attempt Automated Entry
        if user and password:
            try:
                # Username
                print("Entering username...")
                user_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
                )
                user_input.send_keys(user)
                user_input.send_keys(Keys.RETURN)
                time.sleep(2)
                
                # Challenge (Email/Phone) often requested
                try:
                    challenge = self.driver.find_elements(By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']")
                    if challenge:
                         print("Handling login challenge...")
                         challenge[0].send_keys(user) 
                         challenge[0].send_keys(Keys.RETURN)
                         time.sleep(2)
                except: pass
                
                # Password
                print("Entering password...")
                pass_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                pass_input.send_keys(password)
                pass_input.send_keys(Keys.RETURN)
                
                time.sleep(5)
                if self._is_logged_in():
                    st.success("Auto-Login Successful!")
                    return True
                    
            except Exception as e:
                 print(f"Auto-login skipped/failed: {e}")

        # 4. Manual Wait Loop (Critical Fix)
        st.warning("⚠️ AUTOMATION PAUSED: Please Log In manually in the browser window!")
        st.info("I am waiting for you to see the 'Home' screen...")
        
        max_wait = 120 # Wait up to 2 minutes
        for i in range(max_wait):
            if i % 5 == 0:
                print(f"Waiting for manual login... {i}/{max_wait}")
            
            if self._is_logged_in():
                st.success("Manual Login Detected! Resuming...")
                return True
            time.sleep(1)
            
        st.error("Login Timed Out. Aborting.")
        return False

    def _is_logged_in(self):
        """Helper to detect valid session"""
        src = self.driver.page_source.lower()
        # 'compose' button or 'account' menu usually indicates login
        if "compose" in src or "logout" in src or "account" in src:
            return True
        # Check URL as fallback
        if "x.com/home" in self.driver.current_url:
            return True
        return False

    def hunt_strategic_engagement(self, query, location, days_back=30, limit=30):
        """
        WORKFLOW B: Keyword + Engagement Harvesting.
        1. Search for tweets (Keyword + Date + Location).
        2. Scrape the AUTHOR.
        3. Click into tweet and scrape COMMENTERS (High Interest).
        """
        if not self.driver:
            self._setup_driver()
        self._login()

        # 1. Construct Advanced Query
        # "interior design" near:"KL" within:20km since:2024-12-01
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        full_query = f'"{query}" since:{since_date}'
        if location:
             full_query += f' near:"{location}" within:20km'
        
        # We assume the user wants 'Top' or 'Live'. 'Live' is better for "last month" coverage.
        encoded_query = urllib.parse.quote(full_query)
        search_url = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"
        
        st.toast(f"Hunting: {full_query[:30]}...", icon="🕷️")
        print(f"Executing Search: {full_query}")
        
        self.driver.get(search_url)
        time.sleep(5)
        
        total_leads = 0
        processed_tweets = set()
        
        # Selector for feed tweets
        tweet_xpath = "//article[@data-testid='tweet']"
        
        main_scroll_attempts = 0
        while total_leads < limit and main_scroll_attempts < 10:
            try:
                # Find tweets in feed
                try:
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, tweet_xpath)))
                except: pass
                
                feed_cards = self.driver.find_elements(By.XPATH, tweet_xpath)
                
                # Iterate through visible tweets
                for i in range(len(feed_cards)):
                    if total_leads >= limit: break
                    
                    # refresh element list to avoid stale reference after navigation
                    feed_cards = self.driver.find_elements(By.XPATH, tweet_xpath)
                    if i >= len(feed_cards): break
                    card = feed_cards[i]
                    
                    try:
                        # Extract basic info to identify tweet
                        user_el = card.find_element(By.XPATH, ".//div[@data-testid='User-Name']")
                        raw_user = user_el.text.split("\n")
                        author_name = raw_user[0]
                        author_handle = next((s for s in raw_user if s.startswith("@")), "Unknown")
                        
                        time_el = card.find_element(By.TAG_NAME, "time")
                        tweet_link = time_el.find_element(By.XPATH, "..").get_attribute("href")
                        
                        if tweet_link in processed_tweets: continue
                        processed_tweets.add(tweet_link)
                        
                        # --- PART A: Scrape Author ---
                        tweet_text_el = card.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                        tweet_text = tweet_text_el.text
                        
                        st.toast(f"Author: {author_handle}", icon="✍️")
                        db.add_lead(author_name, author_handle, f"X Author ({query})", tweet_text[:200], tweet_link)
                        total_leads += 1
                        
                        # --- PART B: Drill Down for Comments ---
                        # Only if we aren't at limit
                        if total_leads >= limit: break
                        
                        print(f"  > Drilling into {author_handle}'s tweet...")
                        
                        # Click to open thread (using JS to avoid interception)
                        self.driver.execute_script("arguments[0].click();", time_el)
                        time.sleep(4)
                        
                        # Scrape Replies
                        reply_xpath = "//article[@data-testid='tweet']" # Reuse same selector for replies
                        try:
                            WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.XPATH, reply_xpath)))
                            replies = self.driver.find_elements(By.XPATH, reply_xpath)
                            
                            # Skip first one (it's the original tweet usually)
                            for r in replies[1:]:
                                if total_leads >= limit: break
                                try:
                                    r_user_el = r.find_element(By.XPATH, ".//div[@data-testid='User-Name']")
                                    r_raw = r_user_el.text.split("\n")
                                    r_name = r_raw[0]
                                    r_handle = next((s for s in r_raw if s.startswith("@")), None)
                                    
                                    if r_handle and r_handle != author_handle:
                                        r_text = r.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                                        
                                        st.toast(f"Commenter: {r_handle}", icon="💬")
                                        db.add_lead(r_name, r_handle, f"X Commenter ({query})", r_text[:200], tweet_link)
                                        total_leads += 1
                                except: continue
                        except: 
                            print("  > No replies loaded.")
                        
                        # Go Back to Feed
                        self.driver.back()
                        time.sleep(3)
                        
                    except Exception as e:
                        # print(f"Tweet processing error: {e}")
                        continue
                
                # Scroll Feed
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                main_scroll_attempts += 1
                
            except Exception as e:
                print(f"Main Loop Error: {e}")
                main_scroll_attempts += 1
                
        return total_leads
        

    def close(self):
        if self.driver:
            try: self.driver.quit()
            except: pass

