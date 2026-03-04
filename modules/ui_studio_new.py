"""
VOLTS CONTENT STUDIO V2: The Social Media Machine
Features: Strategy Playbook, Gemini AI Brain, Flux Image Architect, and Sync Labs Video Engine.
"""

import streamlit as st
import time
import os
import glob
import modules.studio_style as style
import modules.auth as auth
from modules.payment_handler import handle_payment_success
import modules.api_fal as fal
import modules.api_gemini as gemini
import modules.db_supabase as db

def render_studio():
    """Renders the Full Content Studio Experience."""
    handle_payment_success()
    style.inject_high_end_css()
    
    if "user" not in st.session_state:
        st.session_state["user"] = None
        
    user = st.session_state["user"]
    
    # --- ROUTER ---
    if not user:
        render_auth_page()
    else:
        render_app_interface(user)

def render_auth_page():
    """Login / Signup Screen for Studio."""
    style.render_landing_hero()
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""
        <div style="background: rgba(20, 20, 20, 0.8); padding: 20px; border-radius: 15px; border: 1px solid #333;">
        """, unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
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
            st.markdown("### Create Account")
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
            The Ultimate Content Engine • Powered by FLUX & Fal.ai
        </div>
    """, unsafe_allow_html=True)

def render_pricing_page():
    """The Real Gatekeeper to Pro Studio."""
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Upgrade Content Studio</h1>", unsafe_allow_html=True)
    
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
                <h3 style="color: #C5A55A; margin-bottom: 0.5rem;">STUDIO PRO</h3>
                <div style="font-size: 3.5rem; font-weight: 800; color: white; margin-bottom: 1rem;">
                    $29<span style="font-size: 1rem; color: #666;">/mo</span>
                </div>
                <ul style="text-align: left; list-style: none; padding: 0; color: #ddd; margin-bottom: 2rem;">
                    <li style="margin-bottom: 10px;"><b>Unlimited FLUX Images</b></li>
                    <li style="margin-bottom: 10px;"><b>50 Avatar Sync Videos / mo</b></li>
                    <li style="margin-bottom: 10px;"><b>AI Script Writer (Gemini)</b></li>
                    <li style="margin-bottom: 10px;"><b>No Watermarks</b></li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Upgrade to PRO", type="primary", use_container_width=True):
            # Using Simulator Flow for local dev
            with st.spinner("Processing Simulator Payment..."):
                time.sleep(2)
            user = st.session_state["user"]
            auth.upgrade_user(user["id"], "PRO")
            st.session_state["user"]["tier"] = "PRO"
            st.session_state["user"]["credits_image"] = 5000
            st.balloons()
            st.rerun()
            
    if st.button("Back to Studio", use_container_width=True):
         st.session_state["user"]["tier"] = "FREE" 
         st.rerun()

def render_app_interface(user):
    """The 4-Tab Content Studio Interface."""
    
    st.title("Content Studio Pro")
    st.caption("The High-Volume Social Media Pipeline.")
    
    db_credits = auth.get_user_credits(user["id"])
    tier = "PRO" # Overridden to give all users full access without subscriptions
            
    st.markdown("---")
    
    tab_strategy, tab_brain, tab_flux, tab_video, tab_gallery = st.tabs([
        "Strategy Playbook", 
        "AI Brain", 
        "Image Architect (FLUX)", 
        "Video Engine (Avatar)",
        "🖼️ My Gallery"
    ])
    
    with tab_strategy:
        render_strategy_tab()
        
    with tab_brain:
        render_brain_tab(tier)
        
    with tab_flux:
        render_flux_tab(user, tier)
        
    with tab_video:
        render_video_tab(user, tier)
        
    with tab_gallery:
        render_gallery_tab(user)


