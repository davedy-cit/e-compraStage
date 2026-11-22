from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.ProductList.as_view(), name="product-list"),
    path("products/<int:pk>/", views.ProductDetail.as_view(), name="product-detail"),
    path("categories/", views.CategoryList.as_view(), name="category-list"),
    path("vendors/", views.VendorList.as_view(), name="vendor-list"),
    path("units/", views.UnitOfMeasureList.as_view(), name="unit-list"),
    path("availability/", views.AvailabilityStatusList.as_view(), name="availability-list"),
]
