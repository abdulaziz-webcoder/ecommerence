import json
import logging
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

def send_message_sync(phone_number, text, username=None):
    """
    Push message onto Redis queue to be consumed by the Userbot Daemon.
    This avoids concurrent Telethon connections and SQLite locks.
    """
    if not phone_number and not username:
        return False
        
    try:
        redis_conn = get_redis_connection("default")
        payload = json.dumps({
            "phone": phone_number, 
            "username": username,
            "text": text
        })
        redis_conn.lpush("telethon_outbound_queue", payload)
        logger.info(f"Queued message for {phone_number}/{username} to Redis")
        return True
    except Exception as e:
        logger.error(f"Failed to queue message to Redis: {e}")
        return False
