"""
========================================
🔗 URLS GRAPHQL - API E-COMMERCE
========================================

Configuration des routes GraphQL.
"""

from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from .schema import schema


urlpatterns = [
    # Endpoint GraphQL principal
    path('', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)), name='graphql'),
]
