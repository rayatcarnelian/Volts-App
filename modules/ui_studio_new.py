"""
VOLTS STUDIO: THE SAAS APPLICATION (PRODUCTION)
Real Authentication, Pro Quality, and Gallery.
"""

import streamlit as st
import time
import os
import glob
import modules.studio_style as style
import modules.auth as auth
from modules.studio_subscription import SubscriptionManager
from modules.premium_studio import PremiumStudio
from modules.payment_handler import handle_payment_success # NEW

# Initialize Engines
studio = PremiumStudio()
subs = SubscriptionManager()

def render_studio():
    """Renders the Full SaaS Experience with Real Auth."""
    
    # 0. Handle Payment Return
    handle_payment_success()
    
    # 1. Inject Styles
    style.inject_high_end_css()
    
    # 2. Check Auth State
    if "user" not in st.session_state:
        st.session_state["user"] = None
        
    user = st.session_state["user"]
    
    # --- ROUTER ---
    if not user:
        render_auth_page()
    elif user["tier"] == "PRICING_VIEW": # Temporary state for upgrade flow
        render_pricing_page()
    else:
        # App View (Free/Pro/Admin)
        render_app_interface(user)

def render_auth_page():
    """Login / Signup Screen."""
    style.render_landing_hero()
    
    # Use a container for the auth box to center it perfectly
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""
        <div style="background: rgba(20, 20, 20, 0.8); padding: 20px; border-radius: 15px; border: 1px solid #333;">
        """, unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab_login:
            st.markdown("### Welcome Back")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Authenticating..."):
                         user_data = auth.login(email, password)
                         if user_data:
                             st.session_state["user"] = user_data
                             st.success("Login successful!")
                             time.sleep(0.5)
                             st.rerun()
                         else:
                             st.error("Invalid email or password.")
                    
        with tab_signup:
            st.markdown("### Creates Account")
            new_email = st.text_input("Email", key="signup_email")
            new_pass = st.text_input("Password", type="password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="signup_pass_confirm")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                 if not new_email or not new_pass:
                     st.error("Please fill in all fields.")
                 elif new_pass != confirm_pass:
                     st.error("Passwords do not match.")
                 else:
                     with st.spinner("Creating account..."):
                         success, msg = auth.signup(new_email, new_pass)
                         if success:
                             st.success("Account created! Logging in...")
                             time.sleep(1)
                             user_data = auth.login(new_email, new_pass)
                             st.session_state["user"] = user_data
                             st.rerun()
                         else:
                             st.error(f"Error: {msg}")

        st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #666;">
            Used by 10,000+ Creators • Powered by Flux 1.1 • No Credit Card
        </div>
    """, unsafe_allow_html=True)

