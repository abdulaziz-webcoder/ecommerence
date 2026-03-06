import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from telethon import TelegramClient, events
from apps.telegram_bot.models import BotSettings, PaymentScreenshot
from apps.orders.models import Order

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def process_payment_screenshot(event, order, admin_phone):
    """Save the photo as a PaymentScreenshot and notify the admin."""
    logger.info(f"Processing payment screenshot for order {order.order_number}")
    
    # Download the photo from Telegram into memory
    file_bytes = await event.download_media(file=bytes)
    
    # Run synchronous DB operations in a thread
    def save_to_db():
        # Create standard screenshot instance
        from django.core.files.base import ContentFile
        ss = PaymentScreenshot(order=order)
        filename = f"{order.order_number}_payment.jpg"
        ss.screenshot.save(filename, ContentFile(file_bytes), save=True)
        return ss
        
    ss = await asyncio.to_thread(save_to_db)
    
    # Acknowledge to customer
    await event.reply("✅ Skrinshot qabul qilindi! Adminlarimiz tez orada to'lovni tasdiqlashadi.")
    
    # Forward the actual photo to the Admin
    if admin_phone:
        caption = (
            f"💳 **Yangi to'lov skrinshoti!**\n\n"
            f"📋 Buyurtma: **{order.order_number}**\n"
            f"💰 Summa: {order.grand_total:,.0f} so'm\n"
            f"📱 Mijoz: {order.phone_number}\n\n"
            f"Admin paneldan tasdiqlang."
        )
        await event.client.send_file(admin_phone, file_bytes, caption=caption, parse_mode='md')


async def main():
    logger.info("Initializing Userbot Daemon...")
    
    # Fetch settings synchronously
    def get_settings():
        return BotSettings.objects.filter(is_active=True).first()
        
    bot_settings = await asyncio.to_thread(get_settings)
    
    if not bot_settings or not bot_settings.api_id or not bot_settings.api_hash:
        logger.error("API ID or API Hash is not configured in Admin Panel.")
        return

    session_path = str(Path(settings.BASE_DIR) / "marketplace_bot.session")
    
    if not os.path.exists(session_path):
        logger.error("Session file not found! Please run 'python scripts/login_telethon.py' first.")
        return

    client = TelegramClient(session_path, int(bot_settings.api_id), bot_settings.api_hash)
    
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        sender = await event.get_sender()
        if getattr(sender, 'bot', False) or event.is_group or event.is_channel:
            return  # Ignore bots and groups
            
        # Get user phone number (might be None if they hide it, but we mostly message them by phone first)
        phone = getattr(sender, 'phone', None)
        if phone and not phone.startswith('+'):
            phone = f"+{phone}"
            
        text = event.raw_text
        has_media = event.photo

        # Simple heuristic: If they send a photo, see if they have pending UNPAID orders
        if has_media and phone:
            def get_pending_order():
                # Find the most recent UNPAID order for this phone number
                return Order.objects.filter(phone_number__endswith=phone.replace('+', ''), status='UNPAID').order_by('-created_at').first()
                
            pending_order = await asyncio.to_thread(get_pending_order)
            
            if pending_order:
                await process_payment_screenshot(event, pending_order, bot_settings.admin_phone)
                return

        # Simple Text Reply Router
        if text.startswith('/start'):
            await event.reply("Assalomu alaykum! Do'konimizga xush kelibsiz. Men sizning buyurtmalaringiz holati haqida xabar berib boraman.")
            
        elif text.startswith('/help'):
            await event.reply("Agar savollaringiz bo'lsa, adminga yozing yoki qo'ng'iroq qiling.")
            
        # Basic exact matches
        elif text.lower() in ['salom', 'assalomu alaykum', 'hi']:
            await event.reply("Assalomu alaykum!")

        # Forwards any unhandled text messages from customers directly to the Admin
        elif bot_settings.admin_phone and str(sender.id) != bot_settings.admin_phone:
            user_label = phone if phone else sender.first_name
            forward_text = f"📩 **Yangi xabar** ({user_label}):\n\n{text}"
            await event.client.send_message(bot_settings.admin_phone, forward_text)

    logger.info("Connecting to Telegram...")
    await client.connect()
    
    if not await client.is_user_authorized():
        logger.error("Session is invalid or logged out! Please run login_telethon.py again.")
        return
        
    async def poll_redis_outbound():
        import json
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        logger.info("Started Redis polling queue for outbound messages...")
        while True:
            try:
                def pop_msg():
                    return redis_conn.rpop("telethon_outbound_queue")
                msg = await asyncio.to_thread(pop_msg)
                
                if msg:
                    # msg might be bytes from Redis, decode it
                    if isinstance(msg, bytes):
                        msg = msg.decode('utf-8')
                    
                    logger.info(f"Redis Queue Pop! Raw Data: {msg}")
                    data = json.loads(msg)
                    phone_number = data.get('phone')
                    username = data.get('username')
                    text = data.get('text')
                    
                    target_entity = None
                    
                    # Strategy 1: Resolve by Telegram Username (Reliable, bypasses phone privacy settings)
                    if username:
                        clean_username = username.strip().replace('@', '')
                        try:
                            logger.info(f"Dequeued outbound message. Attempting to resolve by username: @{clean_username}")
                            target_entity = await client.get_entity(clean_username)
                            logger.info(f"Successfully resolved @{clean_username} to User ID {target_entity.id}")
                        except Exception as e:
                            logger.warning(f"Failed to resolve username @{clean_username}: {e}. Falling back to phone number.")
                    
                    # Strategy 2: Resolve by Phone Number via Contact Import (Fails if user hides phone number)
                    if not target_entity and phone_number:
                        clean_phone = '+' + ''.join(filter(str.isdigit, phone_number))
                        logger.info(f"Attempting to resolve by phone number: {clean_phone}")
                        
                        from telethon.tl.functions.contacts import ImportContactsRequest
                        from telethon.tl.types import InputPhoneContact
                        
                        try:
                            contact = InputPhoneContact(client_id=0, phone=clean_phone, first_name="Marketplace", last_name="Mijoz")
                            await client(ImportContactsRequest([contact]))
                            target_entity = await client.get_entity(clean_phone)
                            logger.info(f"Successfully resolved phone {clean_phone} to User ID {target_entity.id}")
                        except Exception as e:
                            logger.warning(f"Could not resolve phone number {clean_phone}: {e}")
                            target_entity = clean_phone  # Final desperate fallback
                    
                    if target_entity:
                        logger.info(f"Sending message via Telethon...")
                        await client.send_message(target_entity, text, parse_mode='md')
                    else:
                        logger.error(f"Failed to send message: No valid targeting method available for User.")
                    
                    # Prevent spamming limits
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Redis poll error: {e}")
                await asyncio.sleep(5)

    # Spawn the Redis polling loop to run alongside Telethon events
    asyncio.create_task(poll_redis_outbound())

    logger.info("Userbot Daemon is running and listening for messages! (Press Ctrl+C to stop)")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Start the asyncio event loop
    asyncio.run(main())
