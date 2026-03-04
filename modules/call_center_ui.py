import streamlit as st
import os
import time
import json
# Import VapiClient directly (Global Scope)
from modules.vapi_client import VapiClient
import modules.auth as auth
import modules.db_supabase as db
import pandas as pd

def render_call_center_ui():
    """
    AI Dialer with Authentication, Minute Tracking, and Billing.
    FREE = 2 min trial. PRO ($15) = 100 min.
    """
    
    # ================================================================
    # 0. AUTH GATEKEEPER — Must be logged in via Studio Auth
    # ================================================================
    if "user" not in st.session_state or not st.session_state.get("user"):
        st.title("AI DIALER")
        st.warning(" Please log in via **Content Studio** first to use the AI Dialer.")
        st.info("Go to sidebar → **3. Content Studio** → Login or Create Account.")
        return
    
    user = st.session_state["user"]
    user_id = user["id"]
    tier = "PRO" # Unlimited Access
    
    # ================================================================
    # 1. HEADER: Usage Meter
    # ================================================================
    st.title("TELEPHONY COMMAND")
    st.caption("Enterprise Cloud Voice • Low Latency • Vapi.ai Neural Engine")
    
    # Unlimited Credits for current deployment
    mins_used = 0
    mins_limit = 9999
    mins_remaining = 9999
    
    # Usage Bar
    h1, h2, h3 = st.columns([2, 1, 1])
    with h1:
        progress = min(1.0, mins_used / mins_limit) if mins_limit > 0 else 1.0
        st.progress(progress)
        st.caption(f"**{mins_remaining} min** remaining of {mins_limit} min ({tier})")
    with h2:
        if tier == "FREE":
            st.markdown(f"<div style='background:#1A1708;padding:8px 12px;border-radius:8px;text-align:center;color:#C5A55A;font-weight:600;'>FREE TRIAL<br><span style='font-size:0.8rem;color:#888;'>{mins_limit} min</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#064e3b;padding:8px 12px;border-radius:8px;text-align:center;color:#6ee7b7;font-weight:600;'>{tier} PLAN<br><span style='font-size:0.8rem;color:#888;'>{mins_limit} min/mo</span></div>", unsafe_allow_html=True)
    with h3:
        if tier == "FREE":
            if st.button("Upgrade ($15/mo → 100 min)"):
                st.session_state["user"]["tier"] = "PRICING_VIEW"
                st.rerun()
    
    st.markdown("---")
    
    # ================================================================
    # 2. MINUTE CHECK — Block if exhausted
    # ================================================================
    if mins_remaining <= 0:
        st.error("OUT OF MINUTES")
        if tier == "FREE":
            st.markdown("""
                <div style='background:linear-gradient(135deg,#1A1708,#000);padding:2rem;border-radius:15px;border:1px solid #3D3520;text-align:center;margin:1rem 0;'>
                    <h3 style='color:#C5A55A;'>Your 2-Minute Free Trial Has Ended</h3>
                    <p style='color:#999;'>Upgrade to PRO for <b>100 minutes</b> of AI calling per month.</p>
                    <h2 style='color:white;'>$15<span style='font-size:1rem;color:#666;'>/month</span></h2>
                    <p style='color:#6ee7b7;'>100 AI call minutes &nbsp;•&nbsp; All voices &nbsp;•&nbsp; Transcripts</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Upgrade to PRO", type="primary", use_container_width=True):
                st.session_state["user"]["tier"] = "PRICING_VIEW"
                st.rerun()
        else:
            st.warning("You've used all your minutes this month. Your quota resets on the next billing cycle.")
        return
    
    # ================================================================
    # 3. CLOUD CONFIGURATION CHECK
    # ================================================================
    api_key = db.get_user_setting(user_id, "VAPI_API_KEY")
    phone_id = db.get_user_setting(user_id, "VAPI_PHONE_ID")
    
    if not api_key or not phone_id:
        st.error("CLOUD CREDENTIALS MISSING")
        st.info("Go to **SETTINGS** in the sidebar to configure your personal Vapi Keys.")
        st.code(f"Key Present: {bool(api_key)}\nID Present: {bool(phone_id)}")
        return

    # --- MAIN INTERFACE ---
    client = VapiClient(api_key)
    
    # --- TABS: DIALER vs AUTO-PILOT vs DATABASE ---
    tab_dialer, tab_auto, tab_db = st.tabs(["🎯 MANUAL DIAL", "🤖 AUTO-PILOT", "📊 DATABASE"])

    # --- TAB 1: DIALER ---
    with tab_dialer:
        st.success(f"CLOUD VOICE ACTIVE | ⏱️ {mins_remaining} min remaining")
        
        c1, c2 = st.columns([1, 1], gap="large")

        with c1:
            st.subheader(" OUTBOUND LINK")
            
            # --- DYNAMIC CRM INJECTION (RAG) ---
            dial_mode = st.radio("Target Source", ["Manual Number", "CRM Lead"], horizontal=True)
            
            target_ph = ""
            lead_context = ""
            
            if dial_mode == "Manual Number":
                target_ph = st.text_input("TARGET NUMBER", placeholder="+60123456789", help="E.164 Format advised")
            else:
                leads_df = db.get_all_leads(user_id)
                # Filter leads with phone numbers
                leads_df = leads_df[leads_df['phone'].notna() & (leads_df['phone'] != '')]
                
                if leads_df.empty:
                    st.warning("No leads with phone numbers found in your CRM.")
                else:
                    # Create a display format
                    leads_list = leads_df.apply(lambda row: f"{row['name']} ({row['phone']}) - ID: {row['id']}", axis=1).tolist()
                    selected_lead_str = st.selectbox("Select Lead to Dial", leads_list)
                    
                    if selected_lead_str:
                        lead_id = int(selected_lead_str.split("ID: ")[1])
                        lead_row = leads_df[leads_df['id'] == lead_id].iloc[0]
                        target_ph = lead_row['phone']
                        
                        # Build Lead Context for AI Prompt
                        st.info(f"⚡ RAG Linked: Injecting data for **{lead_row['name']}** into AI Brain.")
                        lead_context = f"\n\n--- LEAD CONTEXT (READ THIS BEFORE CALLING) ---\n"
                        lead_context += f"Prospect Name: {lead_row['name']}\n"
                        if pd.notna(lead_row.get('bio')): lead_context += f"Profile/Bio: {lead_row['bio']}\n"
                        if pd.notna(lead_row.get('pain_points')): lead_context += f"Known Pain Points: {lead_row['pain_points']}\n"
                        if pd.notna(lead_row.get('ice_breaker')): lead_context += f"Suggested Icebreaker: {lead_row.get('ice_breaker')}\n"
                        if pd.notna(lead_row.get('notes')): lead_context += f"CRM Notes: {lead_row['notes']}\n"
            
            # --- AGENT COMMAND CENTER ---
            
            # Load Agents
            AGENTS_FILE = "modules/agents.json"
            if not os.path.exists(AGENTS_FILE):
                default_agents = {"Tahmid (Default)": {"prompt": "You are Tahmid...", "voice_id": "ErXwobaYiN019PkySvjV", "first_message": "Hello?"}}
                with open(AGENTS_FILE, "w") as f: json.dump(default_agents, f)
                
            with open(AGENTS_FILE, "r") as f:
                known_agents = json.load(f)
                
            st.markdown("####  AGENT NEURAL CORE")
            
            # Selection
            agent_names = list(known_agents.keys())
            selected_agent_name = st.selectbox("Select Active Agent", agent_names, index=0)
            agent_data = known_agents[selected_agent_name]
            
            # Handle Legacy (String) vs New (Dict) format
            if isinstance(agent_data, str):
                agent_data = {"prompt": agent_data, "voice_id": "burt", "first_message": "Hello?"}

            # Training / Editing Area
            with st.expander(" TRAIN / EDIT AGENT", expanded=False):
                edit_name = st.text_input("Name", value=selected_agent_name)
                
                # Voice Library with PREVIEW URLs
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
                if current_voice_id == "burt": current_voice_id = "ErXwobaYiN019PkySvjV"
                
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
                
                if st.button(" SAVE AGENT"):
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
                if st.button("INITIATE CALL", type="primary", use_container_width=True):
                     if not target_ph:
                         st.error("Enter a Target Number.")
                     else:
                         # ============================================
                         # PRE-CALL CHECK: Do they have minutes?
                         # ============================================
                         if not auth.can_make_call(user_id):
                             st.error("Out of minutes! Upgrade to continue.")
                             st.stop()
                         
                         # Smart Formatting (E.164)
                         raw = target_ph.strip().replace(" ", "").replace("-", "")
                         formatted_ph = raw
                         
                         if raw.startswith("+"):
                             formatted_ph = raw
                         elif raw.startswith("880"):
                             formatted_ph = "+" + raw
                         elif raw.startswith("60"):
                             formatted_ph = "+" + raw
                         elif raw.startswith("1") and len(raw) == 11:
                             formatted_ph = "+" + raw
                         elif raw.startswith("0"):
                             formatted_ph = "+60" + raw[1:]
                         else:
                             st.warning(f"Please use E.164 format: +[country code][number].")
                             formatted_ph = raw
                              
                         st.caption(f"Dialing: {formatted_ph}...")
                         
                         # Record start time for duration tracking
                         call_start_time = time.time()
                         
                         # ============================================
                         # PHASE 6: MASTER SALESMAN + DYNAMIC RAG INJECTION
                         # ============================================
                         master_salesman_framework = """
\n\n--- ELITE SALES FRAMEWORK (MANDATORY RULES) ---
1. THE ONE QUESTION RULE: You MUST speak in short, concise bursts. NEVER talk for more than 15 seconds at a time. EVERY SINGLE TIME you stop talking, you MUST end with a question to pass the microphone back to the prospect.
2. VALUE-FIRST APPROACH: NEVER say "How are you today?" or "Did I catch you at a bad time?". Be direct, confident, and immediately state the value you provide or the specific pain point you are calling to solve.
3. OBJECTION HANDLING: 
  - If they say "I'm not interested": Use a pattern interrupt. Say "I completely understand, and honestly I figured you'd say that since I called out of the blue. But if I could show you how we solved [mention a pain point or value proposition], would you give me 30 seconds?"
  - If they say "Send me an email": Use Feel-Felt-Found. Say "I can absolutely do that. Just so I make sure I send you the most relevant information, what is your biggest challenge with [industry/topic] right now?"
4. NATURAL PACING: Use natural filler words like "hmm", "yeah", "I see" occasionally. Pause for a split second before answering so it feels like a real human conversation.
"""
                         final_prompt = agent_data.get("prompt", "") + master_salesman_framework + lead_context
                         
                         with st.spinner("Establishing Neural Uplink..."):
                             res = client.start_call(
                                 formatted_ph, 
                                 prompt_override=final_prompt, 
                                 first_message=agent_data.get("first_message"),
                                 voice_id=agent_data.get("voice_id"),
                                 phone_id=phone_id
                             )
                             
                             if "error" in res:
                                 st.error(f"Uplink Failed: {res['error']}")
                             else:
                                 st.success("SIGNAL LOCKED. CALLING...")
                                 st.toast("AI Agent Dispatched!")
                                 
                                 # Store call ID for tracking
                                 st.session_state["active_call_id"] = res.get("id")
                                 st.session_state["call_start_time"] = call_start_time
                                 
                                 # Display Call Info
                                 with st.expander("CONNECTION LOG", expanded=True):
                                     st.json(res)
                                     st.caption(f"Call ID: {res.get('id')}")
                                     st.info("⏱️ Minutes will be deducted when the call ends. Click 'Sync Minutes' to update.")
        
            # ============================================
            # POST-CALL: Sync Minutes Button
            # ============================================
            st.markdown("---")
            if st.button(" Sync Minutes (After Call Ends)", use_container_width=True):
                with st.spinner("Fetching call duration from Vapi..."):
                    _sync_call_minutes(client, user_id)
                    st.rerun()

        with c2:
            st.subheader("LIVE TELEMETRY")
            
            # --- CACHED DATA FETCHING ---
            @st.cache_data(ttl=30, show_spinner=False)
            def get_cached_history():
                try:
                    return client.get_calls(limit=10)
                except:
                    return []

            # Call History / Logs
            col_h1, col_h2 = st.columns([2, 1])
            col_h1.info("Fetching recent transmissions...")
            
            if col_h2.button(" SYNC DB"):
                with st.spinner("Downloading Transcripts..."):
                    from modules.call_logger import CallLogger
                    full_history = client.get_calls(limit=50)
                    if full_history and "error" not in full_history:
                        msg = CallLogger.save_logs(full_history)
                        st.success(msg)
                        get_cached_history.clear() # Clear cache on sync
                    else:
                        st.error("Failed to fetch logs.")
            
            try:
                history = get_cached_history()
                if history:
                     for call in history:
                         status = call.get('status', 'unknown')
                         cost = call.get('cost', 0)
                         dest = call.get('customer', {}).get('number', 'Unknown')
                         ended_reason = call.get('endedReason', '-')
                         duration = call.get('duration', 0) # seconds
                         
                         icon = "" if status == "in-progress" else "" if status == "ended" else ""
                         
                         with st.container(border=True):
                             h_c1, h_c2 = st.columns([3, 1])
                             with h_c1:
                                 st.markdown(f"**{dest}**")
                                 st.caption(f"ID: {call.get('id')[-8:]}...")
                             with h_c2:
                                 st.markdown(f"{icon} {status.upper()}")
                             
                             if status == "ended":
                                 dur_min = round(duration / 60, 1) if duration else 0
                                 st.caption(f"Duration: {dur_min} min | Reason: {ended_reason} | Cost: ${cost:.4f}")
                else:
                    st.caption("No recent signals found.")
            except Exception as e:
                st.warning(f"Telemetry Offline: {e}")
    
        # --- ADVANCED / DEBUG ---
        with st.expander("DEBUG TOOLS", expanded=False):
            st.text("Vapi Phone ID: " + phone_id)
            if st.button("Ping Vapi Server"):
                st.write(client.get_calls(1))

    # --- TAB 2: AUTO-PILOT CAMPAIGN ---
    with tab_auto:
        st.subheader("Autonomous AI Agency Pipeline")
        st.caption("Let the Google Gemini Brain research your leads, write custom pitches, and sequentially dial them through Vapi.")
        
        st.markdown("""
        <div style='background:#1a1708; border:1px solid #c5a55a; padding:15px; border-radius:8px; margin-bottom:20px;'>
            <h4 style='color:#c5a55a; margin-top:0;'>Zero Bullshit Mode</h4>
            <p style='color:#ccc; font-size:14px;'>
                1. <b>Scans</b> Supabase for leads marked as 'New'.<br>
                2. <b>Researches</b> their bio using Google Gemini to write a personalized Ice-Breaker.<br>
                3. <b>Dials</b> them via Vapi and injects the Ice-Breaker into the opening line.<br>
                4. <b>Updates</b> the CRM automatically to 'Contacted'.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            max_dials = st.slider("Maximum Leads to Call", min_value=1, max_value=50, value=5)
            
        with c2:
            st.write("")
            st.write("")
            if st.button("🚀 LAUNCH DAILY CAMPAIGN", type="primary", use_container_width=True):
                with st.status("Initiating Autonomous Protocol...", expanded=True) as status:
                    st.write("Waking up Gemini Brain...")
                    import modules.ai_manager as ai
                    st.write("Querying Supabase database...")
                    calls_made = ai.run_daily_campaign(user_id=user_id, max_leads=max_dials)
                    status.update(label=f"Campaign Complete. Dispatched {calls_made} calls.", state="complete", expanded=False)
                
                if calls_made > 0:
                    st.success(f"Successfully ran autonomous campaign for {calls_made} leads.")
                else:
                    st.warning("No 'New' leads with phone numbers found in the CRM.")

    # --- TAB 3: DATABASE VIEW ---
    with tab_db:
        st.subheader("CALL TRANSCRIPT DATABASE")
        st.caption("View and Analyze previous interactions.")
        
        # Usage Summary
        st.markdown(f"""
            <div style='background:#111;padding:1rem;border-radius:10px;border:1px solid #333;margin-bottom:1rem;'>
                <b style='color:#C5A55A;'>This Month's Usage</b><br>
                <span style='color:#eee;font-size:1.5rem;font-weight:700;'>{mins_used} min</span>
                <span style='color:#666;'> / {mins_limit} min</span>
                <br><span style='color:#6ee7b7;'> Your cost: ~${mins_used * 0.08:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
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
            
            st.markdown("###  Transcript Viewer")
            selected_id = st.selectbox("Select Call ID to Read Transcript", df['Call ID'].unique())
            
            if selected_id:
                row = df[df['Call ID'] == selected_id].iloc[0]
                st.text_area("Full Transcript", value=row.get('Transcript', 'No Transcript Available'), height=400)
        else:
            st.warning("No Database Found. Go to the **Dialer** tab and click **' SYNC DB'** to create it.")


def _sync_call_minutes(client, user_id):
    """
    Fetches recent calls from Vapi and deducts actual duration from user's balance.
    Only deducts for calls not yet tracked (uses session tracking).
    """
    try:
        history = client.get_calls(limit=20)
        if not history:
            st.info("No calls found.")
            return
        
        # Track which calls we've already deducted for
        if "deducted_call_ids" not in st.session_state:
            st.session_state["deducted_call_ids"] = set()
        
        total_new_minutes = 0
        new_calls = 0
        
        for call in history:
            call_id = call.get("id")
            status = call.get("status")
            duration_seconds = 0
            
            # Get duration from Vapi response
            if "startedAt" in call and "endedAt" in call:
                try:
                    from datetime import datetime
                    started = datetime.fromisoformat(call["startedAt"].replace("Z", "+00:00"))
                    ended = datetime.fromisoformat(call["endedAt"].replace("Z", "+00:00"))
                    duration_seconds = (ended - started).total_seconds()
                except:
                    pass
            
            # Fallback: use 'duration' field if available
            if duration_seconds == 0:
                duration_seconds = call.get("duration", 0)
            
            # Only deduct for ended calls we haven't tracked yet
            if call_id and call_id not in st.session_state["deducted_call_ids"] and status == "ended" and duration_seconds > 0:
                minutes = round(duration_seconds / 60, 2)
                total_new_minutes += minutes
                new_calls += 1
                st.session_state["deducted_call_ids"].add(call_id)
        
        if total_new_minutes > 0:
            auth.deduct_call_minutes(user_id, total_new_minutes)
            st.success(f"Synced {new_calls} call(s). Deducted {round(total_new_minutes, 1)} minutes.")
        else:
            st.info("No new completed calls to sync.")
            
    except Exception as e:
        st.error(f"Sync Error: {e}")
