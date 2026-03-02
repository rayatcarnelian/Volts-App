import streamlit as st

def render_legal_modal():
    """Renders Terms and Privacy in an expander or dialog."""
    st.caption("Combined Terms & Privacy Policy")
    
    with st.expander("📜 User Agreement (Simple Version)"):
        st.markdown("""
        ### ✅ You Own Your Data
        Any leads or content you scrape/generate are 100% yours. We don't claim ownership.

        ### 🛡️ Privacy First
        - We store your data locally on your machine (or private cloud).
        - We don't sell your data to third parties.
        - Your API keys are stored securely and used only for your requests.

        ### ⚡ Fair Use
        Volts is a powerful tool. Please use it responsibly and respect the Terms of Service of the platforms you interact with (e.g., LinkedIn, Google). 
        You are responsible for your outreach campaigns.
        """)
