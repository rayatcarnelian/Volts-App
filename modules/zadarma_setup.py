import requests
import hashlib
import hmac
import base64
import os
import json
import urllib.parse

class ZadarmaAPI:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.base_url = 'https://api.zadarma.com'

    def _get_auth_header(self, method, params, params_string=""):
        """Generates the Authorization header."""
        # Sort params specifically? Zadarma expects query string sorted?
        # Actually for GET, params need to be in url encoded string.
        
        md5_params = hashlib.md5(params_string.encode('utf-8')).hexdigest()
        string_to_sign = f"{method}{params}{md5_params}" # Corrected: No newline
        
        signature = base64.b64encode(
            hmac.new(
                self.secret.encode('utf-8'), 
                string_to_sign.encode('utf-8'), 
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        return f"{self.key}:{signature}"

    def call_api(self, method, endpoint, params={}):
        """Generic API call."""
        
        # Format params
        sorted_params = urllib.parse.urlencode(sorted(params.items()))
        
        api_url = f"{self.base_url}{endpoint}"
        if method == 'GET' and sorted_params:
            api_url += f"?{sorted_params}"
        
        # Auth
        auth = self._get_auth_header(endpoint, sorted_params)
        headers = {'Authorization': auth}
        
        try:
            if method == 'GET':
                response = requests.get(api_url, headers=headers)
            else:
                response = requests.post(api_url, headers=headers, data=params)
                
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_sip_ids(self):
        """Returns list of SIP IDs."""
        return self.call_api('GET', '/v1/sip/')

    def get_sip_status(self, sip_id):
        return self.call_api('GET', f'/v1/sip/{sip_id}/status/')

    def get_pbx_internal(self):
        return self.call_api('GET', '/v1/pbx/internal/')

# Interactive Section
if __name__ == "__main__":
    current_key = "aac23f83d617bf551a6b"
    current_secret = "075d595f6bf0383d4c0a"
    
    print(f"Connecting to Zadarma with Key: {current_key}...")
    z = ZadarmaAPI(current_key, current_secret)
    
    print("--- Fetching SIP IDs ---")
    res = z.get_sip_ids()
    print(json.dumps(res, indent=2))
    
    if res.get('status') == 'success':
        sips = res.get('sips', [])
        print(f"\nFound {len(sips)} SIP Lines.")
        
        for s in sips:
            print(f"ID: {s['id']} | Display: {s.get('display_name')}")
            # Note: API usually does NOT return the password for security.
            # We might check if we can reset it or if user needs to enter it.
            
    print("\n--- Fetching PBX Extensions ---")
    pbx = z.get_pbx_internal()
    print(json.dumps(pbx, indent=2))
