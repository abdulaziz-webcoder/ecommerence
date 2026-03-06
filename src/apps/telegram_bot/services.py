import logging

from apps.telegram_bot.client import send_message_sync

logger = logging.getLogger(__name__)


def _get_bot_settings():
    """Get the singleton bot settings instance."""
    from apps.telegram_bot.models import BotSettings
    try:
        settings = BotSettings.objects.first()
        if settings and settings.is_active and settings.api_id and settings.api_hash:
            return settings
    except Exception:
        pass
    return None


def send_telegram_message(phone_number, text, username=None):
    """Send a message via Telethon Userbot API."""
    return send_message_sync(phone_number, text, username)


def notify_order_status_changed(order_id, new_status):
    """Notify the customer about order status change."""
    from apps.orders.models import Order, OrderStatus
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return

    if not order.phone_number:
        return

    status_emoji = {
        OrderStatus.UNPAID: "🔴",
        OrderStatus.PAID: "✅",
        OrderStatus.COLLECTING: "📦",
        OrderStatus.SHIPPING: "🚚",
        OrderStatus.DELIVERED: "🎉",
    }
    emoji = status_emoji.get(new_status, "ℹ️")

    text = (
        f"{emoji} **Buyurtma yangilandi!**\n\n"
        f"📋 Buyurtma: **{order.order_number}**\n"
        f"📊 Holat: **{order.get_status_display()}**\n"
        f"💰 Summa: **{order.grand_total:,.0f} so'm**\n"
    )

    if new_status == OrderStatus.UNPAID:
        settings = _get_bot_settings()
        if settings and settings.payment_card_number:
            text += (
                f"\n💳 **To'lov ma'lumotlari:**\n"
                f"Karta: `{settings.payment_card_number}`\n"
                f"Egasi: {settings.payment_card_holder}\n\n"
                f"To'lovni amalga oshirgach, skrinshotni yuboring."
            )

    send_telegram_message(order.phone_number, text, username=order.telegram_username)


def notify_customer_new_order(order_id):
    """Notify the customer that their order was received."""
    from apps.orders.models import Order
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return

    if not order.phone_number:
        return

    items_text = ""
    for item in order.items.all():
        items_text += f"  • {item.product_name} x{item.quantity}\n"

    text = (
        f"🎉 **Buyurtmangiz qabul qilindi!**\n\n"
        f"Hurmatli mijoz, sizning **{order.order_number}** raqamli buyurtmangiz muvaffaqiyatli rasmiylashtirildi.\n\n"
        f"🛒 **Mahsulotlar:**\n{items_text}\n"
        f"💰 **Jami summa: {order.grand_total:,.0f} so'm**\n"
    )

    settings = _get_bot_settings()
    if order.status == "UNPAID" and settings and settings.payment_card_number:
        text += (
            f"\n💳 **To'lov ma'lumotlari:**\n"
            f"Karta: `{settings.payment_card_number}`\n"
            f"Egasi: {settings.payment_card_holder}\n\n"
            f"Iltimos, to'lovni amalga oshirgach, ushbu chatga skrinshotni yuboring. Tez orada operatorlarimiz siz bilan bog'lanadi."
        )

    send_telegram_message(order.phone_number, text, username=order.telegram_username)


def notify_admin_new_order(order_id):
    """Notify admin about a new order."""
    from apps.orders.models import Order
    settings = _get_bot_settings()
    if not settings or not settings.admin_phone:
        return

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return

    items_text = ""
    for item in order.items.all():
        items_text += f"  • {item.product_name} x{item.quantity} = {item.subtotal:,.0f} so'm\n"

    text = (
        f"🆕 **Yangi buyurtma!**\n\n"
        f"📋 Raqam: **{order.order_number}**\n"
        f"📱 Telefon: {order.phone_number}\n"
        f"👤 Telegram: @{order.telegram_username}\n"
        f"📍 Manzil: {order.location}\n\n"
        f"🛒 **Mahsulotlar:**\n{items_text}\n"
        f"📦 Yetkazish: {order.cargo_total:,.0f} so'm\n"
        f"💰 **Jami: {order.grand_total:,.0f} so'm**"
    )

    send_telegram_message(settings.admin_phone, text)


def notify_admin_payment_screenshot(screenshot_id):
    """Notify admin about a new payment screenshot."""
    from apps.telegram_bot.models import PaymentScreenshot
    settings = _get_bot_settings()
    if not settings or not settings.admin_phone:
        return

    try:
        ss = PaymentScreenshot.objects.select_related("order").get(pk=screenshot_id)
    except PaymentScreenshot.DoesNotExist:
        return

    text = (
        f"💳 **To'lov skrinshoti keldi!**\n\n"
        f"📋 Buyurtma: **{ss.order.order_number}**\n"
        f"💰 Summa: {ss.order.grand_total:,.0f} so'm\n"
        f"📱 Telefon: {ss.order.phone_number}\n\n"
        f"Admin paneldan tasdiqlang."
    )

    # Note: Sending the actual physical media with Telethon would require `client.send_message(..., file=ss.screenshot.path)`.
    # For now, sending the text to the admin phone number.
    send_telegram_message(settings.admin_phone, text)
