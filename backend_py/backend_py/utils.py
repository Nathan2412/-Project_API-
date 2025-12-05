from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Gestionnaire d'exceptions personnalise"""
    response = exception_handler(exc, context)
    
    if response is not None:
        if response.status_code == 500:
            response.data = {"error": "Erreur interne"}
        
        if response.status_code == 404:
            response.data = {"error": "Ressource non trouvee"}
        
        if response.status_code == 403:
            response.data = {"error": "Acces non autorise"}
        
        if response.status_code == 401:
            response.data = {"error": "Authentification requise"}
    
    else:
        response = Response(
            {"error": "Une erreur est survenue"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
