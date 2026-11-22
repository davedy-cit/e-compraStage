from django.urls import path

from . import views

urlpatterns = [
    path("pos-vendors/", views.PosVendorList.as_view(), name="pos-vendor-list"),
    path("pos/", views.VendorPOSView.as_view(), name="vendor-pos"),
]
