from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display

from apps.telegram_bot.models import BotSettings, PaymentScreenshot


@admin.register(BotSettings)
class BotSettingsAdmin(ModelAdmin):
    list_display = ("__str__", "is_active", "has_api", "has_card")
    fieldsets = (
        (_("Userbot sozlamalari"), {"fields": ("api_id", "api_hash", "admin_phone", "is_active")}),
        (_("To'lov ma'lumotlari"), {"fields": ("payment_card_number", "payment_card_holder")}),
    )

    def has_add_permission(self, request):
        # Only one instance allowed
        if BotSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_api(self, obj):
        return bool(obj.api_id and obj.api_hash)
    has_api.short_description = _("API mavjud")
    has_api.boolean = True

    def has_card(self, obj):
        return bool(obj.payment_card_number)
    has_card.short_description = _("Karta mavjud")
    has_card.boolean = True


@admin.register(PaymentScreenshot)
class PaymentScreenshotAdmin(ModelAdmin):
    list_display = ("order_link", "show_confirmation", "created_at")
    list_filter = ("is_confirmed",)
    readonly_fields = ("order", "screenshot_preview", "created_at")
    fieldsets = (
        (None, {"fields": ("order", "screenshot_preview", "screenshot")}),
        (_("Tasdiqlash"), {"fields": ("is_confirmed", "confirmed_by")}),
    )
    actions = ["confirm_payments"]

    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">{}</a>', obj.order.pk, obj.order.order_number)
    order_link.short_description = _("Buyurtma")

    @display(
        description=_("Holat"),
        label={
            True: "success",
            False: "warning",
        },
    )
    def show_confirmation(self, obj):
        return obj.is_confirmed, _("Tasdiqlangan") if obj.is_confirmed else _("Kutilmoqda")

    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html(
                '<img src="{}" style="max-width:400px;max-height:400px;border-radius:8px;" />',
                obj.screenshot.url,
            )
        return "-"
    screenshot_preview.short_description = _("Ko'rish")

    @admin.action(description=_("Tanlangan to'lovlarni tasdiqlash"))
    def confirm_payments(self, request, queryset):
        for ss in queryset.filter(is_confirmed=False):
            ss.is_confirmed = True
            ss.confirmed_by = request.user.get_full_name() or request.user.email
            ss.save()
            # Update order status to PAID
            order = ss.order
            if order.status == "UNPAID":
                order._changed_by = request.user.get_full_name() or request.user.email
                order.status = "PAID"
                order.save()

    def save_model(self, request, obj, form, change):
        if obj.is_confirmed and not obj.confirmed_by:
            obj.confirmed_by = request.user.get_full_name() or request.user.email
        super().save_model(request, obj, form, change)
        # If confirmed, update order status
        if obj.is_confirmed and obj.order.status == "UNPAID":
            obj.order._changed_by = request.user.get_full_name() or request.user.email
            obj.order.status = "PAID"
            obj.order.save()
