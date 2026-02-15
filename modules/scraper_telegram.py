import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import streamlit as st
import pandas as pd

import nest_asyncio
nest_asyncio.apply()

class TelegramHunter:
    def __init__(self):
        # Matching .env.template keys now
        self.api_id = os.getenv("TG_API_ID")
        self.api_hash = os.getenv("TG_API_HASH")
        self.phone = os.getenv("TG_PHONE")
        self.client = None

    async def connect(self):
        if not self.api_id or not self.api_hash:
            st.error("Telegram Credentials (TG_API_ID) missing in .env")
            return False
            
        self.client = TelegramClient('anon', int(self.api_id), self.api_hash)
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            st.error("Telegram Error: Session not authorized. Please run `python auth_telegram.py` in your terminal first to login.")
            return False
        return True

    async def scrape_members(self, group_link, limit=100):
        if not self.client:
            success = await self.connect()
            if not success: return []

        leads = []
        try:
            from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusLastWeek
            
            # Join/Get Entity
            entity = await self.client.get_entity(group_link)
            
            # Get Participants
            # aggressively fetch more to filter down to active ones
            participants = await self.client.get_participants(entity, limit=limit*3)
            
            st.toast(f"Filtering {len(participants)} raw members for activity...", icon="🔍")
            
            for user in participants:
                if user.bot: continue
                
                # QUALITY FILTER: Check Status
                status = "Inactive"
                if isinstance(user.status, UserStatusOnline):
                    status = "Online"
                elif isinstance(user.status, UserStatusRecently):
                    status = "Recent"
                elif isinstance(user.status, UserStatusLastWeek):
                    status = "This Week"
                
                # Only keep active users if we want high quality
                if status == "Inactive":
                    continue
                    
                leads.append({
                    "Username": user.username if user.username else "N/A",
                    "First Name": user.first_name,
                    "Phone": user.phone if user.phone else "Hidden",
                    "Source": "Telegram",
                    "Group": group_link,
                    "Status": status,
                    "Premium": "Yes" if user.premium else "No"
                })
                
                if len(leads) >= limit:
                    break
                
            st.success(f"Scraped {len(leads)} ACTIVE members from {group_link}")
            return leads
            
        except Exception as e:
            # Check for common permission error (Channels vs Groups)
            error_str = str(e)
            if "ChatAdminRequired" in error_str or "admin privileges" in error_str:
                st.warning("⚠️ ACCESS DENIED: You are likely trying to scrape a CHANNEL or a PROTECTED GROUP.")
                st.info("💡 TIP: Telegram 'Channels' (Broadcasts) do not allow member scraping unless you are an Admin. 'Groups' with 'Hide Members' on also block this.")
                st.success("👉 SOLUTION: Try a normal DISCUSSION GROUP instead.")
                return []
            
            st.error(f"Telegram Scraping Failed: {e}")
            return []
        
        finally:
            if self.client:
                await self.client.disconnect()
