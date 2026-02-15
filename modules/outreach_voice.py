import os
import time
import streamlit as st
try:
    from twilio.rest import Client
except ImportError:
    Client = None

class CallCenter:
    """
    Handles Telephony Operations via Twilio.
    """
    def __init__(self):
        self.sid = os.getenv("TWILIO_SID")
        self.token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.client = None
        
        if self.sid and self.token:
            try:
                self.client = Client(self.sid, self.token)
            except Exception as e:
                print(f"Twilio Init Error: {e}")

    def make_call(self, to_number, message_url=None, text_to_say=None):
        """
        Triggers a call. 
        Note: TwiML 'play' requires a public URL. 'say' is easier for testing.
        """
        if not self.client:
            return "Error: Twilio not configured."
            
        try:
            # TwiML construction
            twiml = "<Response>"
            if message_url:
                twiml += f"<Play>{message_url}</Play>"
            if text_to_say:
                # Upgrade to Neural Voice for realism
                twiml += f"<Say voice='Polly.Joanna-Neural'>{text_to_say}</Say>"
            twiml += "</Response>"
            
            call = self.client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.from_number
            )
            return f"Call Initiated. SID: {call.sid}"
            
        except Exception as e:
            return f"Twilio Call Failed: {str(e)}"

    def blast_dial(self, leads_list, text_message="Hello, this is a priority call from Volts Design.", delay=60):
        """
        Loops through a list of leads and calls them.
        Safety delay included.
        """
        results = []
        progress_bar = st.progress(0)
        
        for idx, lead in enumerate(leads_list):
            phone = lead.get("Contact") or lead.get("Phone")
            name = lead.get("Name", "Client")
            
            # Basic validation
            if phone and any(char.isdigit() for char in str(phone)):
                # Personalized message
                msg = text_message.replace("{Name}", name)
                
                status = self.make_call(phone, text_to_say=msg)
                results.append(f"{name} ({phone}): {status}")
                
                # Update progress
                progress_bar.progress((idx + 1) / len(leads_list))
                
                # Safety Sleep
                if idx < len(leads_list) - 1:
                    time.sleep(delay)
            else:
                results.append(f"{name}: Skipped (Invalid Phone)")
                
        return results
