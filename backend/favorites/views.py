from rest_framework import generics
from .models import FavoriteProduct, FavoriteVendor
from .serializers import FavoriteProductSerializer, FavoriteVendorSerializer

class FavoriteProductList(generics.ListAPIView):
    serializer_class = FavoriteProductSerializer

    def get_queryset(self):
        return FavoriteProduct.objects.filter(user=self.request.user).select_related("product")

class FavoriteVendorList(generics.ListAPIView):
    serializer_class = FavoriteVendorSerializer

    def get_queryset(self):
        return FavoriteVendor.objects.filter(user=self.request.user).select_related("vendor")