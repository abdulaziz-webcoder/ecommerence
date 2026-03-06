from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.orders.models import Order, OrderStatusHistory


@receiver(pre_save, sender=Order)
def track_status_change(sender, instance, **kwargs):
    """Create status history entry and trigger notification when status changes."""
    if not instance.pk:
        return

    try:
        old_instance = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    if old_instance.status != instance.status:
        OrderStatusHistory.objects.create(
            order=instance,
            old_status=old_instance.status,
            new_status=instance.status,
            changed_by=getattr(instance, "_changed_by", "system"),
        )
        # Trigger async Telegram notification
        try:
            from apps.telegram_bot.tasks import notify_status_changed
            notify_status_changed.delay(instance.pk, instance.status)
        except Exception:
            pass  # Don't break order save if notification fails
