from django.urls import path
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from django.contrib import admin
from apps.shared.models.settings import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        (_("Umumiy Sozlamalar"), {
            "fields": ("shop_name", "shop_logo", "contact_phone", "contact_telegram")
        }),
        (_("Hero Banner Sozlamalari (Bosh sahifa)"), {
            "fields": ("hero_title", "hero_subtitle", "hero_image", "hero_button_text", "hero_link")
        }),
    )

    # Only allow editing the single instance by disabling add and delete
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.redirect_to_single_instance), name='site-settings-singleton')
        ]
        return custom_urls + urls

    def redirect_to_single_instance(self, request):
        # Redirect to the change form of the singleton instance
        obj = SiteSettings.get_instance()
        return redirect(f'../sitesettings/{obj.pk}/change/')
