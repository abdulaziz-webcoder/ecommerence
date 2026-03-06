from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def notify_status_changed(self, order_id, new_status):
    """Celery task: notify customer about status change."""
    try:
        from apps.telegram_bot.services import notify_order_status_changed
        notify_order_status_changed(order_id, new_status)
    except Exception as exc:
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def notify_customer_order(self, order_id):
    """Celery task: notify customer about new order."""
    try:
        from apps.telegram_bot.services import notify_customer_new_order
        notify_customer_new_order(order_id)
    except Exception as exc:
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def notify_new_order(self, order_id):
    """Celery task: notify admin about new order."""
    try:
        from apps.telegram_bot.services import notify_admin_new_order
        notify_admin_new_order(order_id)
    except Exception as exc:
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def notify_payment_screenshot(self, screenshot_id):
    """Celery task: notify admin about payment screenshot."""
    try:
        from apps.telegram_bot.services import notify_admin_payment_screenshot
        notify_admin_payment_screenshot(screenshot_id)
    except Exception as exc:
        self.retry(exc=exc)
