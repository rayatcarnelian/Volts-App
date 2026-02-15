import streamlit as st
import os
import time
# Import VapiClient directly (Global Scope)
from modules.vapi_client import VapiClient

def render_call_center_ui():
    st.title("⚡ TELEPHONY COMMAND")
    st.caption("Enterprise Cloud Voice • Low Latency • Vapi.ai Neural Engine")
    st.markdown("---")

    # --- CLOUD CONFIGURATION CHECK ---
    api_key = os.getenv("VAPI_API_KEY", "")
    phone_id = os.getenv("VAPI_PHONE_ID", "")
    
    if not api_key or not phone_id:
        st.error("❌ CLOUD CREDENTIALS MISSING")
        st.info("Go to **SETTINGS** -> **Cloud Voice** to configure your Vapi Keys.")
        st.code(f"Key Present: {bool(api_key)}\nID Present: {bool(phone_id)}")
        return

    # --- MAIN INTERFACE ---
    # Global 'client' variable, no ambiguity
    client = VapiClient(api_key)
    
    # --- TABS: DIALER vs DATABASE vs LEADS ---
    tab_dialer, tab_leads, tab_db = st.tabs(["🚀 DIALER", "📂 LEAD LIST", "🗄️ DATABASE"])

    # --- TAB 1: DIALER ---
    with tab_dialer:
        st.success("✅ CLOUD VOICE ACTIVE (Global Reach)")
        
        c1, c2 = st.columns([1, 1], gap="large")

        with c1:
            st.subheader("📡 OUTBOUND LINK")
            
            # Target Input
            target_ph = st.text_input("TARGET NUMBER", placeholder="+60123456789", help="E.164 Format advised")
            
            # --- AGENT COMMAND CENTER ---
            import json
            
            # Load Agents
            AGENTS_FILE = "modules/agents.json"
            if not os.path.exists(AGENTS_FILE):
                default_agents = {"Tahmid (Default)": "You are Tahmid..."}
                with open(AGENTS_FILE, "w") as f: json.dump(default_agents, f)
                
            with open(AGENTS_FILE, "r") as f:
                known_agents = json.load(f)
                
            st.markdown("#### 🧠 AGENT NEURAL CORE")
            
            # Selection
            agent_names = list(known_agents.keys())
            selected_agent_name = st.selectbox("Select Active Agent", agent_names, index=0)
            agent_data = known_agents[selected_agent_name]
            
            # Handle Legacy (String) vs New (Dict) format
            if isinstance(agent_data, str):
                agent_data = {"prompt": agent_data, "voice_id": "burt", "first_message": "Hello?"}

            # Training / Editing Area
            with st.expander("🎓 TRAIN / EDIT AGENT", expanded=False):
                edit_name = st.text_input("Name", value=selected_agent_name)
                
                # Voice Library with PREVIEW URLs
                # Source: 11Labs Public Samples (Google Storage)
                voice_library = {
                    "Rachel (Female, American)": {
                        "id": "21m00Tcm4TlvDq8ikWAM", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/21m00Tcm4TlvDq8ikWAM/df6788f9-5c96-470d-8312-aab3b3d8f50a.mp3"
                    },
                    "Antoni (Male, Polite)": {
                        "id": "ErXwobaYiN019PkySvjV", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/ErXwobaYiN019PkySvjV/389f41b2-1d54-4a41-a67b-18a04b12dfcb.mp3"
                    },
                    "Josh (Male, Young)": {
                        "id": "TxGEqnHWrfWFTfGW9XjX", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/TxGEqnHWrfWFTfGW9XjX/35b542b2-5cc6-4258-a46f-23677ae967a5.mp3"
                    },
                    "Adam (Male, Deep)": {
                        "id": "pNInz6obpgDQGcFmaJgB", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/pNInz6obpgDQGcFmaJgB/68f7f909-547e-4688-9005-0aed259d4829.mp3"
                    },
                    "Charlie (Male, Casual)": {
                        "id": "IKne3meq5aSn9XLyUdCD", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/102de938-4721-4200-8480-28b67f64464c.mp3"
                    },
                    "Bella (Female, Soft)": {
                        "id": "EXAVITQu4vr4xnSDxMaL", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/0dd1a04d-16a7-47b1-9b62-6ac2144ca308.mp3"
                    },
                     "Fin (Male, British)": {
                        "id": "D38z5RcWu1voky8WS1ja", 
                        "url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/D38z5RcWu1voky8WS1ja/8bc88267-3316-43dd-94e8-f7b53147814b.mp3"
                    }
                }
                
                # Setup
                current_voice_id = agent_data.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
                if current_voice_id == "burt": current_voice_id = "ErXwobaYiN019PkySvjV" # Migrating legacy
                
                # Find Label for ID
                current_label = next((k for k, v in voice_library.items() if v["id"] == current_voice_id), "Rachel (Female, American)")

                c_v1, c_v2 = st.columns([2, 1])
                with c_v1:
                    new_label = st.selectbox("Select Voice Personality", list(voice_library.keys()), index=list(voice_library.keys()).index(current_label))
                    new_id = voice_library[new_label]["id"]
                    preview_url = voice_library[new_label]["url"]
                    
                with c_v2:
                    st.write("") 
                    st.write("")
                    st.audio(preview_url, format="audio/mp3")

                edit_first = st.text_input("First Message (Fixes Silence)", value=agent_data.get("first_message", "Hello?"))
                edit_prompt = st.text_area("Neural Instructions", value=agent_data.get("prompt", ""), height=200)
                
                if st.button("💾 SAVE AGENT"):
                    known_agents[edit_name] = {
                        "prompt": edit_prompt,
                        "voice_id": new_id,
                        "first_message": edit_first
                    }
                    with open(AGENTS_FILE, "w") as f:
                        json.dump(known_agents, f, indent=4)
                    st.success(f"Agent '{edit_name}' Saved!")
                    st.rerun()

            # Display Active Prompt (Read-Only Preview)
            st.caption(f"**Active Voice:** {agent_data.get('voice_id')} | **Opening Line:** \"{agent_data.get('first_message')}\"")
            
            st.markdown("---")
            
            # DIAL BUTTON
            dial_col_1, dial_col_2 = st.columns([2, 1])
            with dial_col_1:
                if st.button("🚀 INITIATE CALL", type="primary", use_container_width=True):
                     if not target_ph:
                         st.error("Enter a Target Number.")
                     else:
                         # Smart Formatting (E.164)
                         raw = target_ph.strip().replace(" ", "").replace("-", "")
                         formatted_ph = raw
                         
                         # If it already starts with +, it's probably correct E.164
                         if raw.startswith("+"):
                             formatted_ph = raw
                         # If it starts with country code (880, 60, 1, etc.), add +
                         elif raw.startswith("880"):  # Bangladesh
                             formatted_ph = "+" + raw
                         elif raw.startswith("60"):  # Malaysia
                             formatted_ph = "+" + raw
                         elif raw.startswith("1") and len(raw) == 11:  # USA/Canada
                             formatted_ph = "+" + raw
                         # If it starts with 0, assume Malaysian mobile (legacy behavior)
                         elif raw.startswith("0"):
                             formatted_ph = "+60" + raw[1:]
                         # Otherwise, warn the user to use E.164 format
                         else:
                             st.warning(f"⚠️ Please use E.164 format: +[country code][number]. Example: +8801712345678 (Bangladesh) or +60123456789 (Malaysia)")
                             formatted_ph = raw  # Send as-is and let Vapi reject it 
                             
                         st.caption(f"Dialing: {formatted_ph}...")
                         
                         with st.spinner("Establishing Neural Uplink..."):
                             # Pass ALL parameters to Client
                             res = client.start_call(
                                 formatted_ph, 
                                 prompt_override=agent_data.get("prompt"), 
                                 first_message=agent_data.get("first_message"),
                                 voice_id=agent_data.get("voice_id"),
                                 phone_id=phone_id
                             )
                             
                             if "error" in res:
                                 st.error(f"Uplink Failed: {res['error']}")
                             else:
                                 st.success("✅ SIGNAL LOCKED. CALLING...")
                                 st.toast("AI Agent Dispatched!", icon="🛰️")
                                 
                                 # Display Call Info
                                 with st.expander("📝 CONNECTION LOG", expanded=True):
                                     st.json(res)
                                     st.caption(f"Call ID: {res.get('id')}")
    
        with c2:
            st.subheader("📊 LIVE TELEMETRY")
            
            # Call History / Logs
            col_h1, col_h2 = st.columns([2, 1])
            col_h1.info("Fetching recent transmissions...")
            
            if col_h2.button("💾 SYNC DB"):
                with st.spinner("Downloading Transcripts..."):
                    from modules.call_logger import CallLogger
                    # Fetch deeper history for logging
                    full_history = client.get_calls(limit=50)
                    if full_history and "error" not in full_history:
                        msg = CallLogger.save_logs(full_history)
                        st.success(msg)
                    else:
                        st.error("Failed to fetch logs.")
            
            try:
                history = client.get_calls(limit=10)
                if history:
                     for call in history:
                         # Parse Vapi Call Object
                         status = call.get('status', 'unknown')
                         cost = call.get('cost', 0)
                         dest = call.get('customer', {}).get('number', 'Unknown')
                         ended_reason = call.get('endedReason', '-')
                         
                         icon = "🟢" if status == "in-progress" else "🔴" if status == "ended" else "🟡"
                         
                         with st.container(border=True):
                             h_c1, h_c2 = st.columns([3, 1])
                             with h_c1:
                                 st.markdown(f"**{dest}**")
                                 st.caption(f"ID: {call.get('id')[-8:]}...")
                             with h_c2:
                                 st.markdown(f"{icon} {status.upper()}")
                             
                             if status == "ended":
                                 st.caption(f"Reason: {ended_reason} | Cost: ${cost:.4f}")
                else:
                    st.caption("No recent signals found.")
            except Exception as e:
                st.warning(f"Telemetry Offline: {e}")
    
        # --- ADVANCED / DEBUG ---
        with st.expander("🛠️ DEBUG TOOLS", expanded=False):
            st.text("Vapi Phone ID: " + phone_id)
            if st.button("Ping Vapi Server"):
                st.write(client.get_calls(1))

    # --- TAB 2: LEAD LIST ---
    with tab_leads:
        st.subheader("📂 Uploaded Leads")
        st.caption("Edit `leads.csv` to add your targets.")
        
        leads_file = "leads.csv"
        if os.path.exists(leads_file):
            import pandas as pd
            df_leads = pd.read_csv(leads_file)
            
            # Interactive Table
            st.data_editor(df_leads, num_rows="dynamic", use_container_width=True, key="leads_editor")
            
            st.markdown("### ⚡ Quick Actions")
            
            # Selector for Calling
            lead_names = df_leads["Name"] + " (" + df_leads["Phone"].astype(str) + ")"
            selected_lead = st.selectbox("Select Lead to Call", lead_names)
            
            if st.button("📞 CALL SELECTED LEAD", type="primary"):
                # Extract Phone from string
                phone_to_call = selected_lead.split("(")[-1].strip(")")
                st.info(f"Initiating call to {phone_to_call}...")
                
                # Trigger Call
                res = client.start_call(
                    phone_to_call, 
                    prompt_override=known_agents[selected_agent_name]["prompt"], # Use active agent settings
                    first_message=known_agents[selected_agent_name]["first_message"],
                    voice_id=known_agents[selected_agent_name]["voice_id"],
                    phone_id=phone_id
                )
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Connected!")
                    time.sleep(1) # UX Pause
        else:
            st.warning("No `leads.csv` found. Create one with columns: Name, Phone.")

    # --- TAB 3: DATABASE VIEW (Below) ---

    with tab_db:
        st.subheader("🗄️ CALL TRANSCRIPT DATABASE")
        st.caption("View and Analyze previous interactions.")
        
        log_file = "call_logs.xlsx"
        if os.path.exists(log_file):
            import pandas as pd
            df = pd.read_excel(log_file)
            
            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Calls", len(df))
            m2.metric("Total Cost", f"${df['Cost ($)'].sum():.2f}")
            m3.metric("Last Update", time.strftime("%H:%M:%S"))

            # Data Table
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### 📜 Transcript Viewer")
            selected_id = st.selectbox("Select Call ID to Read Transcript", df['Call ID'].unique())
            
            if selected_id:
                row = df[df['Call ID'] == selected_id].iloc[0]
                st.text_area("Full Transcript", value=row.get('Transcript', 'No Transcript Available'), height=400)
        else:
            st.warning("No Database Found. Go to the **Dialer** tab and click **'💾 SYNC DB'** to create it.")
