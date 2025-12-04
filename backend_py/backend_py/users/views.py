from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer


class RegisterThrottle(AnonRateThrottle):
    """Sécurité: Limiter les tentatives d'inscription (anti-bot/spam)"""
    rate = '5/hour'


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue de login personnalisée pour utiliser l'email comme identifiant.
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    Vue d'inscription sécurisée.
    
    Sécurité:
    - Rate limiting (5 inscriptions/heure par IP)
    - Validation complète des données
    - Hashage automatique du mot de passe
    - Pas d'exposition de données sensibles
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Sécurité: Ne retourner que les infos non sensibles
        return Response({
            "message": "Compte créé avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveAPIView):
    """
    Vue pour récupérer les infos de l'utilisateur connecté.
    Sécurisée par JWT - l'utilisateur ne peut voir que ses propres infos.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
