import os
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from pyngrok import ngrok
import threading
import json
import time
from datetime import datetime
from modules.ai_engine import AIGhostwriter

# Global Configuration
LOG_FILE = "logs/titan_calls.json"
os.makedirs("logs", exist_ok=True)

# Global State
app = FastAPI()
SERVER_PORT = 8000
TUNNEL_URL = None
system_prompt = "You are a helpful AI assistant. Keep answers short and conversational."

# --- Helper: Logging ---
def log_interaction(call_sid, role, content):
    """Appends interaction to the log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "call_sid": call_sid,
        "role": role,
        "content": content
    }
    
    # Simple file append (Thread-safe enough for low volume)
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                data = json.load(f)
        except: pass
    
    data.append(entry)
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# --- Routes ---

@app.post("/voice")
async def voice(request: Request):
    """Start of Call."""
    form = await request.form()
    call_sid = form.get('CallSid', 'unknown')
    
    log_interaction(call_sid, "system", "Call Started")
    
    resp = VoiceResponse()
    # 1. Greet
    greeting = "Hello! Titan AI listening."
    resp.say(greeting)
    
    # 2. Listen
    gather = Gather(input='speech', action='/gather', speechTimeout='auto')
    resp.append(gather)
    resp.redirect('/voice') # Loop
    
    return PlainTextResponse(str(resp), media_type="application/xml")

@app.post("/gather")
async def gather(request: Request):
    """Process Speech."""
    form = await request.form()
    call_sid = form.get('CallSid', 'unknown')
    speech_result = form.get('SpeechResult', '')
    
    resp = VoiceResponse()
    
    if speech_result:
        print(f"[USER] ({call_sid}): {speech_result}")
        log_interaction(call_sid, "user", speech_result)
        
        # 1. AI Generation
        ghostwriter = AIGhostwriter() # Re-init to ensure fresh env if needed
        full_context = f"{system_prompt}\n\nUser said: {speech_result}\n\nReply (Text only, no markdown):"
        
        try:
            # Ghostwriter now automatically injects business_profile.txt context
            ai_reply = ghostwriter.generate_content(full_context).replace("*", "").strip()
        except Exception as e:
            ai_reply = "I am having trouble thinking right now."
            print(f"AI Error: {e}")
            
        print(f"[AI]: {ai_reply}")
        log_interaction(call_sid, "ai", ai_reply)
        
        # 2. Speak
        resp.say(ai_reply)
        
        # 3. Listen Again
        gather = Gather(input='speech', action='/gather', speechTimeout='auto')
        resp.append(gather)
    else:
        resp.redirect('/voice')
        
    return PlainTextResponse(str(resp), media_type="application/xml")


import subprocess

class TitanTelephony:
    def __init__(self):
        self.public_url = None

    def start_server(self):
        """Starts FastAPI + Ngrok. Returns (url, error)."""
        global TUNNEL_URL
        
        # Prevent double-start
        if TUNNEL_URL:
            return TUNNEL_URL, None
            
        try:
            # 1. HARD CLEANUP: Kill all zombie ngrok processes
            print("[INFO] Performing Hard Reset on Tunnels...")
            try:
                subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1) # Wait for death
            except Exception as k:
                print(f"[WARN] Kill failed: {k}")

            # 2. Ngrok Connect
            # Change Port to 8080 to avoid generic 8000 conflicts
            NEW_PORT = 8082
            
            print("[INFO] Starting Ngrok Tunnel...")
            
            # Re-init ngrok to ensure clean slate
            ngrok.kill()
            tunnel = ngrok.connect(NEW_PORT)
            self.public_url = tunnel.public_url.replace("http://", "https://")
            
            # Update Global
            TUNNEL_URL = self.public_url
            print(f"[SUCCESS] TITAN TUNNEL: {TUNNEL_URL}")
            
            # 2. Uvicorn (Background)
            def run_server():
                uvicorn.run(app, host="0.0.0.0", port=NEW_PORT, log_level="error")
                
            t = threading.Thread(target=run_server, daemon=True)
            t.start()
            
            return self.public_url, None
            
        except Exception as e:
            err_msg = str(e)
            print(f"[ERROR] Server Boot Failed: {err_msg}")
            return None, err_msg

    def update_system_prompt(self, new_prompt):
        global system_prompt
        system_prompt = new_prompt
        # Log the change
        log_interaction("SYSTEM", "admin", f"Prompt Updated: {new_prompt[:50]}...")

    def make_call(self, to_number, from_number, sid, token):
        if not TUNNEL_URL:
            return "Error: Internal Server Offline. URL missing."
            
        try:
            client = Client(sid, token)
            call = client.calls.create(
                to=to_number,
                from_=from_number,
                url=f"{TUNNEL_URL}/voice"
            )
            return f"Dialing... SID: {call.sid}"
        except Exception as e:
            return f"Twilio API Error: {e}"

    def verify_number(self, phone_number, sid, token):
        """Triggers a Twilio Verification Call."""
        try:
            client = Client(sid, token)
            validation = client.validation_requests.create(
                friendly_name=phone_number,
                phone_number=phone_number
            )
            return validation.validation_code
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    print("Starting Titan Telecom Server...")
    titan = TitanTelephony()
    url, err = titan.start_server()
    if url:
        print(f"Server is LIVE. Keep this window open.")
        print(f"Tunnel URL: {url}")
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping Server...")
    else:
        print(f"Failed to start: {err}")
