class SecurityHeadersMiddleware:
    """Middleware pour les headers de securite HTTP"""
    
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
