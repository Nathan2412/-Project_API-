import re
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.throttling import AnonRateThrottle


class ExternalAPIThrottle(AnonRateThrottle):
    """Sécurité: Limiter les appels aux API externes"""
    rate = '30/min'


# Liste blanche des devises valides (ISO 4217)
VALID_CURRENCIES = {
    'EUR', 'USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
    'CNY', 'HKD', 'SGD', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK',
    'HUF', 'RON', 'BGN', 'TRY', 'ILS', 'ZAR', 'MXN', 'BRL',
    'INR', 'KRW', 'THB', 'MYR', 'IDR', 'PHP', 'RUB'
}


class ExternalProducts(APIView):
    """
    Récupère des produits depuis une API externe.
    Sécurisé avec rate limiting.
    """
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
                {"error": "Service externe indisponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class Rates(APIView):
    """
    Récupère les taux de change.
    
    Sécurité:
    - Validation stricte du paramètre 'base' (whitelist)
    - Rate limiting
    - Timeout sur les requêtes externes
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ExternalAPIThrottle]

    def get(self, request):
        base = request.query_params.get('base', 'EUR').upper().strip()
        
        # Sécurité: Valider que la devise est dans la liste blanche
        if base not in VALID_CURRENCIES:
            return Response(
                {"error": f"Devise invalide. Devises acceptées: {', '.join(sorted(VALID_CURRENCIES))}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sécurité: Validation supplémentaire (format ISO 4217)
        if not re.match(r'^[A-Z]{3}$', base):
            return Response(
                {"error": "Format de devise invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            url = f'https://api.exchangerate.host/latest?base={base}'
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return Response(r.json())
        except requests.RequestException:
            return Response(
                {"error": "Service de taux de change indisponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class Health(APIView):
    """Endpoint de santé pour les health checks"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"ok": True, "status": "healthy"})
