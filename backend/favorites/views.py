from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FavoriteProduct, FavoriteVendor
from .serializers import FavoriteProductSerializer, FavoriteVendorSerializer


class FavoriteProductList(generics.ListCreateAPIView):
    serializer_class = FavoriteProductSerializer

    def get_queryset(self):
        return FavoriteProduct.objects.filter(user=self.request.user).select_related("product")

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"detail": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Check if already favorited
        if FavoriteProduct.objects.filter(user=request.user, product_id=product_id).exists():
            return Response(
                {"detail": "Product already in favorites"},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = FavoriteProduct.objects.create(user=request.user, product_id=product_id, created_at=timezone.now())
        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteProductDetail(APIView):
    def delete(self, request, pk):
        try:
            favorite = FavoriteProduct.objects.get(user=request.user, product_id=pk)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteProduct.DoesNotExist:
            return Response(
                {"detail": "Favorite not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class FavoriteVendorList(generics.ListCreateAPIView):
    serializer_class = FavoriteVendorSerializer

    def get_queryset(self):
        return FavoriteVendor.objects.filter(user=self.request.user).select_related("vendor")

    def create(self, request, *args, **kwargs):
        vendor_id = request.data.get("vendor_id")
        if not vendor_id:
            return Response(
                {"detail": "vendor_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Check if already favorited
        if FavoriteVendor.objects.filter(user=request.user, vendor_id=vendor_id).exists():
            return Response(
                {"detail": "Vendor already in favorites"},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = FavoriteVendor.objects.create(user=request.user, vendor_id=vendor_id, created_at=timezone.now())
        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteVendorDetail(APIView):
    def delete(self, request, pk):
        try:
            favorite = FavoriteVendor.objects.get(user=request.user, vendor_id=pk)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteVendor.DoesNotExist:
            return Response(
                {"detail": "Favorite not found"},
                status=status.HTTP_404_NOT_FOUND
            )