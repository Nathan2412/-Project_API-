from rest_framework import serializers
from .models import Review
from backend_py.products.models import Product


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer pour lire les avis"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "user_email", "product", "product_title", "rating", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]

    def validate_rating(self, value):
        """Valider que la note est entre 1 et 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value

    def validate(self, data):
        """Prevenir les doublons: un utilisateur ne peut noter qu'une fois par produit"""
        user = self.context['request'].user
        product = data.get('product')
        
        # Lors de la creation, verifier qu'il n'existe pas deja un avis
        if not self.instance:
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError(
                    "Vous avez déjà laissé un avis pour ce produit."
                )
        
        return data

    def create(self, validated_data):
        """Creer un avis avec l'utilisateur authentifie"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
