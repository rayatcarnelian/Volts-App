from modules.vapi_sip_config import VapiSIPConfigurator
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("VAPI_API_KEY")
tw_sid = os.getenv("TWILIO_SID")
tw_token = os.getenv("TWILIO_AUTH_TOKEN")

print(f"Connecting to Vapi with Key: {api_key[:5]}...")
print(f"Linking Twilio SID: {tw_sid[:5]}...")

config = VapiSIPConfigurator(api_key)
res = config.create_twilio_credential(tw_sid, tw_token, name="My Twilio Direct")

print("\n--- RESULT ---")
print(res)
print("--------------")
