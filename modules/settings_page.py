import streamlit as st
import os

from modules.db_supabase import get_user_setting, save_user_setting

def save_key(key, value):
    """Saves key securely to user's DB profile and active session."""
    user = st.session_state.get('user')
    user_id = user.get('id') if user else None
    if not user_id:
        st.error("You must be logged in to save settings.")
        return
        
    if save_user_setting(user_id, key, value):
        st.session_state[f"USER_{key}"] = value # Update session state dynamically
        st.success("Saved!")
    else:
        st.error("Failed to save setting.")

def render_settings_page():
    st.title("System Settings")
    st.caption("Configure your personal AI, Voice, and Integration keys.")
    
    user = st.session_state.get('user')
    user_id = user.get('id') if user else None
    if not user_id:
        st.warning("Please log in to manage your settings.")
        return

    with st.container(border=True):
        st.subheader("🤖 AI Engines")
        st.caption("Your custom keys will be used instead of the global keys.")
        
        c1, c2 = st.columns(2)
        with c1:
            current_fal = get_user_setting(user_id, "FAL_KEY")
            fal_key = st.text_input("Fal.ai API Key", value=current_fal, type="password")
            if st.button("Save Fal Key"):
                save_key("FAL_KEY", fal_key)
                
                
    with st.container(border=True):
        st.subheader("📞 Voice Apps (Vapi/Twilio)")
        current_vapi_key = get_user_setting(user_id, "VAPI_API_KEY")
        current_vapi_id = get_user_setting(user_id, "VAPI_PHONE_ID")
        current_twilio_sid = get_user_setting(user_id, "TWILIO_ACCOUNT_SID")
        current_twilio_token = get_user_setting(user_id, "TWILIO_AUTH_TOKEN")
        current_twilio_phone = get_user_setting(user_id, "TWILIO_PHONE_NUMBER")
        
        vapi_key = st.text_input("Vapi Private Key", value=current_vapi_key, type="password")
        vapi_id = st.text_input("Vapi Phone ID", value=current_vapi_id)
        
        st.markdown("---")
        twilio_sid = st.text_input("Twilio Account SID", value=current_twilio_sid)
        twilio_token = st.text_input("Twilio Auth Token", value=current_twilio_token, type="password")
        twilio_phone = st.text_input("Twilio Phone Number", value=current_twilio_phone, placeholder="+1234567890")
        
        if st.button("Save Voice Settings"):
            save_key("VAPI_API_KEY", vapi_key)
            save_key("VAPI_PHONE_ID", vapi_id)
            save_key("TWILIO_ACCOUNT_SID", twilio_sid)
            save_key("TWILIO_AUTH_TOKEN", twilio_token)
            save_key("TWILIO_PHONE_NUMBER", twilio_phone)

    with st.container(border=True):
        st.subheader("📧 Email System")
        current_gmail_user = get_user_setting(user_id, "GMAIL_USER")
        current_gmail_pass = get_user_setting(user_id, "GMAIL_APP_PASS")
        
        gmail_user = st.text_input("Gmail Address", value=current_gmail_user)
        gmail_pass = st.text_input("Gmail App Password", value=current_gmail_pass, type="password")
        
        if st.button("Save Email Config"):
            save_key("GMAIL_USER", gmail_user)
            save_key("GMAIL_APP_PASS", gmail_pass)
            
    st.info("Your custom API keys are encrypted and stored directly linked to your account.")
