from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display

from apps.products.models import Category, Color, Discount, Product, ProductMedia


class ColorPickerWidget(forms.TextInput):
    """Native browser color picker (no HEX typing needed)."""
    input_type = "color"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({"style": "width:80px; height:44px; padding:2px; cursor:pointer; border:1px solid #ddd; border-radius:8px;"})


class ColorAdminForm(forms.ModelForm):
    hex_code = forms.CharField(
        label=_("Rang"),
        widget=ColorPickerWidget(),
        initial="#000000",
        help_text=_("Rangni tanlaymiz."),
    )

    class Meta:
        model = Color
        fields = "__all__"


@admin.register(Color)
class ColorAdmin(ModelAdmin):
    form = ColorAdminForm
    list_display = ("name", "color_preview", "hex_code")
    search_fields = ("name",)

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:{};border:1px solid #ccc;vertical-align:middle;"></span>',
            obj.hex_code
        )
    color_preview.short_description = _("Ko'rinish")


class ProductMediaInline(TabularInline):
    model = ProductMedia
    extra = 1
    fields = ("file", "is_video", "ordering")


class DiscountInline(TabularInline):
    model = Discount
    extra = 0
    fields = ("discount_percent", "start_date", "end_date", "is_active")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "is_active", "ordering")
    list_editable = ("is_active", "ordering")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "product_image",
        "name",
        "category",
        "price",
        "show_discount_price",
        "shipping_days",
        "cargo_charge",
        "view_count",
        "order_count",
        "is_active",
    )
    list_display_links = ("product_image", "name")
    list_editable = ("is_active",)
    list_filter = (
        "category",
        "is_active",
        ("created_at", RangeDateFilter),
    )
    list_filter_submit = True
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductMediaInline, DiscountInline]
    fieldsets = (
        (_("Asosiy"), {"fields": ("name", "slug", "category", "is_active")}),
        (_("Narxlar"), {"fields": ("price", "discount_price", "cargo_charge")}),
        (_("Ranglar"), {"fields": ("colors",)}),
        (_("Tavsif"), {"fields": ("description",)}),
        (_("Yetkazish"), {"fields": ("shipping_days",)}),
    )
    readonly_fields = ("view_count", "order_count")

    def product_image(self, obj):
        img = obj.main_image
        if img:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;" />', img.url)
        return format_html('<div style="width:50px;height:50px;background:#eee;border-radius:8px;display:flex;align-items:center;justify-content:center;">📦</div>')
    product_image.short_description = _("Rasm")

    @display(description=_("Chegirmali narx"), ordering="discount_price")
    def show_discount_price(self, obj):
        current = obj.current_price
        if current < obj.price:
            return format_html(
                '<span style="text-decoration:line-through;color:#999;">{}</span> <b style="color:#e53e3e;">{}</b>',
                f"{obj.price:,.0f}",
                f"{current:,.0f}",
            )
        return f"{obj.price:,.0f}"


@admin.register(ProductMedia)
class ProductMediaAdmin(ModelAdmin):
    list_display = ("product", "is_video", "ordering")
    list_filter = ("is_video",)


@admin.register(Discount)
class DiscountAdmin(ModelAdmin):
    list_display = ("product", "discount_percent", "start_date", "end_date", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active", ("start_date", RangeDateFilter))
    list_filter_submit = True
