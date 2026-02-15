import streamlit as st
import os
from dotenv import load_dotenv, set_key

# Load vars
load_dotenv()

def save_to_env(key, value):
    """Saves a single key-value pair to the local .env file."""
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f: f.write("")
    
    # Use dotenv's set_key to handle quoting and escaping correctly
    # If value is empty, we still save it as empty string
    set_key(env_file, key, value)

def render_config_ui():
    st.title("⚙️ System Configuration")
    st.markdown("Link your external accounts and APIs here. These keys are stored locally in `.env`.")

    # --- TABS FOR ORGANIZATION ---
    tab_voice, tab_social, tab_ai, tab_system = st.tabs([
        "📞 Voice & Telephony", 
        "📱 Social Media", 
        "🧠 AI Engines", 
        "📧 Outreach & System"
    ])

    with tab_voice:
        st.subheader("Vapi & Telephony")
        st.info("Required for the AI Call Center.")
        
        with st.form("voice_config"):
            c1, c2 = st.columns(2)
            with c1:
                vapi_key = st.text_input("Vapi Private API Key", value=os.getenv("VAPI_API_KEY", ""), type="password", help="From Vapi Dashboard > Keys")
                vapi_ph = st.text_input("Vapi Phone ID", value=os.getenv("VAPI_PHONE_ID", ""), help="The Assistant/Phone ID from Vapi")
            with c2:
                twilio_sid = st.text_input("Twilio Account SID", value=os.getenv("TWILIO_SID", ""))
                twilio_token = st.text_input("Twilio Auth Token", value=os.getenv("TWILIO_AUTH_TOKEN", ""), type="password")
            
            if st.form_submit_button("💾 Save Voice Settings"):
                save_to_env("VAPI_API_KEY", vapi_key)
                save_to_env("VAPI_PHONE_ID", vapi_ph)
                save_to_env("TWILIO_SID", twilio_sid)
                save_to_env("TWILIO_AUTH_TOKEN", twilio_token)
                st.success("Voice settings saved! Please restart the app for changes to take full effect.")

    with tab_social:
        st.subheader("Scraper Credentials")
        st.warning("Use dedicated accounts for scraping to avoid bans on your personal profiles.")
        
        with st.form("social_config"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Facebook / Instagram")
                fb_email = st.text_input("Facebook Email", value=os.getenv("FB_EMAIL", ""))
                fb_pass = st.text_input("Facebook Password", value=os.getenv("FB_PASS", ""), type="password")
                insta_user = st.text_input("Instagram Username", value=os.getenv("INSTA_USER", ""))
                insta_pass = st.text_input("Instagram Password", value=os.getenv("INSTA_PASS", ""), type="password")
            
            with c2:
                st.markdown("#### Other Platforms")
                tg_api = st.text_input("Telegram API ID", value=os.getenv("TG_API_ID", ""))
                tg_hash = st.text_input("Telegram API Hash", value=os.getenv("TG_API_HASH", ""), type="password")
                x_user = st.text_input("X (Twitter) User", value=os.getenv("X_USER", ""))
                x_pass = st.text_input("X (Twitter) Password", value=os.getenv("X_PASS", ""), type="password")

            if st.form_submit_button("💾 Save Social Config"):
                save_to_env("FB_EMAIL", fb_email)
                save_to_env("FB_PASS", fb_pass)
                save_to_env("INSTA_USER", insta_user)
                save_to_env("INSTA_PASS", insta_pass)
                save_to_env("TG_API_ID", tg_api)
                save_to_env("TG_API_HASH", tg_hash)
                save_to_env("X_USER", x_user)
                save_to_env("X_PASS", x_pass)
                st.success("Social credentials saved.")

    with tab_ai:
        st.subheader("AI Model Access")
        st.markdown("Required for content generation, image analysis, and voice synthesis.")
        
        with st.form("ai_config"):
            gemini = st.text_input("Google Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password", help="For Text & Logic")
            eleven = st.text_input("ElevenLabs API Key", value=os.getenv("ELEVENLABS_API_KEY", ""), type="password", help="For Voice Cloning")
            replicate = st.text_input("Replicate API Token", value=os.getenv("REPLICATE_API_TOKEN", ""), type="password", help="For Image Generation")
            hf = st.text_input("HuggingFace Token", value=os.getenv("HF_TOKEN", ""), type="password", help="For Open Source Models")
            
            if st.form_submit_button("💾 Save AI Keys"):
                save_to_env("GEMINI_API_KEY", gemini)
                save_to_env("ELEVENLABS_API_KEY", eleven)
                save_to_env("REPLICATE_API_TOKEN", replicate)
                save_to_env("HF_TOKEN", hf)
                st.success("AI Keys saved.")

    with tab_system:
        st.subheader("Email Outbound")
        st.info("Use an App Password, not your login password!")
        
        with st.form("sys_config"):
            c1, c2 = st.columns(2)
            with c1:
                gmail_user = st.text_input("Gmail Address", value=os.getenv("GMAIL_USER", ""))
                gmail_pass = st.text_input("Gmail App Password", value=os.getenv("GMAIL_APP_PASS", ""), type="password")
            with c2:
                notify = st.text_input("Notification Recipient Email", value=os.getenv("NOTIFY_EMAIL", ""), help="Where system alerts go")
            
            if st.form_submit_button("💾 Save System Config"):
                save_to_env("GMAIL_USER", gmail_user)
                save_to_env("GMAIL_APP_PASS", gmail_pass)
                save_to_env("NOTIFY_EMAIL", notify)
                st.success("System config saved.")
