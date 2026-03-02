import streamlit as st
import time
import modules.auth as auth

def handle_payment_success():
    """Checks for success query param and upgrades user."""
    query_params = st.query_params
    if query_params.get("checkout") == "success":
        if "user" in st.session_state:
            user = st.session_state["user"]
            auth.upgrade_user(user["id"], "PRO")
            
            # Refresh ALL credits in session state
            st.session_state["user"]["tier"] = "PRO"
            st.session_state["user"]["credits_image"] = 500
            st.session_state["user"]["credits_video"] = 20
            st.session_state["user"]["call_minutes_used"] = 0.0
            st.session_state["user"]["call_minutes_limit"] = 100.0
            
            st.balloons()
            st.success("✅ Payment Successful! You are now a PRO member.")
            
            # Clear param
            st.query_params.clear()
            time.sleep(2)
            st.rerun()
