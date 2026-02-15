import os
import requests
import json
from dotenv import load_dotenv

# Load env if available
load_dotenv()

class VapiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def start_call(self, phone_number, prompt_override=None, first_message=None, phone_id=None, voice_id=None):
        """
        Initiates an outbound call via Vapi.
        phone_number: E.164 format (e.g., +60123456789)
        prompt_override: System prompt for this specific call.
        """
        if not self.api_key:
            return {"error": "Missing VAPI_API_KEY"}
            
        pid = phone_id or os.getenv("VAPI_PHONE_ID")
        if not pid:
            return {"error": "Missing VAPI_PHONE_ID (Buy a number in Vapi Dashboard)"}

        # Construct Payload
        payload = {
            "phoneNumberId": pid,
            "customer": {
                "number": phone_number
            },
            "assistant": {
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2", 
                    "language": "en-US"
                },
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o-mini", # Ultra-low latency
                    "messages": [
                        {
                            "role": "system", 
                            "content": prompt_override or "You are a helpful assistant."
                        }
                    ]
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": voice_id or "burt", 
                    "stability": 0.5,
                    "similarityBoost": 0.75
                },
                "silenceTimeoutSeconds": 30, 
                "responseDelaySeconds": 0.8, # Increased to allow user pauses
                # "backchannelingEnabled": True, # DEPRECATED/MOVED
                # "numWordsToInterrupt": 2 # DEPRECATED/MOVED
            }
        }
        
        # Add First Message if provided
        if first_message:
            payload["assistant"]["firstMessage"] = first_message

        try:
            # DEBUG: Log the exact payload being sent
            import json
            print(f"\n{'='*60}")
            print(f"VAPI API CALL DEBUG")
            print(f"{'='*60}")
            print(f"Phone Number: {phone_number}")
            print(f"Phone ID: {pid}")
            print(f"Payload:")
            print(json.dumps(payload, indent=2))
            print(f"{'='*60}\n")
            
            response = requests.post(f"{self.base_url}/call/phone", headers=self.headers, json=payload, timeout=30)
            
            # DEBUG: Log response
            print(f"\n{'='*60}")
            print(f"VAPI RESPONSE")
            print(f"{'='*60}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body:")
            print(json.dumps(response.json(), indent=2))
            print(f"{'='*60}\n")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Return exact Vapi error if available
            try:
                error_data = response.json()
                
                # Additional debug for errors
                print(f"\n{'='*60}")
                print(f"VAPI ERROR DETAILS")
                print(f"{'='*60}")
                print(f"Status Code: {response.status_code}")
                print(f"Error Data:")
                print(json.dumps(error_data, indent=2))
                print(f"{'='*60}\n")
                
                if "message" in error_data: 
                    # Vapi often returns "message": ["Error 1", "Error 2"]
                    if isinstance(error_data["message"], list):
                        return {"error": "; ".join(error_data["message"])}
                    return {"error": str(error_data["message"])}
                return {"error": str(error_data)}
            except:
                return {"error": f"API Error: {response.text}"}
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"EXCEPTION CAUGHT")
            print(f"{'='*60}")
            print(f"Error: {str(e)}")
            print(f"{'='*60}\n")
            return {"error": str(e)}

    def get_calls(self, limit=10):
        """Fetch call history."""
        if not self.api_key: return []
        try:
            response = requests.get(f"{self.base_url}/call", headers=self.headers, params={"limit": limit}, timeout=30)
            return response.json()
        except:
            return []

if __name__ == "__main__":
    # Test
    client = VapiClient()
    print("Vapi Client Initialized.")
