from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.FavoriteProductList.as_view(), name="favorite-product-list"),
    path("products/<int:pk>/", views.FavoriteProductDetail.as_view(), name="favorite-product-detail"),
    path("vendors/", views.FavoriteVendorList.as_view(), name="favorite-vendor-list"),
    path("vendors/<int:pk>/", views.FavoriteVendorDetail.as_view(), name="favorite-vendor-detail"),
]