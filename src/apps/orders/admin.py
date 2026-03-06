from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display

from apps.orders.models import Cart, CartItem, Order, OrderItem, OrderStatus, OrderStatusHistory


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "unit_price", "cargo_charge", "item_total")
    fields = ("product_name", "quantity", "unit_price", "cargo_charge", "item_total")

    def item_total(self, obj):
        return f"{obj.total_with_cargo:,.0f} so'm"
    item_total.short_description = _("Jami")


class StatusHistoryInline(TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "created_at")
    fields = ("old_status", "new_status", "changed_by", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "order_number",
        "phone_number",
        "show_status",
        "grand_total_display",
        "created_at",
    )
    list_display_links = ("order_number",)
    list_filter = (
        "status",
        ("created_at", RangeDateFilter),
    )
    list_filter_submit = True
    search_fields = ("order_number", "phone_number", "telegram_username")
    readonly_fields = ("order_number", "total_amount", "cargo_total", "grand_total", "created_at", "updated_at")
    inlines = [OrderItemInline, StatusHistoryInline]
    fieldsets = (
        (_("Buyurtma ma'lumotlari"), {"fields": ("order_number", "status", "created_at", "updated_at")}),
        (_("Mijoz ma'lumotlari"), {"fields": ("phone_number", "telegram_username", "telegram_chat_id", "location")}),
        (_("Narxlar"), {"fields": ("total_amount", "cargo_total", "grand_total")}),
        (_("Izoh"), {"fields": ("note",)}),
    )

    @display(
        description=_("Holat"),
        ordering="status",
        label={
            OrderStatus.UNPAID: "danger",
            OrderStatus.PAID: "success",
            OrderStatus.COLLECTING: "warning",
            OrderStatus.SHIPPING: "info",
            OrderStatus.DELIVERED: "success",
        },
    )
    def show_status(self, obj):
        return obj.status, obj.get_status_display()

    def grand_total_display(self, obj):
        return f"{obj.grand_total:,.0f} so'm"
    grand_total_display.short_description = _("Jami summa")

    def save_model(self, request, obj, form, change):
        obj._changed_by = request.user.get_full_name() or request.user.email
        super().save_model(request, obj, form, change)


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity")


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("id", "session_key", "item_count_display", "total_display", "created_at")
    inlines = [CartItemInline]
    readonly_fields = ("session_key",)

    def item_count_display(self, obj):
        return obj.item_count
    item_count_display.short_description = _("Elementlar soni")

    def total_display(self, obj):
        return f"{obj.grand_total:,.0f} so'm"
    total_display.short_description = _("Jami")
