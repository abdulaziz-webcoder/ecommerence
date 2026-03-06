from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class SiteSettings(AbstractBaseModel):
    """Singleton model for global site configuration (shop name, logo, contact info)."""
    shop_name = models.CharField(max_length=150, default="🛒 Do'kon", verbose_name=_("Do'kon nomi"))
    shop_logo = models.ImageField(upload_to="settings/logo/", blank=True, null=True, verbose_name=_("Do'kon logotipi"))
    contact_phone = models.CharField(max_length=30, blank=True, verbose_name=_("Aloqa uchun telefon"))
    contact_telegram = models.CharField(max_length=100, blank=True, verbose_name=_("Telegram Username/Link"))

    # Hero Banner (Old Money Poster)
    hero_title = models.CharField(max_length=200, default="CURATED COLLECTIONS - OLD MONEY ELEGANCE", verbose_name=_("Hero Sarlavha (Katta matn)"))
    hero_subtitle = models.CharField(max_length=200, default="YANGI TO'PLAM - CHEGIRMA", verbose_name=_("Hero Qism-sarlavha (Kichik matn)"))
    hero_image = models.ImageField(upload_to="settings/hero/", blank=True, null=True, verbose_name=_("Hero Poster Rasmi"))
    hero_button_text = models.CharField(max_length=100, default="Batafsil ko'rish", verbose_name=_("Tugma matni"))
    hero_link = models.CharField(max_length=255, default="/", verbose_name=_("Tugma havolasi (URL)"))

    class Meta:
        verbose_name = _("Sayt sozlamalari")
        verbose_name_plural = _("Sayt sozlamalari")
        db_table = "site_settings"

    def __str__(self):
        return self.shop_name

    def save(self, *args, **kwargs):
        # Singleton logic: Ensure only one row exists
        if not self.pk and SiteSettings.objects.exists():
            existing = SiteSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "shop_name": "🛒 Do'kon",
            },
        )
        return obj
