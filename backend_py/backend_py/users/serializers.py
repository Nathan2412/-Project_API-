from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
import re


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les infos utilisateur"""
    class Meta:
        model = User
        fields = ["id", "email", "username"]
        read_only_fields = ["id", "email", "username"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer pour le login avec email"""
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = self.fields.pop('username', serializers.CharField())
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer d'inscription"""
    password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=6,
        max_length=128,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, min_length=3, max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        email = value.lower().strip()
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise serializers.ValidationError("Format invalide")
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email deja utilise")
        
        return email

    def validate_username(self, value):
        username = value.strip()
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError("Caracteres non autorises")
        
        reserved = {'admin', 'administrator', 'root', 'system', 'api', 'null', 'undefined'}
        if username.lower() in reserved:
            raise serializers.ValidationError("Nom reserve")
        
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("Nom deja pris")
        
        return username

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Minimum 6 caracteres")
        
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Doit contenir une lettre")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Doit contenir un chiffre")
        
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil utilisateur"""
    current_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'current_password', 'new_password']
        read_only_fields = ['id', 'email']
        extra_kwargs = {
            'username': {'required': False}
        }
    
    def validate_username(self, value):
        """Vérifie que le username est unique (sauf pour l'utilisateur actuel)"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris")
        if len(value) < 3:
            raise serializers.ValidationError("Minimum 3 caractères")
        return value
    
    def validate_new_password(self, value):
        """Valide le nouveau mot de passe"""
        if value and len(value) > 0:
            if len(value) < 6:
                raise serializers.ValidationError("Minimum 6 caractères")
            if not re.search(r'[a-zA-Z]', value):
                raise serializers.ValidationError("Doit contenir une lettre")
            if not re.search(r'[0-9]', value):
                raise serializers.ValidationError("Doit contenir un chiffre")
        return value
    
    def validate(self, attrs):
        """Vérifie que le mot de passe actuel est fourni si on veut changer le mot de passe"""
        new_password = attrs.get('new_password', '')
        current_password = attrs.get('current_password', '')
        
        if new_password and len(new_password) > 0:
            if not current_password:
                raise serializers.ValidationError({
                    'current_password': "Le mot de passe actuel est requis pour changer le mot de passe"
                })
            
            user = self.context['request'].user
            if not user.check_password(current_password):
                raise serializers.ValidationError({
                    'current_password': "Mot de passe actuel incorrect"
                })
        
        return attrs
    
    def update(self, instance, validated_data):
        """Met à jour le profil utilisateur"""
        # Retirer les champs de mot de passe des données validées
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        
        # Mettre à jour le username si fourni
        if 'username' in validated_data:
            instance.username = validated_data['username']
        
        # Mettre à jour le mot de passe si fourni
        if new_password and len(new_password) > 0:
            instance.set_password(new_password)
        
        instance.save()
        return instance
