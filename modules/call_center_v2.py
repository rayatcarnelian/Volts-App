import streamlit as st
import time
import asyncio
from modules.android_bridge import AndroidBridge
from modules.voice_core import NativeEar, NativeMouth, SalesBrain

# Global State Helper (Session State is tricky with audio loops)
# We might need to define this outside or init in main

def render_call_center_v2():
    st.markdown("## 🛰️ SIM COMMAND CENTER (CYBORG MODE)")
    st.caption("Use your physical phone + AI Voice Cloning. Zero Cost.")
    
    st.markdown("---")
    
    # Init Hardware
    bridge = AndroidBridge()
    
    # Layout
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown("### 🔌 HARDWARE LINK")
        
        # Connection Status
        is_connected = bridge.check_connection()
        if is_connected:
            st.success("ANDROID: ONLINE 🟢")
        else:
            st.error("ANDROID: OFFLINE 🔴")
            st.info("Plugin phone via USB & Enable Debugging.")
            if st.button("RETRY CONNECTION"):
                st.rerun()
                
        st.markdown("---")
        st.markdown("### 🗣️ VOICE PROFILE")
        
        mouth = NativeMouth() # Light init
        voice = st.selectbox("AI Voice Clone", list(mouth.voice_map.keys()))
        
        st.markdown("---")
        st.markdown("### 🧠 KNOWLEDGE BASE")
        kb = st.text_area("Portfolio / Services / Scripts", height=200, value="Hi, I'm calling from Volts. We do AI Interior design. We can render your sketches in seconds. Are you interested in a demo?")
        
    with c2:
        st.markdown("### 📞 DIALER INTERFACE")
        
        tab_dial, tab_auto = st.tabs(["MANUAL DIAL", "AUTO-CAMPAIGN"])
        
        with tab_dial:
            number = st.text_input("Enter Phone Number", placeholder="+60 12 345 6789")
            
            c_a, c_b, c_c = st.columns(3)
            with c_a:
                if st.button("📞 CALL NOW", type="primary", disabled=not is_connected):
                    if bridge.dial_number(number):
                        st.toast(f"Dialing {number}...")
                        st.session_state['call_active'] = True
                        st.session_state['current_number'] = number
            with c_b:
                if st.button("🔴 HANG UP", type="secondary", disabled=not is_connected):
                     bridge.end_call()
                     st.session_state['call_active'] = False
                     st.toast("Call Ended.")
            with c_c:
                 if st.button("🔊 WAKE PHONE"):
                     bridge.wake_device()
            
            # THE LIVE CALL LOOP
            st.markdown("#### 💬 LIVE CONVERSATION LOG")
            log_container = st.empty()
            
            # We strictly only run the loop if "Call Active" is true and a specialized button is pressed to "Start AI Agent"
            # This separates "Dialing" from "Talking" to allow the user to enable speakerphone first.
            
            if st.session_state.get('call_active', False):
                 st.info("Call is Active on Phone. Enable Speakerphone!")
                 
                 if st.button("🤖 ACTIVATE AI AGENT (START LISTENING)", key="btn_activate_ai"):
                     # Initialize Core
                     ear = NativeEar()
                     brain = SalesBrain()
                     brain.load_knowledge(kb)
                     mouth.set_voice(voice)
                     
                     history = ""
                     stop_signal = False
                     
                     st.write("🔴 AI IS LISTENING... (Speak into Mic)")
                     
                     # LOOP
                     placeholder = st.empty()
                     
                     while not stop_signal:
                         # 1. Listen
                         user_text = ear.listen(timeout=5)
                         
                         if user_text:
                             history += f"\nProspect: {user_text}"
                             placeholder.markdown(f"**Prospect:** {user_text}")
                             
                             # 2. Think
                             response = brain.think(user_text, history)
                             history += f"\nAI: {response}"
                             placeholder.markdown(f"**Prospect:** {user_text}\n\n**AI:** {response}")
                             
                             # 3. Speak
                             asyncio.run(mouth.speak(response))
                             
                         # Break mechanism?
                         # Streamlit loops are tricky. We might just run for X turns or until error.
                         time.sleep(1)
                         
        with tab_auto:
            st.info("Select a Database Source to auto-dial next.")
            # Future integration to pull from 'maps_leads.csv'
