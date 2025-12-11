class SecurityHeadersMiddleware:
    """Middleware pour les headers de securite HTTP"""
    
    # Paths that require permissive CSP for external CDN resources (Swagger/ReDoc)
    EXEMPT_PATHS = ['/api/docs/', '/api/redoc/', '/api/schema/']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS - Force HTTPS pendant 1 an, inclut les sous-domaines
        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Apply permissive CSP for documentation endpoints, strict CSP for all others
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            # Permissive CSP for Swagger/ReDoc - allows cdn.jsdelivr.net
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
        else:
            # Strict CSP for API endpoints
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
        
        # Supprimer les headers qui exposent des informations serveur
        for header in ["Server", "X-Powered-By"]:
            if header in response:
                del response[header]
        
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response["Pragma"] = "no-cache"
        
        return response
