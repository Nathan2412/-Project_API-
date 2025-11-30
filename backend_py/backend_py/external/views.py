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


class Rates(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        base = request.query_params.get('base', 'EUR')
        url = f'https://api.exchangerate.host/latest?base={base}'
        r = requests.get(url, timeout=10)
        return Response(r.json())


class Health(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"ok": True})