def render_pricing_page():
    """The Real Gatekeeper."""
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Upgrade your Creativity</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c2:
        st.markdown("""
            <div style="
                background: linear-gradient(180deg, #1A1708 0%, #000 100%);
                border: 1px solid #3D3520;
                border-radius: 20px;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 0 40px rgba(197, 165, 90, 0.2);
            ">
                <h3 style="color: #C5A55A; margin-bottom: 0.5rem;">PRO CREATOR</h3>
                <div style="font-size: 3.5rem; font-weight: 800; color: white; margin-bottom: 1rem;">
                    $29<span style="font-size: 1rem; color: #666;">/mo</span>
                </div>
                <ul style="text-align: left; list-style: none; padding: 0; color: #ddd; margin-bottom: 2rem;">
                    <li style="margin-bottom: 10px;">✅ <b>500 Premium Images</b></li>
                    <li style="margin-bottom: 10px;">✅ <b>Commercial License</b></li>
                    <li style="margin-bottom: 10px;">✅ <b>Priority Generation</b></li>
                    <li style="margin-bottom: 10px;">✅ <b>No Watermarks</b></li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Upgrade to PRO", type="primary", use_container_width=True):
            # 1. Initialize Payment Gateway
            from modules.payments import gateway
            
            if gateway.is_configured():
                # --- REAL STRIPE FLOW ---
                with st.spinner("Creating secure checkout session..."):
                    user = st.session_state["user"]
                    base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
                    session_url, error = gateway.create_checkout_session(
                        user_email=user["email"],
                        success_url=f"{base_url}/?checkout=success",
                        cancel_url=f"{base_url}/?checkout=cancel"
                    )
                    
                    if session_url:
                        st.link_button("👉 Click here to pay securely", session_url, type="primary", use_container_width=True)
                        st.info("You will be redirected to Stripe's secure payment page.")
                        st.stop() # Stop execution to showing the link
                    else:
                        st.error(f"Payment Error: {error}")
            else:
                # --- SIMULATOR FLOW (FALLBACK) ---
                with st.spinner("Processing Simulator Payment..."):
                    time.sleep(2)
                    
                # Upgrade in DB
                user = st.session_state["user"]
                auth.upgrade_user(user["id"], "PRO")
                
                # Refresh Session
                st.session_state["user"]["tier"] = "PRO"
                st.session_state["user"]["credits_image"] = 500
                st.balloons()
                st.rerun()
            
    if st.button("Back to Studio", use_container_width=True):
         st.session_state["user"]["tier"] = "FREE" # Revert view state
         st.rerun()


def render_app_interface(user):
    """The Product: Studio + Gallery."""
    
    # Refresh credits
    db_credits = auth.get_user_credits(user["id"])
    if db_credits:
        current_credits = db_credits["credits_image"]
        tier = db_credits["tier"]
    else:
        current_credits = 0
        tier = "FREE"
    
    limit = 500 if tier in ["PRO", "AGENCY", "ADMIN"] else 5
    
    # --- HEADER & CREDITS ---
    c_h1, c_h2 = st.columns([3, 1])
    with c_h2:
        st.caption(f"{tier} PLAN")
        progress = 0.0
        if limit > 0:
            progress = min(1.0, current_credits / limit)
            
        st.progress(progress)
        st.markdown(f"<div style='text-align:right; color:#71717a;'>{current_credits} Credits Left</div>", unsafe_allow_html=True)
        
        if tier == "FREE":
             if st.button("⭐ Upgrade to Pro"):
                 st.session_state["user"]["tier"] = "PRICING_VIEW" 
                 st.rerun()
                 
        # Display Video Credits for Pro Users
        if tier in ["PRO", "AGENCY", "ADMIN"]:
             vid_limit = 20 if tier == "PRO" else 100
             vid_creds = db_credits.get("credits_video", 0)
             st.caption(f"🎥 Video Credits: {vid_creds}/{vid_limit}")

    st.markdown("---")
    
    # --- TABS: CREATE vs GALLERY ---
    # --- TABS: CREATE vs VIDEO vs GALLERY ---
    tab_create, tab_video, tab_gallery = st.tabs(["✨ Create", "🎥 Video", "🖼️ Gallery"])
    
    with tab_create:
        render_create_tab(user, tier, current_credits)
        
    with tab_video:
        render_video_tab(user, tier, db_credits.get("credits_video", 0))

    with tab_gallery:
        render_gallery_tab()

def render_create_tab(user, tier, current_credits):
    """The Image Generation Interface."""
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align:center; margin-bottom: 1rem; color: #444; font-size: 0.9rem;'>VOLTS ENGINE v2.1 (FLUX)</div>", unsafe_allow_html=True)
        
        prompt = st.text_area("Prompt", placeholder="Imagine anything...", height=100, label_visibility="collapsed")
        
        # PRO MODE TOGGLE
        mode = "schnell" # Default
        if tier in ["PRO", "AGENCY", "ADMIN"]:
             mode = "pro"
             st.success("✨ PRO Mode Active: Using Flux 1.1 Pro (Ultra Quality)")
        else:
             st.info("ℹ️ Free Mode: Using Flux Schnell (Fast). Upgrade for Ultra Quality.")
             
        b1, b2 = st.columns([3, 1])
        with b2:
            generate = st.button("Generate", type="primary", use_container_width=True)
            
    if generate:
        if current_credits <= 0:
            st.error("Out of credits.")
            if tier == "FREE":
                st.session_state["user"]["tier"] = "PRICING_VIEW"
                st.rerun()
        else:
            with st.spinner("Rendering..."):
                 # Call Engine
                 res = studio.generate(prompt=prompt, mode=mode, aspect_ratio="landscape_16_9")
                 if res["success"]:
                     st.session_state["last_image"] = res
                     auth.deduct_credit(user["id"], "image")
                     st.rerun()
                 else:
                     st.error(res.get("error"))
                 
    # Result Feed
    if "last_image" in st.session_state:
        st.divider()
        c_r1, c_r2, c_r3 = st.columns([1, 4, 1])
        with c_r2:
            st.image(st.session_state["last_image"]["images"][0], use_container_width=True)


def render_video_tab(user, tier, current_credits):
    """The Video Generation Interface (Luma Ray / Minimax)."""
    
    # Gatekeeper
    if tier == "FREE":
        st.warning("🔒 Video Studio is locked. Upgrade to PRO to access Luma Ray & Minimax.")
        if st.button("Unlock Video Studio"):
            st.session_state["user"]["tier"] = "PRICING_VIEW"
            st.rerun()
        return

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align:center; margin-bottom: 1rem; color: #444; font-size: 0.9rem;'>HOLLYWOOD ENGINE (Luma Ray / Minimax)</div>", unsafe_allow_html=True)
        
        # Model Selector
        model_choice = st.selectbox("Engine", ["Luma Ray (Cinematic)", "Minimax (High Motion)"], index=0)
        model_map = {"Luma Ray (Cinematic)": "luma", "Minimax (High Motion)": "minimax"}
        
        prompt = st.text_area("Video Prompt", placeholder="A cinematic drone shot of a futuristic city...", height=100)
        
        # Image-to-Video Option
        start_image = None
        use_last_image = st.checkbox("Animate Last Generated Image")
        if use_last_image and "last_image" in st.session_state:
            last = st.session_state["last_image"]
            if "images" in last and last["images"]:
                start_image = last["images"][0]
                st.image(start_image, width=200, caption="Starting Frame")
        elif use_last_image:
            st.warning("No previous image found. Generate an image first!")

        if st.button("Generate Video (Costs 1 Video Credit)", type="primary", use_container_width=True):
            if current_credits <= 0:
                st.error("Out of Video Credits.")
            elif not prompt:
                st.error("Please enter a prompt.")
            else:
                with st.spinner(f"Rendering Video with {model_choice}... This may take 30-60s"):
                     res = studio.generate_video(
                         prompt=prompt, 
                         start_image_path=start_image, 
                         model=model_map[model_choice]
                     )
                     
                     if res["success"]:
                         st.success("Video Generated Successfully!")
                         st.video(res["video_path"])
                         auth.deduct_credit(user["id"], "video")
                     else:
                         st.error(f"Generation Failed: {res.get('error')}")

    # Show last generated video if exists
    video_folder = "assets/studio/video"
    if os.path.exists(video_folder):
        videos = sorted(glob.glob(os.path.join(video_folder, "*.mp4")), key=os.path.getmtime, reverse=True)
        if videos:
            st.divider()
            st.markdown("### Recent Videos")
            for v in videos[:3]:
                st.video(v)
                name = os.path.basename(v)
                with open(v, "rb") as vf:
                    st.download_button(f"Download {name}", data=vf, file_name=name, mime="video/mp4", key=f"dl_vid_{name}")


def render_gallery_tab():
    """Browse the 'Database' of images."""
    st.markdown("### 🖼️ Your Creations")
    
    # Logic: Read from assets/studio/premium
    # In a real app, we'd query the DB for images owned by user['id'].
    # For now, we show all generated images (Local MVP).
    folder = "assets/studio/premium"
    if not os.path.exists(folder):
        st.info("No images generated yet.")
        return
        
    # Get files sorted by time (newest first)
    files = sorted(
        glob.glob(os.path.join(folder, "*.*")),
        key=os.path.getmtime,
        reverse=True
    )
    
    if not files:
        st.info("Gallery is empty.")
        return
        
    # Responsive Grid (4 columns)
    cols = st.columns(4)
    for idx, f in enumerate(files):
        with cols[idx % 4]:
            st.image(f, use_container_width=True)
            # Filename as label (shortened)
            name = os.path.basename(f)
            st.caption(f"{name[:15]}...")
            
            # Action buttons
            with open(f, "rb") as file:
                btn = st.download_button(
                    label="Download",
                    data=file,
                    file_name=name,
                    mime="image/jpeg",
                    key=f"dl_{idx}"
                )
