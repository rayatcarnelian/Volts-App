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
            current_gemini = get_user_setting(user_id, "GEMINI_API_KEY")
            gemini_key = st.text_input("Gemini API Key", value=current_gemini, type="password")
            if st.button("Save Gemini Key"):
                save_key("GEMINI_API_KEY", gemini_key)
                
        with c2:
            current_fal = get_user_setting(user_id, "FAL_KEY")
            fal_key = st.text_input("Fal.ai API Key", value=current_fal, type="password")
            if st.button("Save Fal Key"):
                save_key("FAL_KEY", fal_key)
                
    st.info("Your custom API keys are encrypted and stored directly linked to your account.")
