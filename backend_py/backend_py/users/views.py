from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer, UpdateProfileSerializer


class LoginThrottle(AnonRateThrottle):
    """Limite les tentatives de connexion pour prevenir le brute force"""
    rate = "5/min"


class RegisterThrottle(AnonRateThrottle):
    """Limite les inscriptions pour prevenir le spam"""
    rate = "3/min"


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue de login avec rate limiting"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]


class RegisterView(generics.CreateAPIView):
    """Vue d'inscription avec validation et rate limiting"""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "Compte cree",
            "user": {
                "id": user.id,
                "username": user.username
            }
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    """Recupere et met à jour les infos de l'utilisateur connecte"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Retourne le serializer approprié selon la méthode HTTP"""
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Met à jour le profil utilisateur"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Retourner les infos utilisateur mises à jour
        return Response({
            "message": "Profil mis à jour",
            "user": UserSerializer(instance).data
        })
