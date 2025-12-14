from django.contrib import admin
from django.urls import path, include
from backend_py.external.views import Health
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', Health.as_view(), name='health'),
    path('auth/', include('backend_py.users.urls')),
    path('products/', include('backend_py.products.urls')),
    path('cart/', include('backend_py.cart.urls')),
    path('orders/', include('backend_py.orders.urls')),
    path('payment/', include('backend_py.payments.urls')),
    path('external/', include('backend_py.external.urls')),
    path('reviews/', include('backend_py.reviews.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # GraphQL API
    path('graphql/', include('backend_py.graphql_api.urls')),
]
