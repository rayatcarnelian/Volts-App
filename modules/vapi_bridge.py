import requests
import json
import os
import streamlit as st

class VapiBridge:
    def __init__(self, api_key=None):
        self.api_key = api_key if api_key else os.getenv("VAPI_PRIVATE_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def start_call(self, phone_number, system_prompt, initial_message=None):
        """
        Initiates an outbound call using an Ephemeral Assistant.
        """
        if not self.api_key:
            return {"error": "Missing API Key"}

        url = f"{self.base_url}/call/phone"
        
        # Default Configuration (Robust Ephemeral Assistant)
        payload = {
            "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"), # User needs to buy one on Vapi or use their free one if available? Actually Vapi requires buying a number usually or attaching Twilio. 
            # For this 'Free' request, Vapi has a free tier but maybe not free numbers. 
            # We will ask user for input or use a simplified payload.
            # Wait, if they don't have a phone number ID, this fails.
            # Vapi usually requires a phoneNumberId attached to the account.
            # Let's assume user inputs it or we handle the error.
            
            "customer": {
                "number": phone_number
            },
            "assistant": {
                "firstMessage": initial_message if initial_message else "Hello?",
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ]
                },
                "voice": {
                    "provider": "11labs", # Good default
                    "voiceId": "burt",    # Standard American Male
                },
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2"
                }
            }
        }
        
        # If user provides a specific phone number ID in env, use it. 
        # If not, Vapi might fail. We'll handle that in UI validation.
        phone_id = os.getenv("VAPI_PHONE_ID")
        if phone_id:
             payload["phoneNumberId"] = phone_id
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}

    def get_call_analytics(self, call_id):
        """
        Retrieves transcript and status.
        """
        if not self.api_key: return {}
        
        url = f"{self.base_url}/call/{call_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": data.get("status"),
                    "transcript": data.get("transcript"),
                    "summary": data.get("summary"),
                    "recording_url": data.get("recordingUrl"),
                    "cost": data.get("cost")
                }
            return {}
        except:
            return {}
            
    def validate_key(self):
        """Simple check to see if key works."""
        if not self.api_key: return False
        try:
            r = requests.get(f"{self.base_url}/assistant", headers=self.headers, timeout=30)
            return r.status_code == 200
        except:
            return False
