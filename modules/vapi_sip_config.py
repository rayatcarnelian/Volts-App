import os
import requests
import json

class VapiSIPConfigurator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_sip_trunk(self, username, password, domain, name="AlienVoIP Trunk"):
        """
        Creates a SIP Trunk in Vapi.
        """
        url = f"{self.base_url}/credential"
        
        # Corrected Schema: Vapi BYO-SIP-TRUNK (IP Whitelist Mode)
        # We rely on the User whitelisting Vapi IPs in Zadarma side.
        payload = {
            "provider": "byo-sip-trunk",
            "gateways": [
                {
                    "ip": domain, 
                    "port": 5060,
                }
            ],
            "outboundAuthenticationPlan": {
                "type": "digest",
                "username": username,
                "password": password
            },
            # sipRegisterPlan Removed (Vapi doesn't support it for BYO, likely)
            "name": name 
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": f"{response.status_code} - {response.text}"}
        except Exception as e:
            return {"error": str(e)}

    def list_phone_numbers(self):
        url = f"{self.base_url}/phone-number"
        try:
             res = requests.get(url, headers=self.headers)
             return res.json()
        except: return []

    def bind_number_to_assistant(self, phone_id, assistant_id):
        url = f"{self.base_url}/phone-number/{phone_id}"
        payload = {"assistantId": assistant_id}
        requests.patch(url, headers=self.headers, json=payload)

    def create_twilio_credential(self, sid, token, name="My Twilio Account"):
        """
        Links User's Twilio Account to Vapi.
        """
        url = f"{self.base_url}/credential"
        # "Shotgun" Schema: Vapi validation demanded ALL 4 fields in previous errors.
        # We map SID->apiKey and Token->apiSecret for compatibility.
        payload = {
            "provider": "twilio",
            "accountSid": sid,
            "authToken": token,
            "apiKey": sid,      # redundantly mapped
            "apiSecret": token, # redundantly mapped
            "name": name
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": f"{response.status_code} - {response.text}"}
        except Exception as e:
            return {"error": str(e)}