def render_strategy_tab():
    """The Social Media Playbook."""
    st.markdown("### The High-Volume Dominance Strategy")
    st.markdown("""
    To keep Instagram, Facebook, and TikTok active every single day with high-quality content, follow this optimized workflow. 
    **Recommended Monthly Limits:** ~80 AI Hook Videos (Lipsync) and **~2,000 FLUX Images.**
    
    **1. The "Hook + B-Roll" Reel (Use Mon/Wed/Fri)**
    *   **Goal:** High Trust, High Engagement, Algorithmic Reach.
    *   **Steps:** 
        1. Go to **AI Brain** and generate a script.
        2. Go to **Video Engine** and use the **Avatar Sync** for *only the first 7 to 10 seconds* of the script (The Hook).
        3. Go to **Image Architect** and generate 2-3 cinematic images (B-Roll).
        4. Stitch them together natively or in CapCut: the Avatar Hook grabs attention, then transitions to high-quality images while the voiceover finishes.
        
    **2. The High-Value Carousel (Use Tue/Thu)**
    *   **Goal:** Educational Value, Saves, and Audience Retention.
    *   **Steps:**
        1. Go to **Image Architect** and generate five 4:5 aspect ratio images focused on a specific pain point.
        2. Post as a swipeable carousel on Instagram and Facebook to drive deep engagement.
        
    **3. The Faceless Aesthetic Post (Use Weekends)**
    *   **Goal:** Consistency and Brand Authority.
    *   **Steps:** Generate 1 ultra-realistic luxury image in **Image Architect**. Overlay a quote, tip, or statistic. Post directly to your feed and stories.
    """)
    
    st.info("You need your `FAL_KEY` to generate Images and Videos. Go to Settings and add it!")

def render_brain_tab(tier):
    """Gemini-powered script generator."""
    st.markdown("### The AI Brain (Script Writer)")
    st.caption("Powered by Google Gemini 1.5 Flash")
    
    if not gemini.is_configured():
         st.error("The Master Server is missing its GEMINI_API_KEY. The Brain is offline.")
         return
         
    topic = st.text_input("What is the video about?", placeholder="e.g. 3 reasons why minimalist interior design saves money")
    platform = st.selectbox("Platform", ["Instagram Reels", "TikTok", "Facebook Shorts"])
    
    if st.button("Generate Script", type="primary", disabled=(tier=="FREE")):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Brainstorming..."):
                res = gemini.generate_script(topic, platform)
                if res["success"]:
                    st.success("Script Generated!")
                    st.markdown("### Your Script")
                    st.text_area("Copy this:", res["script"], height=400)
                else:
                    st.error(res.get("error"))

def render_flux_tab(user, tier):
    """FLUX.1 Image generation for B-Roll and Carousels."""
    st.markdown("### Image Architect (FLUX.1)")
    st.caption("Powered by Fal.ai FLUX [schnell]")
    
    user_id = user["id"]
    if not db.get_user_setting(user_id, "FAL_KEY"):
        st.error("FAL_KEY is missing from your User Settings! Go to Settings in the sidebar to add it.")
        
    c1, c2 = st.columns([2, 1])
    with c1:
        prompt = st.text_area("Image Prompt", placeholder="Ultra realistic 8k, luxury modern living room in Kuala Lumpur, morning sunlight...")
    with c2:
        size_options = {
            "Landscape 16:9 (YouTube/Web)": "landscape_16_9",
            "Portrait 4:3 (Instagram Feed)": "portrait_4_3",
            "Portrait 16:9 (Reels/Stories)": "portrait_16_9",
            "Square HD (1:1)": "square_hd"
        }
        display_choice = st.selectbox("Format", list(size_options.keys()))
        aspect_ratio = size_options[display_choice]
    
    if st.button("Generate B-Roll Image (~$0.006)", type="primary", disabled=(tier=="FREE") or not fal.setup_fal_key()):
        if prompt:
            with st.spinner("Rendering via FLUX.1 [schnell]..."):
                res = fal.generate_image(prompt, image_size=aspect_ratio)
                if res["success"]:
                    st.image(res["image_url"], caption="FLUX Generation", use_container_width=True)
                    db.save_studio_asset(user["id"], "image", res["image_url"], f"[{display_choice}] {prompt}")
                    st.success("Render complete & saved to Gallery. Right click to download.")
                else:
                    st.error(res.get("error"))
        else:
            st.warning("Please enter a prompt.")

