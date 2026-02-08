"""
Script to generate Telethon StringSession for deployment
"""
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon.sessions import StringSession
from telethon import TelegramClient
from bot.config import Config

async def generate():
    try:
        config = Config.from_env()
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    print("Generating StringSession using your API_ID and API_HASH from .env...")
    
    async with TelegramClient(StringSession(), config.API_ID, config.API_HASH) as client:
        print("\n" + "=" * 50)
        print("✅ SUCCESS! Here is your SESSION_STRING:")
        print("=" * 50)
        print(client.session.save())
        print("=" * 50)
        print("\nCopy the above string and add it to your Railway variables as SESSION_STRING")

if __name__ == '__main__':
    import asyncio
    
    # Fix Windows event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(generate())
