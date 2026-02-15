import os
import replicate
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("REPLICATE_API_TOKEN")
print(f"Token found: {token[:4]}...{token[-4:] if token else 'None'}")

if not token:
    print("No token found in .env")
    exit(1)

try:
    print("Attempting to connect to Replicate...")
    # Try a very cheap/simple model call
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "a tiny red cube"}
    )
    print("Success!")
    print(output)
except Exception as e:
    print(f"Error: {e}")
