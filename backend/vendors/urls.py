from django.urls import path

from vendors.views import (
    AdminVendorCreateView,
    AdminVendorDeactivateView,
    AdminVendorDetailView,
    AdminVendorListView,
    PosVendorList,
    VendorPOSView,
)

urlpatterns = [
    # Vendor POS (existing)
    path("pos-vendors/", PosVendorList.as_view(), name="pos-vendor-list"),
    path("pos/", VendorPOSView.as_view(), name="vendor-pos"),

    # Market Admin endpoints (NEW)
    path("admin/", AdminVendorListView.as_view(), name="admin-vendor-list"),
    path("admin/create/", AdminVendorCreateView.as_view(), name="admin-vendor-create"),
    path("admin/<int:id>/", AdminVendorDetailView.as_view(), name="admin-vendor-detail"),
    path("admin/<int:id>/deactivate/", AdminVendorDeactivateView.as_view(), name="admin-vendor-deactivate"),
]
