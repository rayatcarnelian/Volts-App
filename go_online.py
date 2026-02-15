import os
import sys
import time
import subprocess
from pyngrok import ngrok, conf

def go_online():
    """
    Launches Streamlit Main App and opens an Ngrok Tunnel to it.
    """
    print("=============================================")
    print("       VOLTS | GOING ONLINE (LIVE LINK)      ")
    print("=============================================")

    # 1. Set Auth Token (User Provided)
    print("[INFO] Authenticating Ngrok...")
    ngrok.set_auth_token("38N8QL8vzXYowyprkqSM6jlamIZ_71EvvPEBSR68b5pMfqrfV")
    
    try:
        # 2. Open Tunnel to Port 8522 (Fixed Port)
        public_url = ngrok.connect(8522).public_url
        print(f"\n[SUCCESS] YOUR MAGIC LINK IS READY:\n")
        print(f" >>> {public_url} <<< \n")
        print("(Send this link to your friend. Keep this window OPEN!)")
        
        # Save to file for the agent to read
        with open("magic_link.txt", "w") as f:
            f.write(public_url)
        
    except Exception as e:
        print(f"\n[ERROR] Ngrok failed to connect: {e}")
        if "ERR_NGROK_4018" in str(e) or "authentication" in str(e).lower():
            print("\n[TIP] You need a Free Auth Token.")
            print("1. Go to dashboard.ngrok.com and sign up (it's free).")
            print("2. Copy your Authtoken.")
            print("3. Run: ngrok config add-authtoken <YOUR_TOKEN> in terminal.")
        return

    # 3. Launch Streamlit (Force Port 8522)
    print("\n[INFO] Launching VOLTS Application on Port 8522...")
    try:
        # Run streamlit on 8522 matches the tunnel
        process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "main.py", "--server.port", "8522"])
        
        # Keep script running to keep tunnel open
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            process.terminate()
            ngrok.kill()
            
    except Exception as e:
        print(f"[ERROR] Failed to run app: {e}")

if __name__ == "__main__":
    go_online()
