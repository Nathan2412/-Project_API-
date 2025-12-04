from rest_framework import serializers
from .models import CartItem
from backend_py.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer sécurisé pour les items du panier.
    
    Sécurité:
    - Validation de la quantité (min 1, max 100)
    - Vérification que le produit existe
    - Vérification du stock disponible
    """
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    product_image = serializers.CharField(source='product.image', read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            "id", "product", "quantity",
            "product_title", "product_price", "product_image"
        ]
    
    def validate_quantity(self, value):
        """Sécurité: Valider la quantité"""
        if value < 1:
            raise serializers.ValidationError("La quantité doit être au moins 1.")
        if value > 100:
            raise serializers.ValidationError("Maximum 100 unités par produit.")
        return value
    
    def validate_product(self, value):
        """Sécurité: Vérifier que le produit existe et est disponible"""
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Ce produit n'existe pas.")
        return value
    
    def validate(self, attrs):
        """Sécurité: Vérifier le stock disponible"""
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)
        
        if product and product.stock < quantity:
            raise serializers.ValidationError(
                f"Stock insuffisant pour {product.title}. Disponible: {product.stock}"
            )
        
        return attrs
