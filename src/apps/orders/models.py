import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product
from apps.shared.models.base import AbstractBaseModel


class OrderStatus(models.TextChoices):
    UNPAID = "UNPAID", _("To'lov qilinmagan")
    PAID = "PAID", _("To'lov qilindi")
    COLLECTING = "COLLECTING", _("Yig'ilyapti")
    SHIPPING = "SHIPPING", _("Yo'lda")
    DELIVERED = "DELIVERED", _("Yetkazildi")


class Cart(AbstractBaseModel):
    session_key = models.CharField(max_length=255, unique=True, verbose_name=_("Sessiya"))

    class Meta:
        verbose_name = _("Savat")
        verbose_name_plural = _("Savatlar")
        db_table = "carts"

    def __str__(self):
        return f"Savat #{self.pk}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_cargo(self):
        return sum(item.cargo_subtotal for item in self.items.all())

    @property
    def grand_total(self):
        return self.total_price + self.total_cargo

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(AbstractBaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name=_("Savat"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Mahsulot"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Soni"))

    class Meta:
        verbose_name = _("Savat elementi")
        verbose_name_plural = _("Savat elementlari")
        db_table = "cart_items"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.product.current_price * self.quantity

    @property
    def cargo_subtotal(self):
        return self.product.cargo_charge * self.quantity


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


class Order(AbstractBaseModel):
    order_number = models.CharField(
        max_length=20, unique=True, default=generate_order_number, verbose_name=_("Buyurtma raqami")
    )
    phone_number = models.CharField(max_length=20, verbose_name=_("Telefon raqami"))
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name=_("Telegram username"))
    telegram_chat_id = models.CharField(max_length=50, blank=True, verbose_name=_("Telegram Chat ID"))
    location = models.TextField(verbose_name=_("Manzil"))
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.UNPAID,
        verbose_name=_("Holati"),
        db_index=True,
    )
    total_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name=_("Mahsulotlar narxi"))
    cargo_total = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name=_("Yetkazish narxi"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name=_("Jami summa"))
    note = models.TextField(blank=True, verbose_name=_("Izoh"))

    class Meta:
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")
        ordering = ["-created_at"]
        db_table = "orders"

    def __str__(self):
        return f"{self.order_number} - {self.get_status_display()}"


class OrderItem(AbstractBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Buyurtma"))
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, verbose_name=_("Mahsulot")
    )
    product_name = models.CharField(max_length=500, verbose_name=_("Mahsulot nomi"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Soni"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("Birlik narxi"))
    cargo_charge = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("Yetkazish narxi"))

    class Meta:
        verbose_name = _("Buyurtma elementi")
        verbose_name_plural = _("Buyurtma elementlari")
        db_table = "order_items"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity

    @property
    def total_with_cargo(self):
        subtotal = self.subtotal or 0
        cargo = self.cargo_charge or 0
        qty = self.quantity or 0
        return subtotal + (cargo * qty)


class OrderStatusHistory(AbstractBaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history", verbose_name=_("Buyurtma")
    )
    old_status = models.CharField(max_length=20, choices=OrderStatus.choices, verbose_name=_("Oldingi holat"))
    new_status = models.CharField(max_length=20, choices=OrderStatus.choices, verbose_name=_("Yangi holat"))
    changed_by = models.CharField(max_length=150, blank=True, verbose_name=_("Kim o'zgartirdi"))

    class Meta:
        verbose_name = _("Holat tarixi")
        verbose_name_plural = _("Holat tarixi")
        ordering = ["-created_at"]
        db_table = "order_status_history"

    def __str__(self):
        return f"{self.order.order_number}: {self.get_old_status_display()} → {self.get_new_status_display()}"
