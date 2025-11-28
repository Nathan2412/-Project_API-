import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class CreatePaymentIntent(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None
        amount = int(float(request.data.get('amount', '0')) * 100)
        if amount <= 0:
            return Response({"error": "Invalid amount"}, status=400)
        intent = stripe.PaymentIntent.create(amount=amount, currency="usd")
        return Response({"client_secret": intent.client_secret})
