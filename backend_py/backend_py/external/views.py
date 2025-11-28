import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class ExternalProducts(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Placeholder for external API integration
        r = requests.get('https://fakestoreapi.com/products?limit=10', timeout=10)
        return Response(r.json())
