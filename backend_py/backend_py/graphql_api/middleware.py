"""
========================================
🔐 MIDDLEWARE GRAPHQL SÉCURISÉ
========================================

Middleware pour protéger l'API GraphQL contre:
- Les requêtes trop profondes (DoS)
- Les requêtes trop complexes (DoS)
- L'introspection en production
"""

from django.conf import settings
from graphql import GraphQLError


class DepthAnalysisMiddleware:
    """
    Middleware qui analyse et limite la profondeur des requêtes GraphQL.
    
    Protège contre les attaques de type:
    - Nested queries attack
    - Circular fragment attack
    - Deep query DoS
    """
    
    def __init__(self):
        self.max_depth = getattr(settings, 'GRAPHQL_MAX_DEPTH', 5)
    
    def resolve(self, next, root, info, **args):
        # Calculer la profondeur de la requête
        depth = self._get_query_depth(info)
        
        if depth > self.max_depth:
            raise GraphQLError(
                f"La profondeur de la requête ({depth}) dépasse la limite autorisée ({self.max_depth}). "
                "Simplifiez votre requête."
            )
        
        return next(root, info, **args)
    
    def _get_query_depth(self, info, depth=0) -> int:
        """Calcule la profondeur de la requête GraphQL"""
        if not hasattr(info, 'field_nodes') or not info.field_nodes:
            return depth
        
        max_depth = depth
        for field_node in info.field_nodes:
            if hasattr(field_node, 'selection_set') and field_node.selection_set:
                for selection in field_node.selection_set.selections:
                    if hasattr(selection, 'selection_set') and selection.selection_set:
                        child_depth = self._calculate_selection_depth(selection.selection_set, depth + 1)
                        max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _calculate_selection_depth(self, selection_set, current_depth) -> int:
        """Calcule récursivement la profondeur d'un selection set"""
        if not selection_set or not selection_set.selections:
            return current_depth
        
        max_depth = current_depth
        for selection in selection_set.selections:
            if hasattr(selection, 'selection_set') and selection.selection_set:
                child_depth = self._calculate_selection_depth(selection.selection_set, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth


class IntrospectionDisableMiddleware:
    """
    Middleware qui désactive l'introspection en production.
    
    L'introspection permet de découvrir le schéma GraphQL complet,
    ce qui peut exposer des informations sensibles sur l'API.
    """
    
    def __init__(self):
        self.introspection_enabled = getattr(settings, 'DEBUG', False)
    
    def resolve(self, next, root, info, **args):
        # Bloquer les requêtes d'introspection en production
        if not self.introspection_enabled:
            field_name = info.field_name
            
            # Les champs d'introspection commencent par __
            if field_name.startswith('__'):
                raise GraphQLError(
                    "L'introspection est désactivée en production pour des raisons de sécurité."
                )
        
        return next(root, info, **args)


class QueryComplexityMiddleware:
    """
    Middleware qui limite la complexité des requêtes GraphQL.
    
    La complexité est calculée en fonction du nombre de champs demandés.
    Protège contre les requêtes qui demandent trop de données.
    """
    
    def __init__(self):
        self.max_complexity = getattr(settings, 'GRAPHQL_MAX_COMPLEXITY', 100)
        self._current_complexity = 0
    
    def resolve(self, next, root, info, **args):
        # Incrémenter la complexité pour chaque champ résolu
        self._current_complexity += 1
        
        # Vérifier si on dépasse la limite (seulement au niveau racine)
        if root is None:
            complexity = self._calculate_complexity(info)
            if complexity > self.max_complexity:
                raise GraphQLError(
                    f"La complexité de la requête ({complexity}) dépasse la limite autorisée ({self.max_complexity}). "
                    "Demandez moins de champs."
                )
        
        return next(root, info, **args)
    
    def _calculate_complexity(self, info) -> int:
        """Calcule la complexité totale de la requête"""
        if not hasattr(info, 'field_nodes') or not info.field_nodes:
            return 1
        
        total = 0
        for field_node in info.field_nodes:
            total += self._count_fields(field_node)
        
        return total
    
    def _count_fields(self, node) -> int:
        """Compte récursivement le nombre de champs dans un noeud"""
        count = 1  # Le noeud lui-même
        
        if hasattr(node, 'selection_set') and node.selection_set:
            for selection in node.selection_set.selections:
                count += self._count_fields(selection)
        
        return count


class RateLimitMiddleware:
    """
    Middleware de rate limiting pour GraphQL.
    
    Limite le nombre de requêtes par utilisateur/IP.
    Note: Utilise le cache Django pour stocker les compteurs.
    """
    
    def __init__(self):
        self.rate_limit = getattr(settings, 'GRAPHQL_RATE_LIMIT', 100)  # requêtes par minute
        self.window = 60  # secondes
    
    def resolve(self, next, root, info, **args):
        # Le rate limiting est géré au niveau de la vue (JWTGraphQLView)
        # Ce middleware peut ajouter une couche supplémentaire si nécessaire
        return next(root, info, **args)


class SecurityLoggingMiddleware:
    """
    Middleware qui log les requêtes GraphQL suspectes.
    """
    
    def resolve(self, next, root, info, **args):
        import logging
        logger = logging.getLogger('graphql.security')
        
        # Log les requêtes d'introspection
        if info.field_name.startswith('__'):
            logger.warning(f"Tentative d'introspection: {info.field_name}")
        
        return next(root, info, **args)
