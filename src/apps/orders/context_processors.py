from django.db.models import Sum

from apps.orders.models import CartItem


def cart_context(request):
    """Add cart item count to all template contexts."""
    count = 0
    if request.session.session_key:
        # 1 query optimization using DB aggregation directly
        aggregated = CartItem.objects.filter(
            cart__session_key=request.session.session_key
        ).aggregate(total=Sum("quantity"))
        count = aggregated["total"] or 0

    return {"cart_count": count}
