from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.FavoriteProductList.as_view(), name="favorite-product-list"),
    path("vendors/", views.FavoriteVendorList.as_view(), name="favorite-vendor-list"),
]
