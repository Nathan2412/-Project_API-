from django.urls import path
from .views import ExternalProducts, Rates, Health, StoreLocator

urlpatterns = [
    path('products/', ExternalProducts.as_view(), name='external_products'),
    path('rates/', Rates.as_view(), name='external_rates'),
    path('health/', Health.as_view(), name='external_health'),
    path('stores/', StoreLocator.as_view(), name='store_locator'),
]
