from django.utils.translation import gettext_lazy as _


def dashboard_callback(request, context):
    """Unfold admin dashboard with analytics charts and KPIs."""
    from apps.orders.models import Order, OrderStatus
    from apps.products.models import Product
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # KPIs
    total_orders = Order.objects.count()
    monthly_orders = Order.objects.filter(created_at__gte=month_start).count()
    monthly_revenue = (
        Order.objects.filter(created_at__gte=month_start, status__in=[OrderStatus.PAID, OrderStatus.COLLECTING, OrderStatus.SHIPPING, OrderStatus.DELIVERED])
        .aggregate(total=Sum("grand_total"))["total"]
        or 0
    )
    total_products = Product.objects.filter(is_active=True).count()

    # Top 10 most viewed products
    top_viewed = Product.objects.filter(is_active=True).order_by("-view_count")[:10]
    top_viewed_labels = [p.name[:20] for p in top_viewed]
    top_viewed_data = [p.view_count for p in top_viewed]

    # Top 10 most ordered products
    top_ordered = Product.objects.filter(is_active=True).order_by("-order_count")[:10]
    top_ordered_labels = [p.name[:20] for p in top_ordered]
    top_ordered_data = [p.order_count for p in top_ordered]

    # Orders by status
    status_counts = Order.objects.values("status").annotate(count=Count("id"))
    status_labels = []
    status_data = []
    status_colors = {
        OrderStatus.UNPAID: "#ef4444",
        OrderStatus.PAID: "#10b981",
        OrderStatus.COLLECTING: "#f59e0b",
        OrderStatus.SHIPPING: "#3b82f6",
        OrderStatus.DELIVERED: "#059669",
    }
    for s in status_counts:
        label = dict(OrderStatus.choices).get(s["status"], s["status"])
        status_labels.append(str(label))
        status_data.append(s["count"])

    # Orders per day (last 7 days)
    daily_labels = []
    daily_data = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = Order.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count()
        daily_labels.append(day.strftime("%d/%m"))
        daily_data.append(count)

    import json
    
    context.update(
        {
            "kpi": [
                {
                    "title": str(_("Jami buyurtmalar")),
                    "metric": str(total_orders),
                    "footer": str(_("Barcha vaqt")),
                },
                {
                    "title": str(_("Oylik buyurtmalar")),
                    "metric": str(monthly_orders),
                    "footer": now.strftime("%B %Y"),
                },
                {
                    "title": str(_("Oylik daromad")),
                    "metric": f"{monthly_revenue:,.0f} so'm",
                    "footer": now.strftime("%B %Y"),
                },
                {
                    "title": str(_("Faol mahsulotlar")),
                    "metric": str(total_products),
                    "footer": str(_("Hozirda")),
                },
            ],
            "charts": [
                {
                    "title": str(_("Eng ko'p ko'rilgan mahsulotlar")),
                    "type": "bar",
                    "data": json.dumps({
                        "labels": top_viewed_labels,
                        "datasets": [
                            {
                                "label": str(_("Ko'rishlar")),
                                "data": top_viewed_data,
                                "backgroundColor": "#4f46e5",
                            }
                        ],
                    }),
                },
                {
                    "title": str(_("Eng ko'p buyurtma qilingan")),
                    "type": "bar",
                    "data": json.dumps({
                        "labels": top_ordered_labels,
                        "datasets": [
                            {
                                "label": str(_("Buyurtmalar")),
                                "data": top_ordered_data,
                                "backgroundColor": "#10b981",
                            }
                        ],
                    }),
                },
                {
                    "title": str(_("Buyurtmalar holati")),
                    "type": "doughnut",
                    "data": json.dumps({
                        "labels": status_labels,
                        "datasets": [
                            {
                                "data": status_data,
                                "backgroundColor": list(status_colors.values())[: len(status_data)],
                            }
                        ],
                    }),
                },
                {
                    "title": str(_("Oxirgi 7 kun buyurtmalar")),
                    "type": "line",
                    "data": json.dumps({
                        "labels": daily_labels,
                        "datasets": [
                            {
                                "label": str(_("Buyurtmalar")),
                                "data": daily_data,
                                "borderColor": "#4f46e5",
                                "backgroundColor": "rgba(79, 70, 229, 0.2)",
                                "fill": True,
                            }
                        ],
                    }),
                },
            ],
        }
    )
    return context
