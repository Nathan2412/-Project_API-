from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
import re


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les infos utilisateur (sans données sensibles)"""
    class Meta:
        model = User
        fields = ["id", "email", "username"]
        # Sécurité: Ne jamais exposer le mot de passe ou is_staff
        read_only_fields = ["id", "email", "username"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personnalisé pour le login avec email.
    SimpleJWT utilise USERNAME_FIELD du modèle User (email).
    """
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remplacer le champ username par email
        self.fields['email'] = self.fields.pop('username', serializers.CharField())
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajouter des infos personnalisées au token
        token['username'] = user.username
        token['email'] = user.email
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer d'inscription sécurisé.
    
    Sécurité:
    - Validation du format email
    - Validation du format username (alphanumérique + underscore)
    - Vérification unicité email et username
    - Mot de passe hashé automatiquement
    """
    password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=6,
        max_length=128,
        style={'input_type': 'password'},
        help_text="Minimum 6 caractères"
    )
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, min_length=3, max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        """Sécurité: Valider et normaliser l'email"""
        email = value.lower().strip()
        
        # Validation basique du format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise serializers.ValidationError("Format d'email invalide.")
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        
        return email

    def validate_username(self, value):
        """Sécurité: Valider le format du username"""
        username = value.strip()
        
        # Sécurité: Autoriser uniquement alphanumérique et underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError(
                "Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores."
            )
        
        # Sécurité: Empêcher les usernames réservés
        reserved = {'admin', 'administrator', 'root', 'system', 'api', 'null', 'undefined'}
        if username.lower() in reserved:
            raise serializers.ValidationError("Ce nom d'utilisateur est réservé.")
        
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        
        return username

    def validate_password(self, value):
        """Sécurité: Valider la force du mot de passe"""
        if len(value) < 6:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        
        # Vérifier qu'il y a au moins une lettre et un chiffre
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        return value

    def create(self, validated_data):
        """Créer l'utilisateur avec mot de passe hashé"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
