import streamlit as st
import pandas as pd
import os
import sys
import asyncio
import time
import glob
import pydeck as pdk
import streamlit_shadcn_ui as ui
import importlib

from dotenv import load_dotenv

# --- COMPATIBILITY PATCH ---
import sys
# SHIM: Redirect moviepy -> moviepy.editor (v1.x compatibility)
# Code uses v2-style `from moviepy import X`, but v1.x has classes in moviepy.editor
try:
    import moviepy.editor as _moviepy_editor
    sys.modules["moviepy"] = _moviepy_editor
except ImportError:
    pass

if sys.version_info >= (3, 12):
    import setuptools
    try:
        from distutils.version import LooseVersion
    except ImportError:
        from setuptools._distutils.version import LooseVersion
        import types
        sys.modules['distutils'] = types.ModuleType('distutils')
        sys.modules['distutils.version'] = types.ModuleType('distutils.version')
        sys.modules['distutils.version'].LooseVersion = LooseVersion

# Import Modules
from modules.crm import LeadManager
from modules.visuals import StudioGallery
# from modules.outreach_whatsapp import WhatsAppSniper # Moved local
from modules.outreach_email import EmailBlaster
import urllib.parse
from modules.ai_engine import AIGhostwriter, VisualStudio
from modules.cinema import CinemaDirector
from modules.presenter import PresenterProducer
from modules.architect import VoltsArchitect
from modules.voice_studio import VoiceStudio
from modules.outreach_voice import CallCenter
from modules import ui_components as uic
importlib.reload(uic)
from modules import db_supabase as db
importlib.reload(db)

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="VOLTS | Growth Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PAYMENT VERIFICATION ---
import modules.auth as auth_module
from modules.payments import gateway

# Check for Stripe callback
if "session_id" in st.query_params:
    session_id = st.query_params["session_id"]
    with st.spinner("Verifying secure payment..."):
        is_valid, email, tier = gateway.verify_session(session_id)
        
        if is_valid and email:
            if auth_module.upgrade_user_by_email(email, tier):
                st.success(f"PAYMENT SUCCESS! Account upgraded to {tier}. Please log in again if needed.")
                st.balloons()
            else:
                st.error("Payment received, but user not found. Please contact support.")
        else:
            # st.error("Invalid or expired payment session.")
            pass
            
    # Clear param to prevent loop
    st.query_params.clear()

# --- RELIABILITY & BACKUP ---
try:
    import sentry_sdk
    if os.getenv("SENTRY_DSN"):
        sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)
except ImportError:
    pass

try:
    from modules.backup import perform_backup
    perform_backup()
except Exception as e:
    print(f"Backup failed: {e}")

# --- INIT DB (Must run before auth) ---
db.init_db()

# --- GLOBAL AUTH GATE ---
import modules.auth as auth_module

