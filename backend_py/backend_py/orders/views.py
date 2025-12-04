from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderThrottle(UserRateThrottle):
    """Sécurité: Limiter les créations de commandes (anti-abus)"""
    rate = '10/hour'


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet sécurisé pour les commandes
    - Authentification requise
    - Rate limiting
    - Utilisateur ne voit que ses propres commandes
    - Validation complète des données
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [OrderThrottle]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """Sécurité: L'utilisateur ne voit que ses propres commandes"""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Sécurité: Création de commande avec validation complète"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = serializer.save()
            # Retourner la commande créée avec tous les détails
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Sécurité: Interdire la suppression des commandes"""
        return Response(
            {"error": "La suppression de commandes n'est pas autorisée."},
            status=status.HTTP_403_FORBIDDEN
        )

    def update(self, request, *args, **kwargs):
        """Sécurité: Interdire la modification des commandes"""
        return Response(
            {"error": "La modification de commandes n'est pas autorisée."},
            status=status.HTTP_403_FORBIDDEN
        )
