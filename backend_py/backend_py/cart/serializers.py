from rest_framework import serializers
from .models import CartItem
from backend_py.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items du panier"""
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
        if value < 1:
            raise serializers.ValidationError("Quantite minimum 1")
        if value > 100:
            raise serializers.ValidationError("Maximum 100 unites")
        return value
    
    def validate_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Produit inexistant")
        return value
    
    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)
        
        if product and product.stock < quantity:
            raise serializers.ValidationError("Stock insuffisant")
        
        return attrs
