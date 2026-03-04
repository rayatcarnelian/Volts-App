"""
Vapi Webhook Listener & Email Closer
This runs outside of Streamlit to catch real-time End-of-Call reports from Vapi.
When a call ends, it uses Gemini to analyze the transcript. 
If the prospect wanted an email, it auto-drafts and sends the portfolio.
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from google import genai
from modules.outreach_email import EmailBlaster
import modules.db_supabase as db

load_dotenv()
app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_transcript_and_email(call_data: dict):
    """
    Reads the Vapi call transcript using Gemini to decide if an email should be sent.
    """
    transcript = call_data.get('transcript', '')
    customer_phone = call_data.get('customer', {}).get('number', '')
    
    if not transcript or not customer_phone:
        print("Webhook: Missing transcript or phone number. Skipping.")
        return

    print(f"🔍 Analyzing transcript for {customer_phone}...")

    if not GEMINI_API_KEY:
         print("Webhook: GEMINI_API_KEY missing. Cannot analyze transcript.")
         return

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are an AI Sales Manager. Read the following phone call transcript.
    
    TRANSCRIPT:
    {transcript}
    
    TASK: Did the customer explicitly agree to receive an email, portfolio, or more information?
    Answer ONLY with "YES" or "NO".
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        decision = response.text.strip().upper()
        
        if "YES" in decision:
            print(f"🎯 Positive outcome detected for {customer_phone}. Triggering Auto-Emailer!")
            
            # 1. Lookup lead by phone to get their email
            df = db.get_all_leads()
            lead_match = df[df['phone'] == customer_phone]
            
            if not lead_match.empty:
                lead_email = lead_match.iloc[0].get('email', '')
                lead_name = lead_match.iloc[0].get('name', 'there')
                
                if pd.notna(lead_email) and lead_email != '':
                    # 2. Trigger the Email Blaster
                    blaster = EmailBlaster()
                    subject = f"Volts Design Portfolio - As requested!"
                    body = f"Hi {lead_name},\n\nGreat speaking with you just now. As promised, here is the link to our portfolio: https://voltsdesign.com/portfolio\n\nLet me know when you have time to chat next week.\n\nBest,\nHazem\nVolts Design Team"
                    
                    blaster.send_email(lead_email, subject, body)
                    print(f"📧 Auto-Email successfully sent to {lead_email}!")
                else:
                    print(f"⚠️ Prospect wanted an email, but no email address found in CRM for {customer_phone}.")
            else:
                 print(f"⚠️ Could not find lead in CRM matching phone {customer_phone}.")
                 
        else:
            print(f"❌ Prospect did not request email. Moving on.")
            
    except Exception as e:
        print(f"Webhook Gemini Error: {e}")

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    """
    The endpoint Vapi calls when an event occurs.
    """
    try:
        data = await request.json()
        message = data.get("message", {})
        
        # We only care about the End of Call Report
        if message.get("type") == "end-of-call-report":
            print("\n" + "="*50)
            print(f"🔔 VAPI CALL ENDED. Received Report.")
            call_data = message.get("call", {})
            
            # Process in background (don't block webhook response)
            import threading
            threading.Thread(target=analyze_transcript_and_email, args=(call_data,)).start()
            
        return {"status": "success"}
        
    except Exception as e:
        print(f"Webhook Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Run the server on port 8000
    print("🚀 Starting Autonomous Webhook Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
