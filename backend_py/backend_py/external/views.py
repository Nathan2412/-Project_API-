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
            # Utiliser l'API gratuite frankfurter.app (basée sur la BCE)
            url = f'https://api.frankfurter.app/latest?from={base}'
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            # Reformater pour correspondre au format attendu
            return Response({
                "base": data.get("base", base),
                "date": data.get("date"),
                "rates": data.get("rates", {})
            })
        except requests.RequestException:
            # Fallback avec des taux statiques si l'API est indisponible
            fallback_rates = {
                "EUR": {"USD": 1.08, "GBP": 0.86, "JPY": 162.5, "CHF": 0.94, "CAD": 1.47, "AUD": 1.65, "CNY": 7.82},
                "USD": {"EUR": 0.93, "GBP": 0.79, "JPY": 150.2, "CHF": 0.87, "CAD": 1.36, "AUD": 1.53, "CNY": 7.24},
                "GBP": {"EUR": 1.17, "USD": 1.26, "JPY": 189.8, "CHF": 1.10, "CAD": 1.72, "AUD": 1.93, "CNY": 9.15},
            }
            if base in fallback_rates:
                return Response({
                    "base": base,
                    "date": "2025-12-11",
                    "rates": fallback_rates[base],
                    "note": "Taux approximatifs (API externe indisponible)"
                })
            return Response(
                {"error": "Service indisponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class Health(APIView):
    """Endpoint de sante"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"ok": True})


class StoreLocator(APIView):
    """Localiser des points de retrait/magasins pres d'un lieu via OpenStreetMap"""
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ExternalAPIThrottle]

    def get(self, request):
        city = request.query_params.get('city', '').strip()
        lat = request.query_params.get('lat', '').strip()
        lon = request.query_params.get('lon', '').strip()
        
        # Valider les parametres
        if not city and not (lat and lon):
            return Response(
                {"error": "Fournir soit 'city', soit 'lat' et 'lon'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Utiliser l'API Nominatim d'OpenStreetMap
            if city:
                # Rechercher par ville
                search_url = f'https://nominatim.openstreetmap.org/search'
                params = {
                    'q': f'shop in {city}',
                    'format': 'json',
                    'limit': 10,
                    'addressdetails': 1
                }
            else:
                # Valider et convertir les coordonnees
                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                except ValueError:
                    return Response(
                        {"error": "Coordonnees invalides"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Rechercher par coordonnees
                search_url = f'https://nominatim.openstreetmap.org/search'
                params = {
                    'q': 'shop',
                    'format': 'json',
                    'limit': 10,
                    'addressdetails': 1,
                    'viewbox': f'{lon_float-0.1},{lat_float-0.1},{lon_float+0.1},{lat_float+0.1}',
                    'bounded': 1
                }
            
            headers = {
                'User-Agent': 'E-Commerce-API/1.0 (Educational Project)'
            }
            
            r = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=10
            )
            r.raise_for_status()
            data = r.json()
            
            # Formater les resultats
            stores = []
            for item in data:
                # Utiliser le type ou category pour le nom si disponible, sinon display_name
                name = item.get('namedetails', {}).get('name') or item.get('type', 'Magasin')
                stores.append({
                    'name': name,
                    'lat': item.get('lat'),
                    'lon': item.get('lon'),
                    'address': item.get('display_name'),
                    'type': item.get('type', 'shop')
                })
            
            return Response({
                'count': len(stores),
                'stores': stores
            })
            
        except requests.RequestException:
            return Response(
                {"error": "Service de geolocalisation indisponible"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