if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["user"]:
    # Show Landing Page + Login
    uic.apply_custom_css()
    
    from modules.landing_page import render_landing_page, render_features_grid
    
    # Render Hero and get the login container
    auth_container = render_landing_page()
    
    with auth_container:
        tab_login, tab_signup = st.tabs([" Login", " Sign Up"])
        
        with tab_login:
            email = st.text_input("Email", key="global_login_email")
            password = st.text_input("Password", type="password", key="global_login_pass")
            if st.button("Login", type="primary", use_container_width=True):
                if email and password:
                    user_data = auth_module.login(email, password)
                    if user_data:
                        st.session_state["user"] = user_data
                        st.success("Login successful!")
                        st.toast(f"Welcome back, {email.split('@')[0]}!", icon="")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                else:
                    st.error("Please enter email and password.")
            
            # --- Password Reset ---
            st.markdown("---")
            with st.expander("Forgot Password?"):
                reset_email = st.text_input("Enter your account email", key="reset_email")
                if st.button("Send Reset Code"):
                    if not reset_email:
                        st.error("Please enter email.")
                    else:
                        success, token = auth_module.generate_reset_token(reset_email)
                        if success:
                            # Send Email (Lazy import to avoid circular dependency if any)
                            from modules.outreach_email import EmailBlaster
                            try:
                                blaster = EmailBlaster()
                                if blaster.connect():
                                    subject = "VOLTS Password Reset Code"
                                    body = f"Your reset code is: <b>{token}</b><br>Expires in 15 minutes."
                                    sent, msg = blaster.send_single_email(reset_email, subject, body)
                                    blaster.close()
                                    if sent:
                                        st.success(f"Code sent to {reset_email}!")
                                        st.session_state["reset_email_sent"] = reset_email
                                    else:
                                        st.error(f"Failed to send email: {msg}")
                                else:
                                    st.error("Email service unavailable. Check .env settings.")
                            except Exception as e:
                                st.error(f"Email Error: {e}")
                        else:
                            st.error(token) # Error msg
                
                if "reset_email_sent" in st.session_state:
                    st.divider()
                    st.info(f"Resetting for: {st.session_state['reset_email_sent']}")
                    reset_code = st.text_input("Enter 6-digit Code", key="reset_code")
                    new_pass_reset = st.text_input("New Password", type="password", key="reset_new_pass")
                    
                    if st.button("Reset Password", type="secondary"):
                        valid, msg = auth_module.reset_password_with_token(
                            st.session_state["reset_email_sent"], 
                            reset_code, 
                            new_pass_reset
                        )
                        if valid:
                            st.success("Password reset! You can now login.")
                            del st.session_state["reset_email_sent"]
                        else:
                            st.error(msg)
        
        with tab_signup:
            new_email = st.text_input("Email", key="global_signup_email")
            new_pass = st.text_input("Password", type="password", key="global_signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="global_signup_confirm")
            if st.button("Create Account", type="primary", use_container_width=True):
                if not new_email or not new_pass:
                    st.error("Please fill in all fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    success, msg = auth_module.signup(new_email, new_pass)
                    if success:
                        st.success("Account created! Logging in...")
                        user_data = auth_module.login(new_email, new_pass)
                        st.session_state["user"] = user_data
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
    
    # Show Features Grid below the fold
    render_features_grid()
    st.stop()
    
# --- USER IS LOGGED IN ---
current_user = st.session_state["user"]
user_tier = current_user.get("tier", "FREE")
user_id = current_user.get("id")
try:
    user_id = int(user_id) if user_id is not None else None
except:
    pass

# --- APPLY GLOBAL CSS THEME ---
uic.apply_custom_css()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    if os.path.exists("logo_transparent.png"):
        st.image("logo_transparent.png", width=120)
    else:
        st.header("VOLTS")
        
    st.caption("ULTIMATE ACQUISITION SYSTEM")
    
    # Build menu based on tier
    menu_items = [
        "Lead Search",
        "Pipeline / CRM",
        "Content Studio",
        "AI Dialer",
    ]
    
    # Settings is for all users; Admin is for ADMIN only
    menu_items.append("Settings")
    if user_tier == "ADMIN":
        menu_items.append("️ Admin")
    
    page = st.radio("NAVIGATION", menu_items, label_visibility="collapsed")
    
    st.markdown("---")
    
    # User Info
    st.caption(f" {current_user.get('email', 'User')}")
    st.caption(f" {user_tier} Plan")
    if st.button(" Logout", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()
    
    # System Health (Admin Only)
    if user_tier == "ADMIN":
        st.markdown("---")
        st.markdown("### System Health")
        uic.card_system_status(title="GEMINI AI", status="Active" if os.getenv("GEMINI_API_KEY") else "Inactive", description="Reasoning Engine", key="status_gemini")
        uic.card_system_status(title="REPLICATE", status="Active" if os.getenv("REPLICATE_API_TOKEN") else "Inactive", description="Vision Models", key="status_rep")
        uic.card_system_status(title="11LABS", status="Active" if os.getenv("ELEVENLABS_API_KEY") else "Inactive", description="Voice Synthesis", key="status_11")
        uic.card_system_status(title="TWILIO", status="Active" if os.getenv("TWILIO_SID") else "Inactive", description="Global Telephony", key="status_twilio")


# --- MODULE 1: LEAD SEARCH ---
if "Lead Search" in page:
    st.title("Lead Search")
    st.caption("Find and enrich high-value prospects from multiple sources.")
    st.markdown("---")
    
    # Hunter Interface
    # Hunter Interface
    # Prioritizing Stable Scrapers for SaaS Launch
    chosen_tab = ui.tabs(options=["GOOGLE MAPS", "LINKEDIN X-RAY", "LABS"], default_value="GOOGLE MAPS", key="hunter_tabs")
    
    st.write("") # Spacer
    
    # Container for the active hunter
    with st.container(border=True):
        if chosen_tab == "GOOGLE MAPS":
            tab_control, tab_db = st.tabs([" Search", "️ Results"])
            
            with tab_control:
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.subheader("/// MAPS_AGENT")
                    keyword = st.text_input("SEARCH QUERY", "Luxury Interior Design", help="e.g. Architects in KL")
                    
                    # Browser Selector
                    browser_choice = st.radio("BROWSER ENGINE", ["Edge (Recommended)", "Chrome"], index=0, horizontal=True, help="Edge is usually more stable on Windows. Chrome may be faster but riskier.")
                    engine_map = {"Edge (Recommended)": "Edge", "Chrome": "Chrome"}
                    
                    # Target Leads Slider
                    target_limit = st.slider("TARGET LEADS", min_value=5, max_value=100, value=20, step=5, help="How many leads to extract? Higher numbers take longer.")
                    
                    st.write("")
                    
                    # Stop button state
                    if "maps_scanning" not in st.session_state:
                        st.session_state.maps_scanning = False
                    
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        start_scan = st.button("▶ Start Scan", key="btn_maps", type="primary", use_container_width=True, disabled=st.session_state.maps_scanning)
                    with btn_col2:
                        stop_scan = st.button("⏹ Stop", key="btn_maps_stop", use_container_width=True, disabled=not st.session_state.maps_scanning)
                    
                    if stop_scan:
                        st.session_state.maps_scanning = False
                        st.toast("Scan stopped by user.", icon="⏹")
                    
                    if start_scan:
                        st.session_state.maps_scanning = True
                        uic.log_message(f"Starting Maps Search for {keyword}...")
                        
                        with st.status(f" Scanning for '{keyword}'...", expanded=True) as status:
                            try:
                                st.write("Initializing browser engine...")
                                from modules.scraper_maps import MapsHunter
                                hunter = MapsHunter(browser_type=engine_map[browser_choice])
                                
                                st.write(f" Opening Google Maps (Engine: {engine_map[browser_choice]})...")
                                leads = hunter.scan(keyword, limit=target_limit)
                                hunter.close()
                                
                                st.session_state.maps_scanning = False
                                
                                if leads:
                                    st.write(f" Saving {len(leads)} leads to database...")
                                    count = LeadManager.add_lead(leads, user_id=user_id)
                                    uic.log_message(f"Scan Complete. {count} found.")
                                    status.update(label=f"Complete — {count} leads added!", state="complete", expanded=False)
                                    st.balloons()
                                else:
                                    status.update(label="No results found", state="error", expanded=False)
                            except Exception as e:
                                st.session_state.maps_scanning = False
                                hunter_ref = locals().get('hunter')
                                if hunter_ref:
                                    try: hunter_ref.close()
                                    except: pass
                                status.update(label=f"Error: {str(e)[:80]}", state="error", expanded=True)
                                st.error(f"Scan failed: {e}")

                with c2:
                    if st.session_state.get("maps_scanning"):
                        st.warning("Scan in progress...")
                    else:
                        st.info("Status: Ready")

            with tab_db:
                st.subheader(" GOOGLE MAPS DATABASE")
                import modules.db_supabase as db
                try:
                    conn = db.get_connection()
                    if conn:
                        c = conn.cursor(cursor_factory=db.RealDictCursor)
                        c.execute("SELECT * FROM leads WHERE source = 'Google Maps' AND user_id = %s ORDER BY id DESC", (user_id,))
                        data = c.fetchall()
                        conn.close()
                        
                        df_maps = pd.DataFrame(data)
                        if not df_maps.empty:
                            st.dataframe(df_maps, use_container_width=True, hide_index=True)
                            csv_data = df_maps.to_csv(index=False).encode('utf-8')
                            st.download_button(" DOWNLOAD MAPS DATA", data=csv_data, file_name="maps_leads.csv", mime="text/csv", type="primary", key="dl_maps")
                        else:
                            st.info("Cloud database empty. Run a scan to populate.")
                    else:
                        st.warning("Cloud database is currently offline (Supabase may be paused).")
                    
                    # Also show offline leads if any exist
                    if os.path.exists(db.OFFLINE_CSV):
                        st.divider()
                        st.caption("OFFLINE LEADS (Saved locally when cloud was down)")
                        df_offline = pd.read_csv(db.OFFLINE_CSV)
                        if not df_offline.empty:
                            st.dataframe(df_offline, use_container_width=True, hide_index=True)
                            csv_offline = df_offline.to_csv(index=False).encode('utf-8')
                            st.download_button("DOWNLOAD OFFLINE DATA", data=csv_offline, file_name="offline_leads.csv", mime="text/csv", key="dl_offline")
                except Exception as e:
                    st.error(f"Database error: {e}")
                
        elif chosen_tab == "LABS":
            st.info("Experimental Features — May require maintenance or be subject to rate limits.")
            
            lab_tab = ui.tabs(options=["IPROPERTY", "PROP GURU"], default_value="IPROPERTY", key="lab_tabs")
            
            if lab_tab == "FACEBOOK":
                tab_control, tab_db = st.tabs(["LAUNCHPAD", "DATABASE"])
                
                with tab_control:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.subheader("/// FACEBOOK_OPERATIONS")
                        
                        fb_mode = ui.tabs(options=["GROUP MONITOR", "MARKETPLACE", "AUTO-COMMENTER"], default_value="GROUP MONITOR", key="fb_tabs")
                        st.write("")

                        # Cookie Management (Advanced)
                        with st.expander("Authentication / Cookies (Unlocker)", expanded=False):
                            st.info("If scraping fails (Login/Timeout), export cookies from your browser (Netscape format) and paste below.")
                            cookie_data = st.text_area("Paste Netscape Cookie Content:", height=100, placeholder="# Netscape HTTP Cookie File\n.facebook.com ...")
                            if st.button("SAVE_COOKIES"):
                                if cookie_data.strip():
                                    with open("cookies.txt", "w", encoding="utf-8") as f:
                                        f.write(cookie_data)
                                    st.success("COOKIES SAVED. Rerun scraper.")
                                else:
                                    st.warning("EMPTY INPUT")
                        
                        if fb_mode == "GROUP MONITOR":
                            url = st.text_input("GROUP URL", "", placeholder="https://web.facebook.com/groups/...", help="Supports Desktop, Mobile, and Share links.")
                            st.info("Headless Mode: ON. Browser will run silently.")
                            if st.button("Initialize Sequence", key="btn_fb_group"):
                                 uic.log_message(f"Deploying Facebook Hunter on {url}")
                                 with st.status("Launching Facebook Group Hunter...", expanded=True) as status:
                                     try:
                                         from modules.scraper_fb import FacebookHunter
                                         hunter = FacebookHunter()
                                         # Use wildcard '*' to capture ALL posts for now to debug
                                         st.write(f"Scanning feed for {url}...")
                                         count = hunter.hunt_group(url, ["*"], 3, user_id=user_id)
                                         hunter.close()
                                         
                                         if count: 
                                             status.update(label=f"Success: Extracted {count} leads", state="complete", expanded=False)
                                             st.success(f"EXTRACTED {count} LEADS")
                                             # Notify User
                                             from modules.notifications import SystemAlert
                                             SystemAlert().send_alert("FB Group Scraper", f"Found {count} leads in {url}")
                                         else: 
                                             status.update(label="No targets found", state="error", expanded=False)
                                             st.warning("NO TARGETS FOUND")
                                     except Exception as e:
                                         status.update(label="Scraper Failed", state="error", expanded=True)
                                         st.error(f"Error: {e}")

                        elif fb_mode == "MARKETPLACE":
                            with st.expander("HOW TO USE MARKETPLACE SCRAPER"):
                                st.markdown("""
                                1. **Go to Facebook Marketplace** in your browser.
                                2. **Set your location** (e.g. Kuala Lumpur, New York).
                                3. **Copy the URL** from your browser address bar. 
                                   - Example: `https://www.facebook.com/marketplace/106648709374092/`
                                4. Paste it into **CITY URL** below.
                                5. Enter your **ITEM QUERY** (e.g., 'Sofa').
                                """)
                            
                            query = st.text_input("ITEM QUERY", "Sofa", help="What are people selling? e.g. 'Old Furniture'")
                            city_url = st.text_input("CITY URL (Optional)", "", help="Paste a FB Marketplace City URL to target a specific area.")
                            limit = st.slider("MAX LISTINGS", 5, 100, 20, help="How many items to scan?")
                            
                            if st.button("Scan Marketplace", key="btn_fb_market"):
                                uic.log_message(f"Scanning Marketplace for {query} ({limit} items)...")
                                with st.spinner(">> EXEC: Analyzing Listings..."):
                                     from modules.scraper_fb import FacebookHunter
                                     hunter = FacebookHunter()
                                     count = hunter.hunt_marketplace(city_url, query, limit=limit, user_id=user_id)
                                     hunter.close()
                                     if count:
                                         st.success(f"FOUND {count} LISTINGS")
                                         from modules.notifications import SystemAlert
                                         SystemAlert().send_alert("Marketplace Scraper", f"Found {count} listings for '{query}'")
                                     else:
                                         st.warning("NO LISTINGS FOUND")

                        elif fb_mode == "AUTO-COMMENTER":
                            st.subheader("AUTO-COMMENTER (BETA)")
                            st.warning("BETA FEATURE: Uses mbasic.facebook.com for stealth. Works best on public posts.")
                            with st.expander("GUIDE"):
                                st.markdown("""
                                - **Post URL**: Must be a public post link. Share links (fb.share...) might not work.
                                - **Comment**: Keep it simple to avoid spam filters.
                                - **Privacy**: Feature uses your local session cookies.
                                """)
                                
                            post_url = st.text_input("POST URL", "")
                            comment = st.text_area("COMMENT TEXT", "Hi! I saw you're looking for renovation. Pm me?")
                            
                            if st.button("DEPLOY COMMENT", type="primary"):
                                if not post_url or not comment:
                                    st.warning("Missing Input")
                                else:
                                    with st.spinner(">> EXEC: Posting..."):
                                         from modules.scraper_fb import FacebookHunter
                                         hunter = FacebookHunter()
                                         success = hunter.auto_comment(post_url, comment)
                                         hunter.close()
                                         if success:
                                             st.success("COMMENT POSTED")
                                             from modules.notifications import SystemAlert
                                             SystemAlert().send_alert("Auto-Commenter", f"Successfully commented on {post_url}")
                                         else:
                                             st.error("FAILED TO POST")
                    with c2:
                        st.markdown("#### STATUS_MONITOR")
                        uic.card_system_status("FACEBOOK", "Active", "Graph API / Scraper", "fb_stat")
                
                with tab_db:
                    st.subheader("FACEBOOK DATABASE")
                    import modules.db_supabase as db
                    try:
                        conn = db.get_connection()
                        c = conn.cursor(cursor_factory=db.RealDictCursor)
                        c.execute("SELECT * FROM leads WHERE (source LIKE 'Facebook%%' OR source LIKE 'Marketplace%%') AND user_id = %s ORDER BY id DESC", (user_id,))
                        data = c.fetchall()
                        conn.close()
                        df_fb = pd.DataFrame(data)
                    except Exception as e:
                        st.error(f"Error fetching Facebook data: {e}")
                        df_fb = pd.DataFrame()
                        
                    if not df_fb.empty:
                        # Fix: Convert created_at to datetime for Streamlit
                        if 'created_at' in df_fb.columns:
                            df_fb['created_at'] = pd.to_datetime(df_fb['created_at'], errors='coerce')

                        # Configure Columns for better UX
                        st.data_editor(
                            df_fb,
                            column_config={
                                "name": st.column_config.TextColumn("Item / Name", width="medium"),
                                "company": st.column_config.TextColumn("Price", help="Item Price"),
                                "role": st.column_config.TextColumn("Type", help="Listing Type"),
                                "location": st.column_config.TextColumn("Location"),
                                "profile_url": st.column_config.LinkColumn("Link", display_text="View Listing"),
                                "created_at": st.column_config.DatetimeColumn("Scraped At", format="D MMM, HH:mm"),
                                # Hide internal columns
                                "id": None,
                                "phone_number": None,
                                "email": None,
                                "status": st.column_config.SelectboxColumn("Status", options=["New", "Contacted", "Closed"])
                            },
                            use_container_width=True,
                            hide_index=True,
                            key="fb_editor"
                        )
                    else:
                        st.info("No Facebook data found.")

        elif chosen_tab == "LABS":
            st.info("Experimental Features — May require maintenance or be subject to rate limits.")
            
            lab_tab = ui.tabs(options=["IPROPERTY", "PROP GURU"], default_value="IPROPERTY", key="lab_tabs")
            
            if lab_tab == "IPROPERTY":
                tab_control, tab_db = st.tabs([" LAUNCHPAD", "️ DATABASE"])
            
                with tab_control:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                         st.subheader("/// IPROPERTY_ORACLE")
                         query = st.text_input("PROPERTY TYPE", "Balcony", help="Filter by features or types.")
                         loc = st.text_input("LOCATION SLUG", "kuala-lumpur", help="e.g. 'mont-kiara', 'petaling-jaya'")
                         
                         # New Controls
                         col_a, col_b = st.columns(2)
                         with col_a:
                             days = st.slider("LOOKBACK (DAYS)", 1, 90, 15, key="ip_days")
                         with col_b:
                             limit = st.slider("TARGET AGENTS", 10, 200, 30, key="ip_limit")
                         
                         if st.button("Initialize Sequence", key="btn_iprop"):
                             uic.log_message(f"Deploying iProperty Hunter in {loc} (Last {days} days)...")
                             uic.log_message(f"Deploying iProperty Hunter in {loc} (Last {days} days)...")
                             with st.status(f" Scanning iProperty ({loc})...", expanded=True) as status:
                                 try:
                                     from modules.scraper_iproperty import IPropertyHunter
                                     hunter = IPropertyHunter()
                                     st.write("Accessing property listings...")
                                     count = hunter.hunt_listings(query, loc, days_back=days, limit=limit, user_id=user_id)
                                     hunter.close()
                                     
                                     if count:
                                         status.update(label=f"Found {count} Agents", state="complete", expanded=False)
                                         st.success(f"EXTRACTED {count} AGENTS")
                                         from modules.notifications import SystemAlert
                                         SystemAlert().send_alert("iProperty Scraper", f"Found {count} agents in {loc}")
                                     else: 
                                         status.update(label="No targets found", state="error", expanded=False)
                                         st.warning("NO TARGETS FOUND")
                                 except Exception as e:
                                     status.update(label="Scraper Error", state="error", expanded=True)
                                     st.error(f"Error: {e}")
                    with c2:
                         st.markdown("#### STATUS_MONITOR")
                         uic.card_system_status("IPROPERTY", "Inactive", "API Beta", "ip_stat")
    
                with tab_db:
                    st.subheader(" IPROPERTY DATABASE")
                    import modules.db_supabase as db
                    try:
                        conn = db.get_connection()
                        c = conn.cursor(cursor_factory=db.RealDictCursor)
                        c.execute("SELECT * FROM leads WHERE source LIKE 'iProperty%%' AND user_id = %s ORDER BY id DESC", (user_id,))
                        data = c.fetchall()
                        conn.close()
                        
                        df_ip = pd.DataFrame(data)
                        if not df_ip.empty:
                            st.dataframe(df_ip, use_container_width=True, hide_index=True)
                        else:
                            st.info("No iProperty data found.")
                    except Exception as e:
                        st.error(f"Error loading iProperty data: {e}")

            elif lab_tab == "PROP GURU":
                tab_control, tab_db = st.tabs([" LAUNCHPAD", "️ DATABASE"])
            
                with tab_control:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                          st.subheader("/// PROPERTY_SCANNER (GOD MODE)")
                          st.caption("Strategy: Session Persistence + Automated Pagination")
                          
                          query = st.text_input("SEARCH QUERY", "Balcony", key="pg_query")
                          loc = st.text_input("LOCATION", "kuala-lumpur", key="pg_loc", help="kuala-lumpur, selangor, penang, johor")
                          limit = st.slider("TARGET AGENTS", 10, 200, 30, key="pg_limit")
                          
                          if st.button("Initialize Sequence", key="btn_prop"):
                              from modules.scraper_propguru import PropGuruHunter
                              uic.log_message(f"Deploying Property Hunter (Target: {limit} agents)...")
                              
                              with st.spinner(">> EXEC: Bypassing Defense Systems..."):
                                  hunter = PropGuruHunter()
                                  count = hunter.hunt_listings(query=query, location=loc, limit=limit, user_id=user_id)
                                  hunter.close()
                                  
                                  if count:
                                      st.success(f"EXTRACTED {count} AGENTS")
                                      from modules.notifications import SystemAlert
                                      SystemAlert().send_alert("PropertyGuru Scraper", f"Found {count} agents in {loc}")
                                  else:
                                      st.warning("NO TARGETS FOUND (Check Cloudflare)")
                with c2:
                         st.markdown("#### STATUS_MONITOR")
                         uic.card_system_status("PROPGURU", "Inactive", "API Beta", "pg_stat")
    
                with tab_db:
                    st.subheader(" PROPERTY GURU DATABASE")
                    import modules.db_supabase as db
                    try:
                        conn = db.get_connection()
                        c = conn.cursor(cursor_factory=db.RealDictCursor)
                        c.execute("SELECT * FROM leads WHERE source LIKE 'PropertyGuru%%' AND user_id = %s ORDER BY id DESC", (user_id,))
                        data = c.fetchall()
                        conn.close()
                        
                        df_pg = pd.DataFrame(data)
                        if not df_pg.empty:
                            st.dataframe(df_pg, use_container_width=True, hide_index=True)
                        else:
                            st.info("No PropertyGuru data found.")
                    except Exception as e:
                        st.error(f"Error loading PropertyGuru data: {e}")

        elif chosen_tab == "LINKEDIN X-RAY":
            st.subheader("LinkedIn X-Ray")
            st.caption("Find professionals via Google Search (No Login Required).")
            
            tab_control, tab_db = st.tabs([" Search", "️ Results"])
            
            with tab_control:
                c1, c2 = st.columns([2, 1])
                with c1:
                    role = st.text_input("Target Role", "Project Manager", help="e.g. Property Developer, Facilities Manager")
                    loc = st.text_input("Location", "Kuala Lumpur")
                    
                    limit = st.slider("Max Profiles", 10, 100, 20, key="ln_limit")
                    
                    if st.button("Start X-Ray Search", key="btn_xray"):
                        uic.log_message(f"Searching for {role} in {loc}...")
                        with st.spinner("Scanning Google Index..."):
                            from modules.scraper_linkedin_xray import LinkedInXRay
                            hunter = LinkedInXRay()
                            count = hunter.hunt_targets(role, loc, limit, user_id=user_id)
                            hunter.close()
                            
                            if count:
                                st.success(f"Found {count} Candidates")
                                uic.log_message(f"X-Ray successful. {count} leads added.")
                            else:
                                st.warning("No targets found. Try broader terms.")
                                
                with c2:
                    st.info("Status: Ready (Safe Mode)")

            with tab_db:
                st.subheader(" LINKEDIN DATABASE")
                import modules.db_supabase as db
                query = '''
                SELECT id, name, notes as Bio, website as Profile, status as Status, created_at as Added
                FROM leads
                WHERE source LIKE 'LinkedIn%%' AND user_id = %s
                ORDER BY id DESC
                '''
                try:
                    conn = db.get_connection()
                    c = conn.cursor(cursor_factory=db.RealDictCursor)
                    c.execute(query, (user_id,))
                    data = c.fetchall()
                    conn.close()
                    
                    df_li = pd.DataFrame(data)
                    if not df_li.empty:
                        st.dataframe(
                            df_li, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "Profile": st.column_config.LinkColumn("LinkedIn", display_text="LINK")
                            }
                        )
                        csv = df_li.to_csv(index=False).encode('utf-8')
                        st.download_button(" DOWNLOAD LINKEDIN DATA", data=csv, file_name="linkedin_leads.csv", mime="text/csv", type="primary", key="dl_li")
                    else:
                        st.info("No LinkedIn Data Found.")
                except Exception as e:
                    st.error(f"Error loading LinkedIn data: {e}")

    st.markdown("---")
    
    with st.expander(" Mission Logs (Campaign History)", expanded=True):
        import modules.db_supabase as db
        campaigns_df = db.get_recent_campaigns(limit=10)
        if not campaigns_df.empty:
            # Clean up display
            display_df = campaigns_df.rename(columns={
                "timestamp": "Date", 
                "source": "Platform", 
                "search_term": "Target",
                "leads_found": "Leads"
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No missions on record. Initialize a scraper sequence to generate logs.")
            
    st.markdown("###  Live Network Status")
    
    # Map
    # leads = LeadManager.get_leads_with_coords() # This line was commented out in the original, keeping it commented.

# --- MODULE 2: PIPELINE ---
elif "Pipeline" in page:
    st.title("Pipeline & Database")
    st.caption("Manage and enrich your leads.")
    st.markdown("---")
    
    # Load V2 Data
    try:
        df = db.get_all_leads(user_id=user_id)
        if not df.empty:
            df = df.fillna('')
    except Exception as e:
        df = pd.DataFrame()
        st.error(f"Error loading leads: {e}")
    
    # --- METRICS LAYER ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card(title="TOTAL LEADS", content=f"{len(df)}", description="Global Database", key="m_total")
    with m2:
        val = len(df[df['status'] == 'New']) if not df.empty and 'status' in df.columns else 0
        ui.metric_card(title="FRESH LEADS", content=f"{val}", description="Needs Contact", key="m_new")
    with m3:
        # Simple heuristics for high value
        val = len(df[df['source'].str.contains('LinkedIn', na=False, case=False)]) if not df.empty and 'source' in df.columns else 0
        ui.metric_card(title="LINKEDIN ASSETS", content=f"{val}", description="High Net Worth", key="m_linkedin")
    with m4:
         val = len(df[df['source'].str.contains('Instagram', na=False, case=False)]) if not df.empty and 'source' in df.columns else 0
         ui.metric_card(title="VISUAL ASSETS", content=f"{val}", description="Instagram/Design", key="m_insta")

    st.write("")
    
    # --- CONTROL & FILTER LAYER ---
    with st.expander("Filter & Search", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            search = st.text_input("Search Database", placeholder="Name, Bio, or Notes...")
        with c2:
            source_filter = st.multiselect("Source", df['source'].unique() if not df.empty else [])
            
    # Apply Filters
    dff = df.copy()
    if not dff.empty:
        dff = dff.fillna('')  # Prevent NaN crashes in both str.contains and data_editor
        
    if search and not dff.empty:
        dff = dff[dff.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    if source_filter and 'source' in dff.columns and not dff.empty:
        dff = dff[dff['source'].isin(source_filter)]
            
    # --- DATA GRID (FRAGMENT) ---
    st.markdown("#### `DATA_MATRIX`")
    
    @st.fragment
    def render_pipeline_editor(data):
        c1, c2 = st.columns([3, 1])
        with c1:
            # Advanced Data Editor
            try:
                edited_df = st.data_editor(
                    data, 
                    num_rows="dynamic", 
                    use_container_width=True, 
                    height=600,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", width="small"),
                        "name": st.column_config.TextColumn("Name", width="medium"),
                        "email": st.column_config.TextColumn("Email"),
                        "phone": st.column_config.TextColumn("Phone"),
                        "company": st.column_config.TextColumn("Company"),
                        "website": st.column_config.LinkColumn("Website", display_text="LINK"),
                        "status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["New", "Contacted", "Qualified", "Closed", "Archived"],
                            required=True
                        ),
                        "source": st.column_config.TextColumn("Source"),
                        "notes": st.column_config.TextColumn("Notes", width="medium"),
                        "bio": st.column_config.TextColumn("Bio"),
                        "ice_breaker": st.column_config.TextColumn("Ice Breaker", width="medium"),
                        "pain_points": st.column_config.TextColumn("Pain Points", width="medium"),
                        "score": st.column_config.NumberColumn("Score"),
                        "created_at": st.column_config.DatetimeColumn("Added", format="D MMM YYYY"),
                    },
                    hide_index=True,
                    key="pipeline_editor_frag"
                )
            except Exception as e:
                st.error(f"Table Rendering Error: {e}")
                st.dataframe(data, use_container_width=True)
                edited_df = data

        with c2:
            st.markdown("#### OPERATIONS")
            st.caption("Pending Changes: Auto-detected")

            if st.button(" COMMIT TO MEMORY", type="primary", use_container_width=True):
                try:
                    import modules.db_supabase as db
                    # Save only the edits
                    LeadManager.save_data(edited_df) 
                    st.toast("Neural Database Updated!", icon="")
                    st.cache_data.clear() # Clear cache on save
                    st.rerun()
                except Exception as e:
                    st.error(f"Write Error: {e}")

            st.write("")
            st.markdown("#### ENRICHMENT")

            # --- CLAY MODE: DEEP RESEARCH ---
            st.caption("AI visits each lead's website, analyzes their business, and writes personalized ice-breakers. Results go into the Bio, Ice Breaker & Pain Points columns.")
            clay_limit = st.slider("Leads to Research", 1, 50, 5, key="clay_limit", help="How many un-researched leads to process")
            
            if st.button("DEEP RESEARCH (CLAY-MODE)", help="Visits websites, analyzes business, writes ice-breakers."):
                 with st.spinner(f"Agent is researching {clay_limit} leads... (Can take 10s per lead)"):
                     from modules.research_agent import ResearchAgent
                     researcher = ResearchAgent()
                     
                     # Get leads that haven't been researched yet
                     pending_leads = researcher.get_pending_leads(limit=clay_limit, user_id=user_id)
                     
                     if not pending_leads:
                         st.info("No unresearched leads found. All leads have ice-breakers already.")
                     else:
                         count = 0
                         progress_bar = st.progress(0)
                         for i, lead in enumerate(pending_leads):
                             st.toast(f"Researching: {lead['name']}...")
                             success = researcher.research_lead(lead['id'])
                             if success: count += 1
                             progress_bar.progress((i + 1) / len(pending_leads))
                             
                         st.success(f"Deep Research Complete: {count}/{len(pending_leads)} Profiles Updated.")
                         st.balloons()
                         time.sleep(2)
                         st.rerun()



    if dff.empty:
        st.warning("Your database is currently empty or no leads match your search filters.")
        st.info("Head to the 'Lead Search' tab to acquire new leads or clear the search filters above.")
    else:
        render_pipeline_editor(dff)


# --- MODULE 3: CONTENT STUDIO (v2 Full Stack) ---
# --- MODULE 3: CONTENT STUDIO ---
elif "Content Studio" in page:
    from modules.ui_studio_new import render_studio
    render_studio()
    
# --- MODULE X: PRODUCTION STUDIO ---
elif "Production Studio" in page:
    from modules.production_studio import render_production_studio
    render_production_studio()# --- MODULE 4: AI DIALER ---
# --- MODULE 4: AI DIALER ---
elif "AI Dialer" in page:
    from modules.call_center_ui import render_call_center_ui
    render_call_center_ui()

# --- MODULE 5: SETTINGS ---
elif "Settings" in page:
    from modules import config_ui
    config_ui.render_config_ui()

# --- MODULE 5: THE SNIPER (Placeholder - Removed) ---




# --- MODULE S: SETTINGS ---
# --- LEGACY SETTINGS CLEANED ---
            

# --- LEGACY CLEANUP COMPLETE ---


# --- MODULE: ADMIN ---
# --- MODULE 6: ADMIN ---
elif "Admin" in page:
    st.title("Admin Console")
    st.caption("System Administration & Deep Analysis")
    st.markdown("---")
    
    # Session State for Sovereign
    if 'sovereign_active' not in st.session_state:
        st.session_state.sovereign_active = False
    if 'sovereign_logs' not in st.session_state:
        st.session_state.sovereign_logs = []
    if 'analysis_results' not in st.session_state:
         st.session_state.analysis_results = None

    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.success("Strategic Analysis Engine: Ready.")
        
        # --- TABBED INTERFACE ---
        mode_tab = ui.tabs(options=["1. INGEST & ANALYZE", "2. PITCH DECK REVIEW", "3. ️ MISSION DATABASE"], default_value="3. ️ MISSION DATABASE", key="sov_tabs")
        
        if mode_tab == "1. INGEST & ANALYZE":
            st.markdown("####  STEP 1: IMPORT LEADS")
            st.caption("Upload an Excel/CSV with columns: `Company`, `Website`, `Name` (Optional).")
            
            uploaded_file = st.file_uploader("Drop your lead list here", type=['csv', 'xlsx'])
            
            if uploaded_file:
                if st.button(" LAUNCH DEEP RESEARCH", type="primary"):
                    with st.spinner(" Agent is visiting websites & analyzing business models..."):
                        from modules.sovereign_mode import SovereignAgent
                        agent = SovereignAgent()
                        count = agent.ingest_leads(uploaded_file)
                        st.session_state.analysis_results = "Ready" # Signal to refresh or show data
                        st.success(f"Analysis Complete! Processed {count} leads.")
                        st.info(" Switch to 'PITCH DECK REVIEW' tab to see the results.")
        
        elif mode_tab == "2. PITCH DECK REVIEW":
            st.markdown("####  STEP 2: REVIEW & FIRE")
            
            # Fetch leads with drafts
            import modules.db_supabase as db
            conn = db.get_connection()
            # Assuming we add a 'pitch_draft' column. For now we use 'notes' as placeholder if needed, 
            # but ideally we modify DB. Let's assume we use 'notes' or a new json field.
            c = conn.cursor(cursor_factory=db.RealDictCursor)
            c.execute("SELECT id, name, notes FROM leads WHERE (notes LIKE '%%PITCH:%%' OR notes LIKE 'ANALYZING%%' OR notes LIKE 'ERROR%%') AND user_id = %s", (user_id,))
            data = c.fetchall()
            conn.close()
            df = pd.DataFrame(data)
            
            if not df.empty:
                for idx, row in df.iterrows():
                    status_icon = ""
                    if "ANALYZING" in row['notes']: status_icon = ""
                    elif "ERROR" in row['notes']: status_icon = ""
                    else: status_icon = ""
                    
                    with st.expander(f"{status_icon} {row['name']}"):
                        col_pitch, col_ctrl = st.columns([3, 1])
                        with col_pitch:
                            pitch_content = row['notes'].replace("PITCH:", "")
                            st.text_area("Live Pitch Draft", pitch_content, height=150, key=f"pitch_{row['id']}")
                        with col_ctrl:
                            st.markdown("**Actions**")
                            
                            # Email Action
                            if st.button(" SEND", key=f"snd_email_{row['id']}"):
                                with st.spinner("Dispatching via SMTP..."):
                                    # Try to find email
                                    c_email = None
                                    try:
                                        # Simple query for email
                                        q_conn = db.get_connection()
                                        c_res = q_conn.execute("SELECT email FROM leads WHERE id = %s", (row['id'],)).fetchone()
                                        if c_res: c_email = c_res['email']
                                        q_conn.close()
                                    except: pass
                                    
                                    if c_email and "@" in c_email:
                                        blaster = EmailBlaster()
                                        success, msg = blaster.send_single_email(c_email, f"Opportunity for {row['name']}", pitch_content)
                                        blaster.close()
                                        if success:
                                            st.success(f"Sent to {c_email}")
                                            st.balloons()
                                        else:
                                            st.error(f"Failed: {msg}")
                                    else:
                                        st.error("No valid email found for this lead.")

                            # WhatsApp Action
                            import urllib.parse
                            # Try to get phone
                            c_phone = ""
                            try:
                                q_conn = db.get_connection()
                                p_res = q_conn.execute("SELECT phone FROM leads WHERE id = %s", (row['id'],)).fetchone()
                                if p_res and p_res['phone']: 
                                    c_phone = str(p_res['phone']).replace("+", "").replace(" ", "").replace("-", "")
                                q_conn.close()
                            except: pass
                            
                            safe_msg = urllib.parse.quote(pitch_content)
                            if c_phone:
                                wa_url = f"https://wa.me/{c_phone}?text={safe_msg}"
                            else:
                                wa_url = f"https://wa.me/?text={safe_msg}"
                                
                            st.link_button(" WhatsApp", wa_url)
            else:
                st.info("No drafts found. Go to 'INGEST' tab to analyze new leads.")

        elif mode_tab == "3. ️ MISSION DATABASE":
            st.markdown("#### ️ MISSION CONTROL CENTER")
            st.caption("Double-click any cell to edit. Changes save automatically.")
            
            import modules.db_supabase as db
            from modules.crm import LeadManager
            conn = db.get_connection()
            c = conn.cursor(cursor_factory=db.RealDictCursor)
            
            # Load Data Explicitly
            query = "SELECT id, name, email, phone as primary_phone, '' as website, notes, status FROM leads WHERE user_id = %s ORDER BY id DESC"
            c.execute(query, (user_id,))
            data = c.fetchall()
            conn.close()
            
            df = pd.DataFrame(data)
            
            # Configuration for the Data Editor
            edited_df = st.data_editor(
                df,
                key="mission_editor",
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                    "name": st.column_config.TextColumn("Lead Name", required=True),
                    "website": st.column_config.LinkColumn("Website"),
                    "primary_email": st.column_config.TextColumn("Email"),
                    "master_status": st.column_config.SelectboxColumn("Status", options=["New", "Contacted", "Qualified", "Closed", "Lost"]),
                    "notes": st.column_config.TextColumn("AI Notes / Pitch"),
                },
                hide_index=True
            )
            
            # Save Logic (Diff Check)
            if st.button(" SAVE CHANGES & DELETE SELECTED ROWS", type="primary"):
               # We compare edited_df with standard df logic or just iterate updates
               # Streamlit data_editor handles bulk, but we need to identify changes if we want partial updates
               # Simpler approach: iterate edited_df and update all (inefficient but safe for <1000 rows)
               
               # Actually, st.data_editor returns the state. We can track deletions if we use the callback but simplified:
               # We just update everything.
               with st.spinner("Syncing Database..."):
                   count = 0
                   for index, row in edited_df.iterrows():
                       # Update each field
                       LeadManager.update_lead_field(row['id'], 'name', row['name'])
                       LeadManager.update_lead_field(row['id'], 'primary_email', row['primary_email'])
                       LeadManager.update_lead_field(row['id'], 'primary_phone', row['primary_phone'])
                       LeadManager.update_lead_field(row['id'], 'website', row['website'])
                       LeadManager.update_lead_field(row['id'], 'master_status', row['master_status'])
                       LeadManager.update_lead_field(row['id'], 'notes', row['notes'])
                       count += 1
                   
                   # Handle Deletions? 
                   # DataEditor doesn't return deleted rows easily in this mode without session state tracking.
                   # Alternative: We add a 'Delete' checkbox column yourself next time.
                   # For now, we assume user uses the editor to edit.
                   
                   st.success(f"Database Synced: {count} records updated.")
            
            st.markdown("---")
            # Advanced Delete
            with st.expander("️ DELETE ZONE (Bulk Actions)"):
                del_ids = st.text_input("Enter IDs to delete (comma separated)", help="Example: 5, 8, 12")
                if st.button("PERMANENTLY DELETE LEADS"):
                    if del_ids:
                        ids = [x.strip() for x in del_ids.split(',')]
                        deleted = 0
                        for i in ids:
                            if LeadManager.delete_lead(i, user_id=user_id):
                                deleted += 1
                        st.success(f"Annihilated {deleted} records.")
                        st.rerun()
                                
    with c2:
        st.markdown("#### `LIVE TELEMETRY`")
        uic.animation_radar()
        
        st.metric("CPU LOAD", "12%", "+2%")
        st.metric("NETWORK", "SECURE", "VPN ACTIVE")
        st.metric("OPERATIONAL COST", "$0.00", "Free Protocol Active")
        
        # Log Container
        st.markdown("#### `NEURAL LOGS`")
        log_container = st.container(height=300, border=True)
        with log_container:
            if 'sovereign_logs' in st.session_state:
                for log in st.session_state.sovereign_logs:
                    st.text(log)
    
    if mode_tab == "Settings":
        from modules import settings_page
        settings_page.render_settings_page()

    if mode_tab == "️ Admin":
        from modules import admin_page
        admin_page.render_admin_page()


