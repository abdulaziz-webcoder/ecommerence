from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class BotSettings(AbstractBaseModel):
    """Singleton model for Telethon Userbot configuration."""
    api_id = models.CharField(max_length=50, blank=True, verbose_name=_("API ID"))
    api_hash = models.CharField(max_length=100, blank=True, verbose_name=_("API Hash"))
    admin_phone = models.CharField(max_length=30, blank=True, verbose_name=_("Admin Telefon Raqami (masalan: +998901234567)"))
    payment_card_number = models.CharField(max_length=30, blank=True, verbose_name=_("To'lov karta raqami"))
    payment_card_holder = models.CharField(max_length=200, blank=True, verbose_name=_("Karta egasi"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))

    class Meta:
        verbose_name = _("Bot Sozlamalari")
        verbose_name_plural = _("Bot Sozlamalari")
        db_table = "bot_settings"

    def __str__(self):
        return "Telegram Bot Sozlamalari"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton)
        if not self.pk and BotSettings.objects.exists():
            existing = BotSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "api_id": "",
                "api_hash": "",
                "admin_phone": "",
            },
        )
        return obj


class PaymentScreenshot(AbstractBaseModel):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment_screenshots",
        verbose_name=_("Buyurtma"),
    )
    screenshot = models.ImageField(upload_to="payment_screenshots/%Y/%m/", verbose_name=_("Skrinshot"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Tasdiqlangan"))
    confirmed_by = models.CharField(max_length=150, blank=True, verbose_name=_("Kim tasdiqladi"))

    class Meta:
        verbose_name = _("To'lov skrinshoti")
        verbose_name_plural = _("To'lov skrinshotlari")
        ordering = ["-created_at"]
        db_table = "payment_screenshots"

    def __str__(self):
        status = "✅" if self.is_confirmed else "⏳"
        return f"{status} {self.order.order_number}"
