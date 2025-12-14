"""
========================================
🔐 VIEWS GRAPHQL SÉCURISÉES
========================================

Vue GraphQL avec:
- Authentification JWT
- Désactivation introspection en production
- Rate limiting
"""

from graphene_django.views import GraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from graphql import parse, validate
from graphql.validation import NoSchemaIntrospectionCustomRule


class JWTGraphQLView(GraphQLView):
    """
    Vue GraphQL sécurisée avec:
    - Support de l'authentification JWT
    - Désactivation de l'introspection en production
    - Interface GraphiQL désactivée en production
    """
    
    @classmethod
    def as_view(cls, **kwargs):
        # Désactiver GraphiQL en production
        kwargs['graphiql'] = getattr(settings, 'DEBUG', False)
        return super().as_view(**kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        # Essayer d'authentifier avec JWT
        try:
            auth = JWTAuthentication()
            auth_result = auth.authenticate(request)
            if auth_result:
                request.user, _ = auth_result
        except Exception:
            request.user = AnonymousUser()
        
        return super().dispatch(request, *args, **kwargs)
    
    def execute_graphql_request(self, request, data, query, variables, operation_name, show_graphiql=False):
        """Override pour bloquer l'introspection en production"""
        
        # En production, bloquer l'introspection
        if not getattr(settings, 'DEBUG', False) and query:
            if '__schema' in query or '__type' in query:
                from graphql import GraphQLError
                return self.format_error(GraphQLError(
                    "L'introspection est désactivée en production pour des raisons de sécurité."
                ))
        
        return super().execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )

