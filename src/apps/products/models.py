from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone

from apps.shared.models.base import AbstractBaseModel


class Category(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Nomi"))
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name=_("Slug"))
    icon = models.CharField(max_length=50, blank=True, default="category", verbose_name=_("Ikonka"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))
    ordering = models.IntegerField(default=0, verbose_name=_("Tartib"))

    class Meta:
        verbose_name = _("Kategoriya")
        verbose_name_plural = _("Kategoriyalar")
        ordering = ["ordering", "name"]
        db_table = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

class Color(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Rang nomi"))
    hex_code = models.CharField(max_length=7, default="#000000", verbose_name=_("HEX kod"),
                                help_text=_("Masalan: #FF5733"))

    class Meta:
        verbose_name = _("Rang")
        verbose_name_plural = _("Ranglar")
        db_table = "colors"
        ordering = ["name"]

    def __str__(self):
        return self.name



class Product(AbstractBaseModel):
    name = models.CharField(max_length=500, verbose_name=_("Nomi"))
    slug = models.SlugField(max_length=500, unique=True, blank=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Tavsif"))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Kategoriya"),
    )
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("Narxi (so'm)"))
    discount_price = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True, verbose_name=_("Chegirmali narx")
    )
    shipping_days = models.PositiveIntegerField(default=3, verbose_name=_("Yetkazish (kun)"))
    cargo_charge = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name=_("Yetkazish narxi (so'm)")
    )
    colors = models.ManyToManyField(
        Color, blank=True, related_name="products", verbose_name=_("Ranglar")
    )
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("Ko'rishlar soni"), editable=False)
    order_count = models.PositiveIntegerField(default=0, verbose_name=_("Buyurtmalar soni"), editable=False)
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))

    class Meta:
        verbose_name = _("Mahsulot")
        verbose_name_plural = _("Mahsulotlar")
        ordering = ["-created_at"]
        db_table = "products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if not self.slug:
                self.slug = f"product-{timezone.now().timestamp():.0f}"
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        """Return active discounted price or regular price."""
        now = timezone.now()
        # Evaluate in python to utilize prefetch_related cache and avoid N+1 queries
        active_discounts = [
            d for d in self.discounts.all()
            if d.is_active and d.start_date <= now <= d.end_date
        ]
        
        if active_discounts:
            active_discount = sorted(active_discounts, key=lambda x: x.discount_percent, reverse=True)[0]
            return int(self.price * (100 - active_discount.discount_percent) / 100)
            
        if self.discount_price is not None:
            return self.discount_price
        return self.price

    @property
    def has_discount(self):
        if self.discount_price is not None and self.discount_price < self.price:
            return True
            
        now = timezone.now()
        return any(
            d.is_active and d.start_date <= now <= d.end_date
            for d in self.discounts.all()
        )

    @property
    def main_image(self):
        media = self.media_files.filter(is_video=False).order_by("ordering").first()
        if media:
            return media.file
        return None


class ProductMedia(AbstractBaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="media_files", verbose_name=_("Mahsulot")
    )
    file = models.FileField(upload_to="products/media/%Y/%m/", verbose_name=_("Fayl"))
    is_video = models.BooleanField(default=False, verbose_name=_("Video"))
    ordering = models.IntegerField(default=0, verbose_name=_("Tartib"))

    class Meta:
        verbose_name = _("Mahsulot fayli")
        verbose_name_plural = _("Mahsulot fayllari")
        ordering = ["ordering"]
        db_table = "product_media"

    def __str__(self):
        kind = _("Video") if self.is_video else _("Rasm")
        return f"{self.product.name} - {kind}"


class Discount(AbstractBaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="discounts", verbose_name=_("Mahsulot")
    )
    discount_percent = models.PositiveIntegerField(verbose_name=_("Chegirma (%)"))
    start_date = models.DateTimeField(verbose_name=_("Boshlanish sanasi"))
    end_date = models.DateTimeField(verbose_name=_("Tugash sanasi"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))

    class Meta:
        verbose_name = _("Chegirma")
        verbose_name_plural = _("Chegirmalar")
        ordering = ["-created_at"]
        db_table = "discounts"

    def __str__(self):
        return f"{self.product.name} - {self.discount_percent}%"
