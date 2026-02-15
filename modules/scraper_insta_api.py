
import os
import json
import streamlit as st
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    TwoFactorRequired, FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)
from dotenv import load_dotenv

load_dotenv()

class InstagramHunterAPI:
    def __init__(self):
        self.cl = Client()
        self.session_file = "insta_session.json"
        
        # --- MONKEY PATCH FOR PYDANTIC VALIDATION ERROR ---
        try:
            from instagrapi.types import ClipsMetadata, ClipsOriginalSoundInfo
            from typing import Optional
            
            # Allow original_sound_info to be None (Fix for "Input should be a valid dictionary or instance")
            if 'original_sound_info' in ClipsMetadata.model_fields:
                # Update Pydantic v2 field definition
                ClipsMetadata.model_fields['original_sound_info'].annotation = Optional[ClipsOriginalSoundInfo]
                ClipsMetadata.model_fields['original_sound_info'].default = None
                
                # Force rebuild of the model schema
                if hasattr(ClipsMetadata, 'model_rebuild'):
                    ClipsMetadata.model_rebuild(force=True)
                    
            print(">>> DEBUG: PATCHED Instagrapi ClipsMetadata Schema <<<")
        except Exception as e:
            print(f"Patch warning: {e}")
        # --------------------------------------------------
        
    def login(self, username, password):
        """
        Logs in using the private mobile API.
        Handles session file corruption/expiration automatically.
        """
        import time
        try:
            # 1. Try loading session
            if os.path.exists(self.session_file):
                try:
                    print("Loading session from file...")
                    self.cl.load_settings(self.session_file)
                    
                    # Verify session validity by doing a lightweight call?
                    # Actually, instagrapi validates on first call usually. 
                    # But let's trust load_settings unless it throws.
                    # We'll just proceed. If calls fail, we handle there.
                    st.success("API Session Loaded")
                    return True
                except Exception as e:
                    print(f"Session load warning: {e}")
                    pass 

            # 2. Fresh Login (if session missing or we forced reload)
            st.toast("Authenticating with Instagram API...", icon="🔐")
            time.sleep(1)
            self.cl.login(username, password)
            
            # Save new session
            self.cl.dump_settings(self.session_file)
            st.success("API Login Successful")
            return True
            
        except TwoFactorRequired:
            st.error("2FA Required. Please disable 2FA or use an app password if possible.")
            return False
        except ChallengeRequired:
            st.error("Instagram Checkpoint (Challenge). Please open Instagram on your phone and approve 'This was me'.")
            st.warning("Do NOT delete the session file yet. After approving, wait 30 seconds and try again.")
            
            # CRITICAL: Save the session (device settings) so the Next Attempt uses the SAME Device ID
            # If we don't save, the next attempt uses a new device ID, triggering a loop.
            try:
                self.cl.dump_settings(self.session_file)
            except: pass
            
            return False
        except BadPassword:
            st.error("Incorrect Password. Clearing session and retrying...")
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                st.info("Old session removed. Please try running the scraper again to force a new login.")
            return False
        except Exception as e:
            st.error(f"API Login Error: {e}")
            # If completely failed, remove bad session
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return False

    def scrape_hashtag(self, hashtag, max_posts=50, username=None, password=None):
        import time
        import random
        leads = []
        seen_users = set()
        
        try:
            # Credentials
            final_user = username if username else os.getenv("INSTA_USER")
            final_pass = password if password else os.getenv("INSTA_PASS")
            
            if not final_user or not final_pass:
                st.error("Username/Password required for API Mode.")
                return []

            # Login
            if not self.login(final_user, final_pass):
                return []
            
            # --- SCRAPE LOGIC ---
            tag = hashtag.replace("#", "")
            st.toast(f"Fetching top {max_posts} media for #{tag}...", icon="📡")
            
            try:
                # Fetch Medias
                medias = self.cl.hashtag_medias_top(tag, amount=max_posts)
            except Exception as e:
                # Catch LoginRequired logic manually to be safe
                if "login_required" in str(e).lower():
                    st.warning("Session expired/invalid. Performing Hard Reset...")
                    
                    # 1. Kill Session File
                    if os.path.exists(self.session_file):
                        os.remove(self.session_file)
                    
                    # 2. Re-init Client (Clear internal state)
                    # We need to re-import Client to be safe or use self.cl class
                    from instagrapi import Client
                    self.cl = Client()
                    
                    # 3. Fresh Login
                    time.sleep(3)
                    if self.login(final_user, final_pass):
                         st.toast("Hard Reset Successful. Retrying fetch...", icon="🔄")
                         time.sleep(5) # Cooldown
                         medias = self.cl.hashtag_medias_top(tag, amount=max_posts)
                    else:
                        st.error("Hard Re-Login Failed.")
                        return []
                else:
                    raise e
            
            total_items = len(medias)
            st.info(f"Found {total_items} posts. Extracting & enriching details...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, media in enumerate(medias):
                try:
                    # Update Progress
                    progress = (i + 1) / total_items
                    progress_bar.progress(progress)
                    
                    user = media.user
                    if user.username in seen_users:
                        continue
                    seen_users.add(user.username)
                    
                    status_text.text(f"Enriching: {user.username}...")
                    
                    # --- ENRICHMENT STEP ---
                    delay = 1.5 + random.random() # Reduced slightly
                    time.sleep(delay)
                    
                    try:
                        full_user = self.cl.user_info(user.pk)
                        
                        email = full_user.public_email
                        phone = full_user.contact_phone_number
                        website = full_user.external_url
                        bio = full_user.biography
                        
                        # Extra Hunt: Check Bio for Email
                        if not email and bio:
                            import re
                            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                            found = re.findall(email_pattern, bio)
                            if found:
                                email = found[0]

                        category = full_user.category
                        
                        leads.append({
                            "Username": full_user.username,
                            "Name": full_user.full_name,
                            "Profile": f"https://www.instagram.com/{full_user.username}",
                            "Source": "Instagram API",
                            "Email": email if email else "N/A",
                            "Phone": phone if phone else "N/A",
                            "Website": website if website else f"https://www.instagram.com/{full_user.username}",
                            "Notes": bio[:200] if bio else "",
                            "Group": category if category else "N/A",
                            "Caption": media.caption_text[:100] if media.caption_text else ""
                        })
                    except Exception as enrichment_err:
                        # Soft fail for individual user enrichment
                        # If 429/LoginRequired, maybe we should stop?
                        if "login_required" in str(enrichment_err).lower():
                            st.warning("Rate limit hit or session killed properly. Stopping early.")
                            break
                            
                        # Otherwise just fallback to basic
                        leads.append({
                            "Username": user.username,
                            "Name": user.full_name,
                            "Profile": f"https://www.instagram.com/{user.username}",
                            "Website": f"https://www.instagram.com/{user.username}", # Guaranteed Link
                            "Source": "Instagram API (Basic)",
                            "Caption": media.caption_text[:100] if media.caption_text else ""
                        })

                except Exception as e:
                    pass
            
            status_text.text("Enrichment Complete!")
            return leads

        except Exception as e:
            st.error(f"API Scrape Error: {e}")
            return []

    def close(self):
        # Nothing to close for API client usually, maybe save settings
        pass
