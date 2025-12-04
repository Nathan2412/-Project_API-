from rest_framework import viewsets, permissions, filters
from .models import Product
from .serializers import ProductSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Sécurité: Seuls les admins peuvent modifier les produits.
    Tout le monde peut les consulter.
    """
    def has_permission(self, request, view):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture réservée aux admins
        return request.user and request.user.is_staff


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet sécurisé pour les produits:
    - GET: Accessible à tous
    - POST/PUT/DELETE: Réservé aux administrateurs
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["price", "created_at"]
