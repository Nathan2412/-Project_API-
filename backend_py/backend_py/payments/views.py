import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.throttling import UserRateThrottle
from backend_py.orders.models import Order


class PaymentThrottle(UserRateThrottle):
    """Limite les tentatives de paiement"""
    rate = '10/hour'


class CreatePaymentIntent(APIView):
    """Vue pour creer un PaymentIntent Stripe"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [PaymentThrottle]

    def post(self, request):
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response(
                {"error": "Paiement non configure"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response(
                {"error": "order_id requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Commande introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if order.status != 'pending':
            return Response(
                {"error": "Cette commande ne peut pas etre payee"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = int(float(order.total) * 100)
        
        if amount <= 0:
            return Response(
                {"error": "Montant invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="eur",
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id
                }
            )
            return Response({
                "client_secret": intent.client_secret,
                "order_id": order.id,
                "amount": float(order.total)
            })
        except stripe.error.StripeError:
            return Response(
                {"error": "Erreur de paiement"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
