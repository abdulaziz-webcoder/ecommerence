from django.urls import path
from apps.orders import views

app_name = "orders"

urlpatterns = [
    path("savat/", views.cart_view, name="cart"),
    path("savat/qoshish/<int:product_id>/", views.cart_add, name="cart_add"),
    path("savat/ochirish/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("savat/yangilash/<int:item_id>/", views.cart_update, name="cart_update"),
    path("buyurtma/", views.checkout_view, name="checkout"),
    path("buyurtma/muvaffaqiyat/<str:order_number>/", views.order_success_view, name="order_success"),
]
