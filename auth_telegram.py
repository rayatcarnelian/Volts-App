import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

# Load env vars
load_dotenv()

api_id = os.getenv("TG_API_ID")
api_hash = os.getenv("TG_API_HASH")

if not api_id or not api_hash:
    print("Error: TG_API_ID or TG_API_HASH not found in .env")
    exit(1)

print(f"Authenticating with ID: {api_id}")

client = TelegramClient('anon', int(api_id), api_hash)

async def main():
    await client.start()
    print("\n✅ PRE-AUTHENTICATION SUCCESSFUL!")
    print("The 'anon.session' file has been created.")
    print("You can now restart the VOLTS app and use the Telegram scraper.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
