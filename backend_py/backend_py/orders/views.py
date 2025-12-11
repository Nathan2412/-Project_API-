from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer


class OrderThrottle(UserRateThrottle):
    """Limite les creations de commandes"""
    rate = '10/hour'


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commandes"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [OrderThrottle]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            # Les admins peuvent voir toutes les commandes
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = serializer.save()
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        except Exception:
            return Response(
                {"error": "Erreur lors de la creation"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"error": "Operation non autorisee"},
            status=status.HTTP_403_FORBIDDEN
        )

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Operation non autorisee"},
                status=status.HTTP_403_FORBIDDEN
            )
        # Permettre aux admins de mettre a jour le statut de la commande
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Operation non autorisee"},
                status=status.HTTP_403_FORBIDDEN
            )
        # Permettre aux admins de mettre a jour partiellement le statut
        return super().partial_update(request, *args, **kwargs)
