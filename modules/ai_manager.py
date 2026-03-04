"""
The Autonomous "Agency in a Box" AI Manager.
This script acts as the master brain:
1. Grabs fresh leads from Supabase.
2. Uses Google Gemini to research the company/lead and write a personalized Ice Breaker.
3. Automatically dispatches the Vapi AI Voice Agent to call them using the custom Ice Breaker.
4. (Future) Listens to webhooks to dispatch emails.
"""

import os
import time
from dotenv import load_dotenv
from google import genai
import modules.db_supabase as db
import requests
import streamlit as st

load_dotenv()

def analyze_lead_with_gemini(lead_data):
    """
    Uses Google Gemini (Free Tier) to read the lead's data and 
    craft a highly personalized, natural-sounding ice breaker for the voice bot.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    try:
        if 'USER_GEMINI_API_KEY' in st.session_state and st.session_state['USER_GEMINI_API_KEY']:
            api_key = st.session_state['USER_GEMINI_API_KEY']
    except:
        pass
        
    if not api_key:
        print("Error: GEMINI_API_KEY missing.")
        return "Hey there, I saw your business online and wanted to connect."

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Gemini Init Error: {e}")
        return "Hey there, I wanted to quickly reach out about your business. Do you have a quick second?"
    
    prompt = f"""
    You are an elite Inside Sales Hacker preparing a call script for an AI Voice Agent.
    
    Target Lead Information:
    Name: {lead_data.get('name', 'Unknown')}
    Company/Bio: {lead_data.get('bio', 'Unknown')}
    Industry/Notes: {lead_data.get('notes', 'Unknown')}
    
    TASK: Write a 1-2 sentence "Ice Breaker" for the AI Agent to say right after the prospect answers the phone.
    
    RULES:
    1. It must sound extremely natural and conversational, NOT like a robot reading a script.
    2. Reference something specific about their company or bio to prove we did our research.
    3. End with a soft question to keep them talking.
    4. NO EMOJIS, DO NOT write any actions like [pauses], just the raw text the AI will speak.
    
    Example: 'Hey Sarah, I was just looking at your recent post about the new real estate regulations in KL, completely agree with your take. How is your team handling the transition so far?'
    
    Write the Ice Breaker now:
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ice_breaker = response.text.strip().replace('"', '')
        print(f"🧠 Gemini crafted Ice Breaker for {lead_data.get('name')}: {ice_breaker}")
        return ice_breaker
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Hey there, I wanted to quickly reach out about your business. Do you have a quick second?"

def dispatch_vapi_call(lead_data, ice_breaker):
    """
    Triggers the Vapi AI to call the lead, injecting the Gemini Ice Breaker 
    directly into the AI's system prompt instructions.
    """
    
    vapi_key = os.getenv("VAPI_API_KEY")
    vapi_id = os.getenv("VAPI_PHONE_ID")
    
    try:
        if 'USER_VAPI_API_KEY' in st.session_state and st.session_state['USER_VAPI_API_KEY']:
            vapi_key = st.session_state['USER_VAPI_API_KEY']
        if 'USER_VAPI_PHONE_ID' in st.session_state and st.session_state['USER_VAPI_PHONE_ID']:
            vapi_id = st.session_state['USER_VAPI_PHONE_ID']
    except:
        pass
    
    if not vapi_key or not vapi_id:
        print("Error: Vapi API keys missing.")
        return False
        
    phone = lead_data.get('phone')
    if not phone:
        print(f"Skipping {lead_data.get('name')}: No phone number.")
        return False
    headers = {
        'Authorization': f'Bearer {vapi_key}',
        'Content-Type': 'application/json',
    }

    # Elite Sales Framework Prompt
    system_prompt = f"""
    You are an elite, top-tier business consultant calling from Volts Design.
    You are calling {lead_data.get('name')}.
    
    YOUR FIRST SENTENCE MUST BE EXACTLY THIS (AND NOTHING ELSE):
    "{ice_breaker}"
    
    YOUR DIRECTIVE:
    You are qualifying them for our automated design and marketing services. 
    1. Never pitch immediately. 
    2. Use the "Acknowledge & Pivot" framework if they give an objection. (e.g., "I totally understand timing is tough right now, but just out of curiosity...")
    3. THE ONE QUESTION RULE: Never ask more than one question at a time.
    4. Speak casually, use filler words naturally (like 'um', 'you know'), but maintain absolute authority.
    
    If they are interested, tell them you will email them the portfolio right after the call.
    """

    payload = {
        "phoneNumberId": vapi_id,
        "customer": {
            "number": phone,
            "name": lead_data.get('name', '')
        },
        "assistantOverrides": {
            "model": {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(
            'https://api.vapi.ai/call/phone', 
            headers=headers, 
            json=payload
        )
        if response.status_code == 201:
            call_id = response.json().get('id', 'Unknown')
            print(f"📞 Vapi Dispatched to {lead_data.get('name')} (Call ID: {call_id})")
            return call_id
        else:
            print(f"Vapi Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to trigger Vapi: {e}")
        return False

def run_daily_campaign(user_id=None, max_leads=5):
    """
    The master loop. Grabs 'New' leads, researches them, and calls them automatically.
    """
    print("🚀 Initiating Zero Bullshit Autonomous Campaign...")
    
    # 1. Get raw leads from Supabase
    df = db.get_all_leads(user_id=user_id)
    if df.empty:
        print("No leads found in database.")
        return 0
        
    # 2. Filter for actionable leads (New, Has Phone)
    pipeline = df[(df['status'] == 'New') & (df['phone'].notna()) & (df['phone'] != '')].head(max_leads)
    
    if len(pipeline) == 0:
        print("No actionable 'New' leads with phone numbers found.")
        return 0
        
    print(f"🎯 Found {len(pipeline)} qualified leads. Beginning execution sequence.")
    
    calls_made = 0
    for index, row in pipeline.iterrows():
        lead_data = {
            'id': row['id'],
            'name': row['name'],
            'phone': row['phone'],
            'bio': row['bio'],
            'notes': row['notes']
        }
        
        # 1. Brain: Gemini Research
        breaker = analyze_lead_with_gemini(lead_data)
        
        # 2. Action: Vapi Call
        call_id = dispatch_vapi_call(lead_data, breaker)
        
        if call_id:
            # 3. CRM Update: Mark as Actioned
            conn = db.get_connection()
            if conn:
                try:
                    c = conn.cursor()
                    c.execute("UPDATE leads SET status = 'Contacted' WHERE id = %s", (row['id'],))
                    conn.commit()
                except Exception as e:
                    print(f"DB Update Error: {e}")
                finally:
                    conn.close()
                    
            calls_made += 1
            
            # Anti-Spam Rate Limit: Wait 30 seconds before dialing the next person 
            # to let the current call breathe and avoid API throttling.
            if calls_made < len(pipeline):
                print("Sleeping 30s before next dial to respect rate limits...")
                time.sleep(30)
                
    print(f"✅ Autonomous Campaign Complete. Total Dials: {calls_made}")
    return calls_made

if __name__ == "__main__":
    # Test execution for the first 2 leads
    run_daily_campaign(max_leads=2)
