"""
Tests for SecurityHeadersMiddleware CSP behavior
"""
from django.test import TestCase, Client


class SecurityHeadersMiddlewareTest(TestCase):
    """Test CSP headers are correctly applied based on path"""
    
    def setUp(self):
        self.client = Client()
    
    def test_swagger_ui_has_permissive_csp(self):
        """Swagger UI endpoint should have permissive CSP allowing cdn.jsdelivr.net"""
        response = self.client.get('/api/docs/')
        
        # Check that CSP header exists
        self.assertIn('Content-Security-Policy', response)
        
        csp = response['Content-Security-Policy']
        
        # Verify permissive CSP allows cdn.jsdelivr.net
        self.assertIn('https://cdn.jsdelivr.net', csp)
        self.assertIn("script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net", csp)
        self.assertIn("style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net", csp)
        self.assertIn("font-src 'self' https://cdn.jsdelivr.net", csp)
    
    def test_redoc_has_permissive_csp(self):
        """ReDoc endpoint should have permissive CSP allowing cdn.jsdelivr.net"""
        response = self.client.get('/api/redoc/')
        
        csp = response['Content-Security-Policy']
        
        # Verify permissive CSP allows cdn.jsdelivr.net
        self.assertIn('https://cdn.jsdelivr.net', csp)
        self.assertIn("script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net", csp)
    
    def test_schema_endpoint_has_permissive_csp(self):
        """Schema endpoint should have permissive CSP"""
        response = self.client.get('/api/schema/')
        
        csp = response['Content-Security-Policy']
        
        # Verify permissive CSP
        self.assertIn('https://cdn.jsdelivr.net', csp)
    
    def test_api_endpoints_have_strict_csp(self):
        """Regular API endpoints should have strict CSP"""
        response = self.client.get('/products/')
        
        csp = response['Content-Security-Policy']
        
        # Verify strict CSP does NOT allow cdn.jsdelivr.net
        self.assertNotIn('https://cdn.jsdelivr.net', csp)
        self.assertIn("script-src 'self'", csp)
        # Should not have unsafe-inline for scripts in strict mode
        self.assertNotIn("script-src 'self' 'unsafe-inline'", csp)
    
    def test_health_endpoint_has_strict_csp(self):
        """Health endpoint should have strict CSP"""
        response = self.client.get('/health/')
        
        csp = response['Content-Security-Policy']
        
        # Verify strict CSP
        self.assertNotIn('https://cdn.jsdelivr.net', csp)
        self.assertIn("script-src 'self'", csp)
    
    def test_all_endpoints_have_security_headers(self):
        """All endpoints should have common security headers"""
        endpoints = ['/api/docs/', '/products/', '/health/']
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                
                # Common security headers
                self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
                self.assertEqual(response['X-Frame-Options'], 'DENY')
                self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
                self.assertIn('Strict-Transport-Security', response)
                self.assertIn('Referrer-Policy', response)
                
                # Should not expose server info
                self.assertNotIn('Server', response)
                self.assertNotIn('X-Powered-By', response)
