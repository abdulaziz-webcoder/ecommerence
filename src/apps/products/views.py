from django.db.models import Q, Min, Max
from django.views.generic import DetailView, ListView

from apps.products.models import Category, Color, Product


class ProductListView(ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related(
            "media_files", "discounts", "colors"
        )
        slug = self.kwargs.get("slug")
        if slug:
            qs = qs.filter(category__slug=slug)

        # Price filter
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            try:
                qs = qs.filter(price__gte=int(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(price__lte=int(max_price))
            except ValueError:
                pass

        # Color filter
        color_id = self.request.GET.get("color")
        if color_id:
            try:
                qs = qs.filter(colors__id=int(color_id))
            except ValueError:
                pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.filter(is_active=True)
        ctx["current_category"] = self.kwargs.get("slug", "")
        ctx["all_colors"] = Color.objects.all()
        # Price range for filter inputs
        price_data = Product.objects.filter(is_active=True).aggregate(
            min_price=Min("price"), max_price=Max("price")
        )
        ctx["price_min"] = price_data["min_price"] or 0
        ctx["price_max"] = price_data["max_price"] or 0
        ctx["filter_min"] = self.request.GET.get("min_price", "")
        ctx["filter_max"] = self.request.GET.get("max_price", "")
        ctx["filter_color"] = self.request.GET.get("color", "")
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related("media_files", "discounts", "colors")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        from django.db.models import F
        Product.objects.filter(pk=self.object.pk).update(view_count=F("view_count") + 1)
        return response


class ProductSearchView(ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related(
            "media_files", "discounts", "colors"
        )
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.filter(is_active=True)
        ctx["search_query"] = self.request.GET.get("q", "")
        ctx["all_colors"] = Color.objects.all()
        return ctx
