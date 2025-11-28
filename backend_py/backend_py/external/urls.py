from django.urls import path
from .views import ExternalProducts

urlpatterns = [
    path('products/', ExternalProducts.as_view(), name='external_products'),
]
