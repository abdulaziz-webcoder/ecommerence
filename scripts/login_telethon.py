import os
import sys
import asyncio
from telethon import TelegramClient

# Add project root to python path to import django settings loosely
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# Set session path in project root
SESSION_FILE = "marketplace_bot.session"

async def main():
    print("="*50)
    print("Telethon Userbot Login Script")
    print("="*50)
    print("Before starting, ensure you have your API_ID and API_HASH from my.telegram.org")
    
    api_id = input("Enter your API_ID: ").strip()
    api_hash = input("Enter your API_HASH: ").strip()
    
    if not api_id or not api_hash:
        print("Error: API ID and Hash are required!")
        return
        
    try:
        api_id = int(api_id)
    except ValueError:
        print("Error: API ID must be an integer!")
        return

    print(f"\nCreating session file: {SESSION_FILE} ...")
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    
    await client.connect()
    if not await client.is_user_authorized():
        print("\nAccount not authorized. Starting interactive login...")
        phone = input("Enter your phone number (with country code, e.g. +998901234567): ").strip()
        
        try:
            await client.send_code_request(phone)
            code = input("Enter the login code you just received on Telegram: ").strip()
            
            try:
                await client.sign_in(phone, code)
            except Exception as e:
                if 'SessionPasswordNeededError' in str(type(e)):
                    password = input("Two-step verification enabled! Enter your password: ").strip()
                    await client.sign_in(password=password)
                else:
                    raise e
                    
            print("\n✅ Successfully logged in!")
            
        except Exception as e:
            print(f"\n❌ Login Failed: {e}")
            return
    else:
        print("\n✅ Already logged in using existing session file!")

    print("\nSession file looks good! Your Django app can now use it to send messages.")
    
    # Optional: Send a test message to Saved Messages
    try:
        await client.send_message("me", "**Do'kon Web Marketplace:** Telethon Userbot successfully linked! 🚀", parse_mode='md')
        print("A test message was sent to your 'Saved Messages' (Saqlangan Xabarlar) on Telegram.")
    except Exception as e:
        print(f"Failed to send test message: {e}")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
