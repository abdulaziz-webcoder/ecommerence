from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.products.models import Product


def _get_or_create_cart(request):
    """Get or create cart for the current session."""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1},
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Return JSON for AJAX, redirect for form submit
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.item_count,
            "message": f"{product.name} savatga qo'shildi",
        })
    return redirect("orders:cart")


@require_POST
def cart_update(request, item_id):
    """Update cart item quantity."""
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()
    return redirect("orders:cart")


@require_POST
def cart_remove(request, item_id):
    """Remove an item from the cart."""
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "cart_count": cart.item_count})
    return redirect("orders:cart")


def cart_view(request):
    """Display the cart."""
    cart = _get_or_create_cart(request)
    # Prefetch discounts to prevent N+1 queries when calculating subtotal
    items = cart.items.select_related("product").prefetch_related("product__discounts").all()
    return render(request, "cart/cart.html", {
        "cart": cart,
        "items": items,
    })


def checkout_view(request):
    """Checkout: show form and process order."""
    cart = _get_or_create_cart(request)
    items = cart.items.select_related("product").prefetch_related("product__discounts").all()

    if not items.exists():
        return redirect("orders:cart")

    if request.method == "POST":
        phone_number = request.POST.get("phone_number", "").strip()
        location = request.POST.get("location", "").strip()
        telegram_username = request.POST.get("telegram_username", "").strip()
        note = request.POST.get("note", "").strip()

        if not phone_number or not location:
            return render(request, "cart/checkout.html", {
                "cart": cart,
                "items": items,
                "error": "Telefon raqami va manzil majburiy!",
                "phone_number": phone_number,
                "location": location,
                "telegram_username": telegram_username,
            })

        # Create order items in bulk
        total_amount = 0
        cargo_total = 0
        order_items = []

        order = Order.objects.create(
            phone_number=phone_number,
            telegram_username=telegram_username,
            location=location,
            note=note,
        )

        from django.db.models import F

        for item in items:
            price = item.product.current_price
            cargo = item.product.cargo_charge
            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=price,
                    cargo_charge=cargo,
                )
            )
            total_amount += price * item.quantity
            cargo_total += cargo * item.quantity

            # Increment product order count atomically
            Product.objects.filter(pk=item.product.pk).update(
                order_count=F("order_count") + item.quantity
            )

        # Execute single INSERT for all items
        OrderItem.objects.bulk_create(order_items)

        order.total_amount = total_amount
        order.cargo_total = cargo_total
        order.grand_total = total_amount + cargo_total
        order.save()

        # Clear cart
        cart.items.all().delete()

        # Notify admin and customer via Telegram
        try:
            from apps.telegram_bot.tasks import notify_new_order, notify_customer_order
            notify_new_order.delay(order.pk)
            notify_customer_order.delay(order.pk)
        except Exception:
            pass

        return redirect("orders:order_success", order_number=order.order_number)

    return render(request, "cart/checkout.html", {
        "cart": cart,
        "items": items,
    })


def order_success_view(request, order_number):
    """Order success page."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "cart/success.html", {"order": order})