def render_video_tab(user, tier):
    """Avatar Lip-sync and Video gen."""
    st.markdown("### Video Engine")
    st.caption("Powered by Fal.ai Sync-Lipsync & Kling 1.5")
    
    user_id = user["id"]
    if not db.get_user_setting(user_id, "FAL_KEY"):
        st.error("FAL_KEY is missing from your User Settings! Go to Settings in the sidebar to add it.")
        return
        
    v_tab1, v_tab2 = st.tabs(["Avatar Lip-Sync (The Hook)", "Cinematic B-Roll (Text-to-Video)"])
    
    with v_tab1:
        st.markdown("""
        **How it works (The Digital Mask):**
        Avatar Sync completely eliminates the need to record yourself speaking. You only ever record yourself **once**.
        
        1. **Create the Base Video:** Record a 10-second video of yourself sitting silently, looking at the camera. Upload it to a public link (like Google Drive or Imgur).
        2. **Create the Audio Hook:** Use the AI Brain script and feed it to a voice generator (like ElevenLabs) to create an `.mp3` of the hook. Upload it.
        3. **The Magic:** Paste both URLs below. Fal.ai will physically map your face and animate your lips and jaw to perfectly match the audio file!
        """)
        
        base_video_url = st.text_input("Base User Video URL (.mp4)")
        audio_url = st.text_input("Hook Audio URL (.mp3)")
        
        if st.button("Sync Avatar (~$0.70 for 7s)", type="primary", disabled=(tier=="FREE")):
            if base_video_url and audio_url:
                with st.spinner("Processing lip-sync geometry... (Takes approx 20-40s)"):
                    # NOTE: Assuming placeholder or live payload here
                    res = fal.generate_avatar_sync(base_video_url, audio_url)
                    if res["success"]:
                        st.video(res["video_url"])
                        db.save_studio_asset(user["id"], "video", res["video_url"], f"Avatar Sync | Audio: {audio_url}")
                        st.success("Video synced & saved to Gallery!")
                    else:
                        st.error(res.get("error"))
            else:
                st.warning("Provide both Video and Audio URLs.")
                
    with v_tab2:
        st.markdown("""
        **Kling 1.5 Text-to-Video:**
        Generate a 3 to 5 second dynamic motion clip from text.
        """)
        v_prompt = st.text_input("Video Prompt", placeholder="Drone flying over a luxury pool, sunset...")
        if st.button("Generate Motion B-Roll (~$0.30)", type="primary", disabled=(tier=="FREE")):
            if v_prompt:
                with st.spinner("Rendering video cluster... (Takes approx 40s)"):
                    res = fal.generate_video(v_prompt)
                    if res["success"]:
                        st.video(res["video_url"])
                        db.save_studio_asset(user["id"], "video", res["video_url"], f"Wan 2.5: {v_prompt}")
                        st.success("Motion B-Roll rendered & saved to Gallery!")
                    else:
                        st.error(res.get("error"))
            else:
                st.warning("Enter a prompt.")

def render_gallery_tab(user):
    """Displays all previously generated images and videos for the user."""
    st.markdown("### 🖼️ My Asset Gallery")
    st.caption("Your permanently saved high-volume media.")
    
    assets_df = db.get_user_assets(user["id"])
    if assets_df.empty:
        st.info("Your gallery is empty! Go generate some FLUX images or Avatar videos.")
        return
        
    # Create masonry-like layout
    cols = st.columns(3)
    for index, row in assets_df.iterrows():
        col = cols[index % 3]
        with col:
            st.markdown(f"**{row['asset_type'].upper()}**")
            if row['asset_type'] == 'image':
                st.image(row['asset_url'], use_container_width=True)
            elif row['asset_type'] == 'video':
                st.video(row['asset_url'])
            
            with st.expander("Prompt Details"):
                st.caption(row['prompt'])
                st.caption(f"*Created: {row['created_at']}*")
