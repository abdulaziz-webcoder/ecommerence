from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from apps.orders.models import Cart, CartItem, Order, OrderItem, OrderStatus, OrderStatusHistory


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "color_name", "size_name", "quantity", "unit_price", "cargo_charge", "subtotal")
    fields = ("product_name", "color_name", "size_name", "quantity", "unit_price", "cargo_charge", "subtotal")

    def subtotal(self, obj):
        return f"{obj.subtotal:,.0f} so'm"
    subtotal.short_description = _("Jami")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderStatusHistoryInline(TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "created_at")
    fields = ("old_status", "new_status", "changed_by", "created_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("order_number", "phone_number", "status_badge", "grand_total_display", "created_at")
    list_filter = ("status",)
    search_fields = ("order_number", "phone_number", "telegram_username", "location")
    readonly_fields = ("order_number", "total_amount", "cargo_total", "grand_total", "created_at", "updated_at")
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    fieldsets = (
        (_("Buyurtma"), {"fields": ("order_number", "status", "note")}),
        (_("Mijoz"), {"fields": ("phone_number", "telegram_username", "telegram_chat_id", "location")}),
        (_("Narxlar"), {"fields": ("total_amount", "cargo_total", "grand_total")}),
        (_("Vaqt"), {"fields": ("created_at", "updated_at")}),
    )

    def status_badge(self, obj):
        colors = {
            OrderStatus.UNPAID: "#e53e3e",
            OrderStatus.PAID: "#3182ce",
            OrderStatus.COLLECTING: "#d69e2e",
            OrderStatus.SHIPPING: "#805ad5",
            OrderStatus.DELIVERED: "#38a169",
        }
        color = colors.get(obj.status, "#718096")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = _("Holati")

    def grand_total_display(self, obj):
        return f"{obj.grand_total:,.0f} so'm"
    grand_total_display.short_description = _("Jami summa")

    def save_model(self, request, obj, form, change):
        obj._changed_by = request.user.username
        super().save_model(request, obj, form, change)


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "color", "size", "quantity")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("id", "session_key", "item_count", "created_at")
    readonly_fields = ("session_key", "created_at", "updated_at")
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.item_count
    item_count.short_description = _("Mahsulotlar soni")