"""
========================================
📊 SCHÉMA GRAPHQL - API E-COMMERCE
========================================

Définition des types GraphQL pour l'API.
"""

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model

from backend_py.products.models import Product
from backend_py.orders.models import Order, OrderItem
from backend_py.cart.models import CartItem
from backend_py.reviews.models import Review

User = get_user_model()


# ========================================
# TYPES GRAPHQL
# ========================================

class UserType(DjangoObjectType):
    """Type GraphQL pour les utilisateurs"""
    class Meta:
        model = User
        # Ne pas exposer le mot de passe ! On liste explicitement les champs autorisés
        fields = ("id", "username", "email")


class ProductType(DjangoObjectType):
    """Type GraphQL pour les produits"""
    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "stock", "image", "created_at", "updated_at")
        filter_fields = {
            'title': ['exact', 'icontains'],
            'price': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'stock': ['exact', 'lt', 'gt'],
        }
        interfaces = (graphene.relay.Node,)


class ReviewType(DjangoObjectType):
    """Type GraphQL pour les avis"""
    class Meta:
        model = Review
        fields = ("id", "user", "product", "rating", "comment", "created_at")


class OrderItemType(DjangoObjectType):
    """Type GraphQL pour les items de commande"""
    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price")


class OrderType(DjangoObjectType):
    """Type GraphQL pour les commandes"""
    items = graphene.List(OrderItemType)
    
    class Meta:
        model = Order
        fields = ("id", "user", "total", "status", "created_at", "items")
    
    def resolve_items(self, info):
        return self.items.all()


class CartItemType(DjangoObjectType):
    """Type GraphQL pour les items du panier"""
    class Meta:
        model = CartItem
        fields = ("id", "user", "product", "quantity")


# ========================================
# QUERIES (Lecture)
# ========================================

class Query(graphene.ObjectType):
    """Requêtes GraphQL disponibles"""
    
    # Produits
    all_products = graphene.List(ProductType, search=graphene.String(), min_price=graphene.Float(), max_price=graphene.Float())
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    
    # Avis
    all_reviews = graphene.List(ReviewType, product_id=graphene.Int())
    review = graphene.Field(ReviewType, id=graphene.Int(required=True))
    
    # Utilisateur connecté
    me = graphene.Field(UserType)
    my_orders = graphene.List(OrderType)
    my_cart = graphene.List(CartItemType)
    
    # Résolveurs Produits
    def resolve_all_products(self, info, search=None, min_price=None, max_price=None):
        queryset = Product.objects.all()
        
        if search:
            queryset = queryset.filter(title__icontains=search)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None
    
    # Résolveurs Avis
    def resolve_all_reviews(self, info, product_id=None):
        queryset = Review.objects.all()
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    def resolve_review(self, info, id):
        try:
            return Review.objects.get(pk=id)
        except Review.DoesNotExist:
            return None
    
    # Résolveurs Utilisateur (authentification requise)
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentification requise")
        return user
    
    def resolve_my_orders(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentification requise")
        return Order.objects.filter(user=user).order_by('-created_at')
    
    def resolve_my_cart(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentification requise")
        return CartItem.objects.filter(user=user)


# ========================================
# MUTATIONS (Écriture)
# ========================================

class AddToCart(graphene.Mutation):
    """Ajouter un produit au panier"""
    
    class Arguments:
        product_id = graphene.Int(required=True)
        quantity = graphene.Int(default_value=1)
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, product_id, quantity=1):
        user = info.context.user
        if user.is_anonymous:
            return AddToCart(success=False, message="Authentification requise")
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return AddToCart(success=False, message="Produit introuvable")
        
        if quantity < 1:
            return AddToCart(success=False, message="Quantité invalide")
        
        if product.stock < quantity:
            return AddToCart(success=False, message="Stock insuffisant")
        
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return AddToCart(cart_item=cart_item, success=True, message="Produit ajouté au panier")


class RemoveFromCart(graphene.Mutation):
    """Retirer un produit du panier"""
    
    class Arguments:
        cart_item_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, cart_item_id):
        user = info.context.user
        if user.is_anonymous:
            return RemoveFromCart(success=False, message="Authentification requise")
        
        try:
            cart_item = CartItem.objects.get(pk=cart_item_id, user=user)
            cart_item.delete()
            return RemoveFromCart(success=True, message="Produit retiré du panier")
        except CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Item introuvable")


class CreateOrder(graphene.Mutation):
    """Créer une commande à partir du panier"""
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info):
        user = info.context.user
        if user.is_anonymous:
            return CreateOrder(success=False, message="Authentification requise")
        
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return CreateOrder(success=False, message="Panier vide")
        
        # Calculer le total et vérifier le stock
        total = 0
        for item in cart_items:
            if item.product.stock < item.quantity:
                return CreateOrder(
                    success=False, 
                    message=f"Stock insuffisant pour {item.product.title}"
                )
            total += item.product.price * item.quantity
        
        # Créer la commande
        order = Order.objects.create(user=user, total=total, status='pending')
        
        # Créer les items et décrémenter le stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity
            )
            item.product.stock -= item.quantity
            item.product.save()
        
        # Vider le panier
        cart_items.delete()
        
        return CreateOrder(order=order, success=True, message="Commande créée")


class AddReview(graphene.Mutation):
    """Ajouter un avis sur un produit"""
    
    class Arguments:
        product_id = graphene.Int(required=True)
        rating = graphene.Int(required=True)
        comment = graphene.String(required=True)
    
    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, product_id, rating, comment):
        user = info.context.user
        if user.is_anonymous:
            return AddReview(success=False, message="Authentification requise")
        
        if rating < 1 or rating > 5:
            return AddReview(success=False, message="La note doit être entre 1 et 5")
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return AddReview(success=False, message="Produit introuvable")
        
        # Vérifier si l'utilisateur a déjà laissé un avis
        if Review.objects.filter(user=user, product=product).exists():
            return AddReview(success=False, message="Vous avez déjà laissé un avis")
        
        review = Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            comment=comment
        )
        
        return AddReview(review=review, success=True, message="Avis ajouté")


class Mutation(graphene.ObjectType):
    """Mutations GraphQL disponibles"""
    add_to_cart = AddToCart.Field()
    remove_from_cart = RemoveFromCart.Field()
    create_order = CreateOrder.Field()
    add_review = AddReview.Field()


# ========================================
# SCHÉMA FINAL
# ========================================

schema = graphene.Schema(query=Query, mutation=Mutation)
