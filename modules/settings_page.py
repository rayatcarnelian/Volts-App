import streamlit as st
import os
import dotenv

def save_key(key, value):
    """Updates .env file with new key."""
    dotenv_file = dotenv.find_dotenv()
    dotenv.set_key(dotenv_file, key, value)
    st.session_state[key] = value # Update session state too
    os.environ[key] = value

def render_settings_page():
    st.title("⚙️ System Settings")
    st.caption("Configure your AI, Voice, and Payment integrations.")

    with st.container(border=True):
        st.subheader("🧠 AI Engines")
        
        c1, c2 = st.columns(2)
        with c1:
            gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
            if st.button("Save Gemini Key"):
                save_key("GEMINI_API_KEY", gemini_key)
                st.success("Saved!")
                
        with c2:
            replicate_key = st.text_input("Replicate API Token", value=os.getenv("REPLICATE_API_TOKEN", ""), type="password")
            if st.button("Save Replicate Token"):
                save_key("REPLICATE_API_TOKEN", replicate_key)
                st.success("Saved!")

    with st.container(border=True):
        st.subheader("📞 Voice & Telecom (Vapi/Twilio)")
        vapi_key = st.text_input("Vapi Private Key", value=os.getenv("VAPI_API_KEY", ""), type="password")
        vapi_id = st.text_input("Vapi Phone ID", value=os.getenv("VAPI_PHONE_ID", ""))
        
        if st.button("Save Voice Settings"):
            save_key("VAPI_API_KEY", vapi_key)
            save_key("VAPI_PHONE_ID", vapi_id)
            st.success("Voice settings updated.")

    with st.container(border=True):
        st.subheader("💳 Payments (Stripe)")
        stripe_key = st.text_input("Stripe Secret Key", value=os.getenv("STRIPE_SECRET_KEY", ""), type="password")
        price_id = st.text_input("Stripe Price ID", value=os.getenv("STRIPE_PRICE_ID", ""))
        
        if st.button("Save Payment Config"):
            save_key("STRIPE_SECRET_KEY", stripe_key)
            save_key("STRIPE_PRICE_ID", price_id)
            st.success("Payment config updated.")

    with st.container(border=True):
        st.subheader("📧 Email System")
        gmail_user = st.text_input("Gmail Address", value=os.getenv("GMAIL_USER", ""))
        gmail_pass = st.text_input("Gmail App Password", value=os.getenv("GMAIL_APP_PASS", ""), type="password")
        
        if st.button("Save Email Config"):
            save_key("GMAIL_USER", gmail_user)
            save_key("GMAIL_APP_PASS", gmail_pass)
            st.success("Email config saved.")
            
    st.info("Note: Some changes may require a full app restart to take effect.")
