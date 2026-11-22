from rest_framework import generics
from .models import PosVendor
from .serializers import PosVendorSerializer

class PosVendorList(generics.ListAPIView):
    queryset = PosVendor.objects.select_related("catalog_vendor")
    serializer_class = PosVendorSerializer