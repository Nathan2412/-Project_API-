from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('backend_py.users.urls')),
    path('products/', include('backend_py.products.urls')),
    path('cart/', include('backend_py.cart.urls')),
    path('orders/', include('backend_py.orders.urls')),
    path('payment/', include('backend_py.payments.urls')),
    path('external/', include('backend_py.external.urls')),
]
