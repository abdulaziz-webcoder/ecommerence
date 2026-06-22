from django.urls import path
from apps.products import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("category/<slug:slug>/", views.ProductListView.as_view(), name="product_list_by_category"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("search/", views.ProductSearchView.as_view(), name="product_search"),
    path("collections/", views.CollectionListView.as_view(), name="collection_list"),
    path("collections/<slug:slug>/", views.CollectionDetailView.as_view(), name="collection_detail"),
]
