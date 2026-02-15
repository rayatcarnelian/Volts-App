"""
Automated setup script for Replicate API token.
Enables CapCut-quality, watermark-free videos.
"""

import os
import webbrowser
from pathlib import Path

def setup_replicate():
    print("=" * 60)
    print("REPLICATE API SETUP - Get CapCut-Quality Videos")
    print("=" * 60)
    
    # Step 1: Open browser
    print("\n[1/3] Opening Replicate signup page...")
    print("→ Sign up with Google (FREE, 30 seconds)")
    webbrowser.open("https://replicate.com/signin")
    input("\nPress ENTER after you've signed up...")
    
    # Step 2: Open token page
    print("\n[2/3] Opening API token page...")
    print("→ Click 'Create token' and copy it")
    webbrowser.open("https://replicate.com/account/api-tokens")
    
    token = input("\n📋 Paste your token here: ").strip()
    
    if not token.startswith("r8_"):
        print("\n❌ Error: Token should start with 'r8_'")
        print("Try again!")
        return
    
    # Step 3: Save to .env
    print("\n[3/3] Saving token...")
    env_path = Path(".env")
    
    # Read existing .env
    if env_path.exists():
        with open(env_path, "r") as f:
            content = f.read()
    else:
        content = ""
    
    # Update or add token
    if "REPLICATE_API_TOKEN=" in content:
        import re
        content = re.sub(r"REPLICATE_API_TOKEN=.*", f"REPLICATE_API_TOKEN={token}", content)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"REPLICATE_API_TOKEN={token}\n"
    
    with open(env_path, "w") as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Setup complete.")
    print("=" * 60)
    print("\n📌 Next step:")
    print("   1. Restart your Streamlit app")
    print("   2. Generate a video in Video Studio")
    print("   3. You'll now get CapCut-quality, no watermarks!")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        setup_replicate()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please follow SETUP_REPLICATE.md manually.")
