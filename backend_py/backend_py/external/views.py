import re
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.throttling import AnonRateThrottle


class ExternalAPIThrottle(AnonRateThrottle):
    """Limite les appels aux API externes"""
    rate = '30/min'


VALID_CURRENCIES = {
    'EUR', 'USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
    'CNY', 'HKD', 'SGD', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK',
    'HUF', 'RON', 'BGN', 'TRY', 'ILS', 'ZAR', 'MXN', 'BRL',
    'INR', 'KRW', 'THB', 'MYR', 'IDR', 'PHP', 'RUB'
}


class ExternalProducts(APIView):
    """Recupere des produits depuis une API externe"""
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ExternalAPIThrottle]

    def get(self, request):
        try:
            r = requests.get(
                'https://fakestoreapi.com/products?limit=10',
                timeout=10
            )
            r.raise_for_status()
            return Response(r.json())
        except requests.RequestException:
            return Response(
                {"error": "Service indisponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class Rates(APIView):
    """Recupere les taux de change"""
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ExternalAPIThrottle]

    def get(self, request):
        base = request.query_params.get('base', 'EUR').upper().strip()
        
        if base not in VALID_CURRENCIES:
            return Response(
                {"error": "Devise invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not re.match(r'^[A-Z]{3}$', base):
            return Response(
                {"error": "Format invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            url = f'https://api.exchangerate.host/latest?base={base}'
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return Response(r.json())
        except requests.RequestException:
            return Response(
                {"error": "Service indisponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class Health(APIView):
    """Endpoint de sante"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"ok": True})
