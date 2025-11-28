from django.urls import path
from .views import CreatePaymentIntent

urlpatterns = [
    path('intent/', CreatePaymentIntent.as_view(), name='payment_intent'),
]
