from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet pour les avis produits avec rate limiting"""
    serializer_class = ReviewSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        """Filtrer les avis par product_id si fourni"""
        queryset = Review.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def get_permissions(self):
        """
        - Lecture (GET): Tous (authentifies ou non)
        - Creation (POST): Utilisateurs authentifies uniquement
        - Modification/Suppression: Proprietaire uniquement
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Creer un avis avec l'utilisateur authentifie"""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Seul le proprietaire peut modifier son avis"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"error": "Vous ne pouvez modifier que vos propres avis"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Seul le proprietaire peut modifier partiellement son avis"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"error": "Vous ne pouvez modifier que vos propres avis"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Seul le proprietaire peut supprimer son avis"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"error": "Vous ne pouvez supprimer que vos propres avis"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
