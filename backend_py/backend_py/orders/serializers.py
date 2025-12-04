from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from backend_py.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_title", "quantity", "price"]
        read_only_fields = ["price"]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer pour créer des items de commande"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "total", "status", "created_at", "items"]
        read_only_fields = ["user", "status", "created_at"]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer sécurisé pour créer une commande
    - Validation des produits
    - Vérification du stock
    - Calcul sécurisé du total côté serveur
    """
    items = OrderItemCreateSerializer(many=True)
    
    def validate_items(self, value):
        """Sécurité: Valider que les items sont corrects"""
        if not value:
            raise serializers.ValidationError("La commande doit contenir au moins un produit.")
        
        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 produits par commande.")
        
        # Vérifier les doublons
        product_ids = [item['product_id'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Produits en double détectés.")
        
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Sécurité: Création atomique avec vérification du stock"""
        user = self.context['request'].user
        items_data = validated_data['items']
        
        total = 0
        order_items = []
        
        for item_data in items_data:
            # Récupérer le produit avec verrou pour éviter les race conditions
            try:
                product = Product.objects.select_for_update().get(id=item_data['product_id'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Produit {item_data['product_id']} introuvable.")
            
            quantity = item_data['quantity']
            
            # Sécurité: Vérifier le stock disponible
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Stock insuffisant pour {product.title}. Disponible: {product.stock}"
                )
            
            # Sécurité: Calculer le prix côté serveur (ne jamais faire confiance au client)
            item_price = product.price * quantity
            total += item_price
            
            # Diminuer le stock
            product.stock -= quantity
            product.save()
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': item_price
            })
        
        # Créer la commande
        order = Order.objects.create(user=user, total=total, status='pending')
        
        # Créer les items
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        return order
