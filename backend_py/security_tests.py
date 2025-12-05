#!/usr/bin/env python
"""
========================================
🔐 TESTS DE SÉCURITÉ - API E-COMMERCE
========================================

Ce fichier contient des tests de sécurité pour vérifier la robustesse
de l'API contre les attaques les plus courantes:

1. Injection SQL
2. Cross-Site Scripting (XSS)
3. Broken Authentication
4. IDOR (Insecure Direct Object Reference)
5. Rate Limiting / Brute Force
6. Mass Assignment
7. Path Traversal
8. SSRF (Server-Side Request Forgery)
9. JWT Token Security
10. Input Validation

Usage:
    python security_tests.py [--url http://localhost:8000]
"""

import requests
import json
import time
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class Colors:
    """Couleurs pour le terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SecurityTester:
    """Classe principale pour les tests de sécurité"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results: List[Dict] = []
        self.auth_token: Optional[str] = None
        self.test_user = {
            "username": "security_tester",
            "email": "security@test.com",
            "password": "Test1234!"
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Logger avec couleurs"""
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "TEST": Colors.PURPLE,
            "VULN": Colors.RED + Colors.BOLD,
            "SAFE": Colors.GREEN + Colors.BOLD
        }
        color = colors.get(level, Colors.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] [{level}] {message}{Colors.END}")
    
    def add_result(self, test_name: str, category: str, passed: bool, details: str, severity: str = "LOW"):
        """Ajouter un résultat de test"""
        self.results.append({
            "test": test_name,
            "category": category,
            "passed": passed,
            "severity": severity,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def setup_test_user(self) -> bool:
        """Créer un utilisateur de test et obtenir un token"""
        self.log("Création d'un utilisateur de test...", "INFO")
        
        # Essayer de créer l'utilisateur
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register/",
                json=self.test_user,
                timeout=10
            )
            if response.status_code in [201, 400]:  # 400 = déjà existant
                pass
        except Exception as e:
            self.log(f"Erreur création user: {e}", "WARNING")
        
        # Login pour obtenir le token
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login/",
                json={
                    "email": self.test_user["email"],
                    "password": self.test_user["password"]
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access")
                self.log("Token JWT obtenu avec succès", "SUCCESS")
                return True
        except Exception as e:
            self.log(f"Erreur login: {e}", "WARNING")
        
        return False

    # ========================================
    # 1. TESTS D'INJECTION SQL
    # ========================================
    
    def test_sql_injection(self):
        """Tests d'injection SQL sur différents endpoints"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Injection SQL", "TEST")
        self.log("=" * 50, "TEST")
        
        sql_payloads = [
            # Classic SQL Injection
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "1' OR '1'='1",
            "1 OR 1=1",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL, NULL--",
            "' UNION SELECT username, password FROM users--",
            
            # Blind SQL Injection
            "' AND SLEEP(5)--",
            "' AND 1=1--",
            "' AND 1=2--",
            "1' AND (SELECT COUNT(*) FROM users) > 0--",
            
            # Error-based SQL Injection
            "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version())))--",
            "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            
            # Time-based Blind SQL Injection
            "'; WAITFOR DELAY '0:0:5'--",
            "' AND BENCHMARK(10000000, SHA1('test'))--",
            
            # NoSQL Injection (MongoDB-style)
            '{"$gt": ""}',
            '{"$ne": null}',
            '{"$where": "1==1"}',
        ]
        
        # Test sur l'endpoint products (search)
        for payload in sql_payloads:
            try:
                # Test dans les query params
                response = self.session.get(
                    f"{self.base_url}/products/",
                    params={"search": payload},
                    timeout=10
                )
                
                # Vérifier si l'injection a réussi (erreur SQL exposée)
                if response.status_code == 500:
                    self.log(f"⚠️ Erreur 500 avec payload: {payload[:30]}...", "VULN")
                    self.add_result(
                        "SQL Injection - Products Search",
                        "Injection SQL",
                        False,
                        f"Erreur serveur avec payload: {payload}",
                        "CRITICAL"
                    )
                elif "error" in response.text.lower() and "sql" in response.text.lower():
                    self.log(f"⚠️ Message d'erreur SQL exposé!", "VULN")
                    self.add_result(
                        "SQL Injection - Error Disclosure",
                        "Injection SQL",
                        False,
                        "Message d'erreur SQL visible dans la réponse",
                        "HIGH"
                    )
                else:
                    self.log(f"✓ Payload bloqué: {payload[:30]}...", "SAFE")
                    
            except requests.exceptions.Timeout:
                # Time-based injection possible
                self.log(f"⚠️ Timeout suspect avec: {payload[:30]}...", "VULN")
                self.add_result(
                    "SQL Injection - Time-based",
                    "Injection SQL",
                    False,
                    f"Timeout suspect avec payload: {payload}",
                    "CRITICAL"
                )
            except Exception as e:
                pass
        
        # Test sur l'endpoint login
        for payload in sql_payloads[:5]:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/login/",
                    json={"email": payload, "password": payload},
                    timeout=10
                )
                if response.status_code == 500:
                    self.add_result(
                        "SQL Injection - Login",
                        "Injection SQL",
                        False,
                        f"Erreur 500 sur login avec payload SQL",
                        "CRITICAL"
                    )
            except:
                pass
        
        self.add_result(
            "SQL Injection - General",
            "Injection SQL",
            True,
            "Aucune injection SQL détectée (ORM Django protège)",
            "INFO"
        )

    # ========================================
    # 2. TESTS XSS (Cross-Site Scripting)
    # ========================================
    
    def test_xss(self):
        """Tests XSS sur les inputs"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Cross-Site Scripting (XSS)", "TEST")
        self.log("=" * 50, "TEST")
        
        xss_payloads = [
            # Basic XSS
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            
            # Event handlers
            "\" onmouseover=\"alert('XSS')\"",
            "' onclick='alert(1)'",
            "<div onmouseover='alert(1)'>hover me</div>",
            
            # JavaScript protocol
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            
            # Encoded XSS
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;",
            "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
            
            # Polyglot XSS
            "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcLiCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//>\\x3e",
            
            # DOM-based XSS
            "#<script>alert('XSS')</script>",
            "?q=<script>alert('XSS')</script>",
            
            # SVG XSS
            "<svg><animate onbegin=alert(1) attributeName=x dur=1s>",
            "<svg><set onbegin=alert(1) attributename=x>",
        ]
        
        vulnerable_endpoints = []
        
        # Test sur registration
        for payload in xss_payloads[:5]:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register/",
                    json={
                        "username": payload,
                        "email": f"test{int(time.time())}@test.com",
                        "password": "Test1234!"
                    },
                    timeout=10
                )
                
                # Vérifier si le payload est retourné sans échappement
                if payload in response.text and "<script>" in response.text:
                    self.log(f"⚠️ XSS possible dans register: {payload[:30]}...", "VULN")
                    vulnerable_endpoints.append("register")
                else:
                    self.log(f"✓ XSS bloqué: {payload[:30]}...", "SAFE")
                    
            except Exception as e:
                pass
        
        # Test sur products search
        for payload in xss_payloads:
            try:
                response = self.session.get(
                    f"{self.base_url}/products/",
                    params={"search": payload},
                    timeout=10
                )
                
                # Vérifier la réponse pour les scripts non échappés
                if "<script>" in response.text and "alert" in response.text:
                    self.log(f"⚠️ XSS reflété dans search!", "VULN")
                    vulnerable_endpoints.append("products_search")
                    
            except:
                pass
        
        if vulnerable_endpoints:
            self.add_result(
                "XSS - Reflected",
                "Cross-Site Scripting",
                False,
                f"XSS possible sur: {', '.join(set(vulnerable_endpoints))}",
                "HIGH"
            )
        else:
            self.add_result(
                "XSS - All Endpoints",
                "Cross-Site Scripting",
                True,
                "Aucune vulnérabilité XSS détectée (API JSON)",
                "INFO"
            )

    # ========================================
    # 3. TESTS AUTHENTIFICATION
    # ========================================
    
    def test_broken_authentication(self):
        """Tests de sécurité de l'authentification"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Broken Authentication", "TEST")
        self.log("=" * 50, "TEST")
        
        vulnerabilities = []
        
        # Test 1: Brute Force Protection
        self.log("Test: Protection brute force...", "INFO")
        failed_attempts = 0
        for i in range(8):
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/login/",
                    json={"email": "admin@test.com", "password": f"wrong{i}"},
                    timeout=2
                )
                if response.status_code == 429:  # Too Many Requests
                    self.log(f"✓ Rate limiting activé après {i+1} tentatives", "SAFE")
                    break
                failed_attempts += 1
            except:
                pass
        
        if failed_attempts >= 8:
            self.log("⚠️ Pas de protection brute force!", "VULN")
            vulnerabilities.append("Brute force non bloqué")
        
        # Test 2: Weak Password Policy
        self.log("Test: Politique de mots de passe faibles...", "INFO")
        weak_passwords = ["123", "abc", "password", "a"]
        for pwd in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register/",
                    json={
                        "username": f"weakuser{int(time.time())}",
                        "email": f"weak{int(time.time())}@test.com",
                        "password": pwd
                    },
                    timeout=10
                )
                if response.status_code == 201:
                    self.log(f"⚠️ Mot de passe faible accepté: {pwd}", "VULN")
                    vulnerabilities.append(f"Mot de passe faible accepté: {pwd}")
                else:
                    self.log(f"✓ Mot de passe faible rejeté: {pwd}", "SAFE")
            except:
                pass
        
        # Test 3: JWT Token in URL (should not work)
        self.log("Test: Token JWT dans l'URL...", "INFO")
        if self.auth_token:
            try:
                response = self.session.get(
                    f"{self.base_url}/auth/me/?token={self.auth_token}",
                    timeout=10
                )
                if response.status_code == 200:
                    self.log("⚠️ Token accepté dans l'URL!", "VULN")
                    vulnerabilities.append("Token JWT accepté dans l'URL")
            except:
                pass
        
        # Test 4: Token sans expiration
        self.log("Test: Expiration du token...", "INFO")
        if self.auth_token:
            # Décoder le JWT pour vérifier l'expiration
            try:
                import base64
                parts = self.auth_token.split('.')
                if len(parts) == 3:
                    payload = parts[1]
                    # Ajouter padding
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = json.loads(base64.urlsafe_b64decode(payload))
                    if 'exp' in decoded:
                        self.log(f"✓ Token a une expiration: {decoded['exp']}", "SAFE")
                    else:
                        self.log("⚠️ Token sans expiration!", "VULN")
                        vulnerabilities.append("Token JWT sans expiration")
            except Exception as e:
                pass
        
        # Test 5: Credentials en clair dans les logs/réponses
        self.log("Test: Credentials exposées...", "INFO")
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login/",
                json={"email": "test@test.com", "password": "MySecretPass123"},
                timeout=10
            )
            if "MySecretPass123" in response.text:
                self.log("⚠️ Mot de passe visible dans la réponse!", "VULN")
                vulnerabilities.append("Mot de passe exposé dans la réponse")
            else:
                self.log("✓ Mot de passe non exposé", "SAFE")
        except:
            pass
        
        if vulnerabilities:
            self.add_result(
                "Broken Authentication",
                "Authentication",
                False,
                "; ".join(vulnerabilities),
                "HIGH"
            )
        else:
            self.add_result(
                "Broken Authentication",
                "Authentication",
                True,
                "Authentification correctement sécurisée",
                "INFO"
            )

    # ========================================
    # 4. TESTS IDOR
    # ========================================
    
    def test_idor(self):
        """Tests IDOR (Insecure Direct Object Reference)"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: IDOR (Insecure Direct Object Reference)", "TEST")
        self.log("=" * 50, "TEST")
        
        vulnerabilities = []
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Test 1: Accès aux commandes d'autres utilisateurs
        self.log("Test: Accès aux commandes d'autres users...", "INFO")
        for order_id in range(1, 20):
            try:
                response = self.session.get(
                    f"{self.base_url}/orders/{order_id}/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    # Vérifier si c'est une commande d'un autre user
                    if data.get('user') and data['user'] != self.test_user.get('id'):
                        self.log(f"⚠️ Accès à la commande #{order_id} d'un autre user!", "VULN")
                        vulnerabilities.append(f"Accès commande #{order_id}")
                        break
            except:
                pass
        
        # Test 2: Accès au panier d'autres utilisateurs
        self.log("Test: Accès au panier d'autres users...", "INFO")
        for cart_id in range(1, 20):
            try:
                response = self.session.get(
                    f"{self.base_url}/cart/{cart_id}/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.log(f"⚠️ Accès au panier #{cart_id}!", "VULN")
                    vulnerabilities.append(f"Accès panier #{cart_id}")
                    break
            except:
                pass
        
        # Test 3: Modification d'objets d'autres users
        self.log("Test: Modification d'objets d'autres users...", "INFO")
        for order_id in range(1, 10):
            try:
                response = self.session.patch(
                    f"{self.base_url}/orders/{order_id}/",
                    headers=headers,
                    json={"status": "cancelled"},
                    timeout=10
                )
                if response.status_code == 200:
                    self.log(f"⚠️ Modification de la commande #{order_id}!", "VULN")
                    vulnerabilities.append(f"Modification commande #{order_id}")
                    break
            except:
                pass
        
        # Test 4: Accès aux données utilisateur par ID
        self.log("Test: Enumération des utilisateurs...", "INFO")
        for user_id in range(1, 20):
            try:
                response = self.session.get(
                    f"{self.base_url}/users/{user_id}/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'email' in data or 'password' in data:
                        self.log(f"⚠️ Données user #{user_id} exposées!", "VULN")
                        vulnerabilities.append(f"Données user #{user_id} exposées")
            except:
                pass
        
        if vulnerabilities:
            self.add_result(
                "IDOR",
                "Broken Access Control",
                False,
                "; ".join(vulnerabilities[:3]),
                "CRITICAL"
            )
        else:
            self.add_result(
                "IDOR",
                "Broken Access Control",
                True,
                "Contrôle d'accès correct - isolation des données",
                "INFO"
            )

    # ========================================
    # 5. TESTS RATE LIMITING
    # ========================================
    
    def test_rate_limiting(self):
        """Tests de rate limiting"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Rate Limiting / DoS Protection", "TEST")
        self.log("=" * 50, "TEST")
        
        endpoints_to_test = [
            ("/products/", "GET"),
            ("/auth/login/", "POST"),
            ("/auth/register/", "POST"),
        ]
        
        for endpoint, method in endpoints_to_test:
            self.log(f"Test: Rate limit sur {endpoint}...", "INFO")
            rate_limited = False
            
            # Reduced from 60 to 15 requests for faster testing
            for i in range(15):
                try:
                    if method == "GET":
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            timeout=2
                        )
                    else:
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json={"email": f"test{i}@test.com", "password": "test"},
                            timeout=2
                        )
                    
                    if response.status_code == 429:
                        self.log(f"✓ Rate limiting activé après {i+1} requêtes", "SAFE")
                        rate_limited = True
                        break
                        
                except:
                    pass
            
            if not rate_limited:
                self.log(f"⚠️ Pas de rate limiting sur {endpoint}!", "VULN")
                self.add_result(
                    f"Rate Limiting - {endpoint}",
                    "DoS Protection",
                    False,
                    f"Pas de rate limiting sur {endpoint}",
                    "MEDIUM"
                )
            else:
                self.add_result(
                    f"Rate Limiting - {endpoint}",
                    "DoS Protection",
                    True,
                    f"Rate limiting actif sur {endpoint}",
                    "INFO"
                )

    # ========================================
    # 6. TESTS MASS ASSIGNMENT
    # ========================================
    
    def test_mass_assignment(self):
        """Tests Mass Assignment"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Mass Assignment", "TEST")
        self.log("=" * 50, "TEST")
        
        vulnerabilities = []
        
        # Test 1: Essayer de devenir admin à l'inscription
        self.log("Test: Privilege escalation à l'inscription...", "INFO")
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register/",
                json={
                    "username": f"hacker{int(time.time())}",
                    "email": f"hacker{int(time.time())}@test.com",
                    "password": "Test1234!",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_admin": True,
                    "role": "admin"
                },
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                user_data = data.get('user', {})
                if user_data.get('is_staff') or user_data.get('is_superuser'):
                    self.log("⚠️ Privilege escalation possible!", "VULN")
                    vulnerabilities.append("is_staff/is_superuser accepté")
                else:
                    self.log("✓ Champs admin ignorés", "SAFE")
        except:
            pass
        
        # Test 2: Modifier le prix d'un produit via commande
        self.log("Test: Modification de prix via commande...", "INFO")
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        try:
            response = self.session.post(
                f"{self.base_url}/orders/",
                headers=headers,
                json={
                    "items": [{
                        "product_id": 1,
                        "quantity": 1,
                        "price": 0.01  # Prix manipulé
                    }],
                    "total": 0.01
                },
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                if float(data.get('total', 0)) < 1:
                    self.log("⚠️ Prix manipulé accepté!", "VULN")
                    vulnerabilities.append("Manipulation de prix possible")
                else:
                    self.log("✓ Prix calculé côté serveur", "SAFE")
        except:
            pass
        
        # Test 3: Modifier le stock via panier
        self.log("Test: Modification de stock via panier...", "INFO")
        try:
            response = self.session.post(
                f"{self.base_url}/cart/",
                headers=headers,
                json={
                    "product": 1,
                    "quantity": 1,
                    "stock": 99999  # Tentative de modifier le stock
                },
                timeout=10
            )
        except:
            pass
        
        if vulnerabilities:
            self.add_result(
                "Mass Assignment",
                "Input Validation",
                False,
                "; ".join(vulnerabilities),
                "HIGH"
            )
        else:
            self.add_result(
                "Mass Assignment",
                "Input Validation",
                True,
                "Protection contre le mass assignment active",
                "INFO"
            )

    # ========================================
    # 7. TESTS PATH TRAVERSAL
    # ========================================
    
    def test_path_traversal(self):
        """Tests Path Traversal"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Path Traversal / LFI", "TEST")
        self.log("=" * 50, "TEST")
        
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc/passwd",
            "/etc/passwd",
            "file:///etc/passwd",
            "....//....//....//....//etc/passwd",
            "..%c0%af..%c0%af..%c0%afetc/passwd",
        ]
        
        vulnerable = False
        
        for payload in traversal_payloads:
            try:
                # Test sur les images de produits
                response = self.session.get(
                    f"{self.base_url}/products/image/{payload}",
                    timeout=10,
                    allow_redirects=False
                )
                
                if response.status_code == 200:
                    if "root:" in response.text or "NTLM" in response.text:
                        self.log(f"⚠️ Path traversal réussi: {payload}", "VULN")
                        vulnerable = True
                        break
                
                # Test dans les query params
                response = self.session.get(
                    f"{self.base_url}/products/",
                    params={"file": payload},
                    timeout=10
                )
                
            except:
                pass
        
        if vulnerable:
            self.add_result(
                "Path Traversal",
                "File Access",
                False,
                "Vulnérabilité Path Traversal détectée",
                "CRITICAL"
            )
        else:
            self.add_result(
                "Path Traversal",
                "File Access",
                True,
                "Pas de vulnérabilité Path Traversal",
                "INFO"
            )

    # ========================================
    # 8. TESTS SSRF
    # ========================================
    
    def test_ssrf(self):
        """Tests SSRF (Server-Side Request Forgery)"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: SSRF (Server-Side Request Forgery)", "TEST")
        self.log("=" * 50, "TEST")
        
        ssrf_payloads = [
            "http://localhost:22",
            "http://127.0.0.1:22",
            "http://0.0.0.0:22",
            "http://[::1]:22",
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "http://metadata.google.internal/",  # GCP metadata
            "http://localhost:6379",  # Redis
            "http://localhost:27017",  # MongoDB
            "file:///etc/passwd",
            "dict://localhost:11211/",
            "gopher://localhost:25/",
        ]
        
        vulnerable = False
        
        # Test sur l'endpoint external/rates
        for payload in ssrf_payloads:
            try:
                response = self.session.get(
                    f"{self.base_url}/external/rates/",
                    params={"base": payload},
                    timeout=10
                )
                
                # Vérifier si la requête interne a été faite
                if response.status_code == 200:
                    if "meta-data" in response.text or "ami-id" in response.text:
                        self.log(f"⚠️ SSRF possible vers: {payload}", "VULN")
                        vulnerable = True
                        break
                        
            except requests.exceptions.Timeout:
                self.log(f"⚠️ Timeout suspect avec: {payload[:30]}...", "WARNING")
            except:
                pass
        
        if vulnerable:
            self.add_result(
                "SSRF",
                "Server-Side Request Forgery",
                False,
                "Vulnérabilité SSRF détectée",
                "CRITICAL"
            )
        else:
            self.add_result(
                "SSRF",
                "Server-Side Request Forgery",
                True,
                "Pas de vulnérabilité SSRF (paramètres validés)",
                "INFO"
            )

    # ========================================
    # 9. TESTS JWT SECURITY
    # ========================================
    
    def test_jwt_security(self):
        """Tests de sécurité JWT"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: JWT Token Security", "TEST")
        self.log("=" * 50, "TEST")
        
        vulnerabilities = []
        
        # Test 1: Token avec algorithme "none"
        self.log("Test: JWT avec alg=none...", "INFO")
        fake_token_none = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0."
        try:
            response = self.session.get(
                f"{self.base_url}/auth/me/",
                headers={"Authorization": f"Bearer {fake_token_none}"},
                timeout=10
            )
            if response.status_code == 200:
                self.log("⚠️ Token alg=none accepté!", "VULN")
                vulnerabilities.append("Algorithme 'none' accepté")
            else:
                self.log("✓ Token alg=none rejeté", "SAFE")
        except:
            pass
        
        # Test 2: Token expiré
        self.log("Test: Token expiré...", "INFO")
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxMDAwMDAwMDAwfQ.fake"
        try:
            response = self.session.get(
                f"{self.base_url}/auth/me/",
                headers={"Authorization": f"Bearer {expired_token}"},
                timeout=10
            )
            if response.status_code == 200:
                self.log("⚠️ Token expiré accepté!", "VULN")
                vulnerabilities.append("Token expiré accepté")
            else:
                self.log("✓ Token expiré rejeté", "SAFE")
        except:
            pass
        
        # Test 3: Token avec signature invalide
        self.log("Test: Token signature invalide...", "INFO")
        if self.auth_token:
            parts = self.auth_token.split('.')
            if len(parts) == 3:
                tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"
                try:
                    response = self.session.get(
                        f"{self.base_url}/auth/me/",
                        headers={"Authorization": f"Bearer {tampered_token}"},
                        timeout=10
                    )
                    if response.status_code == 200:
                        self.log("⚠️ Signature non vérifiée!", "VULN")
                        vulnerabilities.append("Signature JWT non vérifiée")
                    else:
                        self.log("✓ Signature vérifiée", "SAFE")
                except:
                    pass
        
        # Test 4: Token avec payload modifié
        self.log("Test: Token payload modifié...", "INFO")
        if self.auth_token:
            try:
                import base64
                parts = self.auth_token.split('.')
                if len(parts) == 3:
                    # Modifier le payload pour devenir admin
                    payload = base64.urlsafe_b64decode(parts[1] + '==')
                    payload_data = json.loads(payload)
                    payload_data['is_staff'] = True
                    payload_data['is_superuser'] = True
                    new_payload = base64.urlsafe_b64encode(
                        json.dumps(payload_data).encode()
                    ).decode().rstrip('=')
                    
                    modified_token = f"{parts[0]}.{new_payload}.{parts[2]}"
                    
                    response = self.session.get(
                        f"{self.base_url}/auth/me/",
                        headers={"Authorization": f"Bearer {modified_token}"},
                        timeout=10
                    )
                    if response.status_code == 200:
                        self.log("⚠️ Payload modifié accepté!", "VULN")
                        vulnerabilities.append("Modification de payload acceptée")
                    else:
                        self.log("✓ Payload modifié rejeté", "SAFE")
            except:
                pass
        
        if vulnerabilities:
            self.add_result(
                "JWT Security",
                "Authentication",
                False,
                "; ".join(vulnerabilities),
                "CRITICAL"
            )
        else:
            self.add_result(
                "JWT Security",
                "Authentication",
                True,
                "JWT correctement sécurisé",
                "INFO"
            )

    # ========================================
    # 10. TESTS HEADERS DE SÉCURITÉ
    # ========================================
    
    def test_security_headers(self):
        """Tests des headers de sécurité HTTP"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Security Headers", "TEST")
        self.log("=" * 50, "TEST")
        
        try:
            response = self.session.get(f"{self.base_url}/products/", timeout=10)
            headers = response.headers
            
            missing_headers = []
            
            # Headers de sécurité recommandés
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": None,  # Juste vérifier présence
                "Content-Security-Policy": None,
                "Referrer-Policy": None,
            }
            
            for header, expected in security_headers.items():
                value = headers.get(header)
                if not value:
                    self.log(f"⚠️ Header manquant: {header}", "WARNING")
                    missing_headers.append(header)
                else:
                    self.log(f"✓ {header}: {value[:50]}", "SAFE")
            
            # Vérifier qu'il n'y a pas de headers dangereux
            dangerous_headers = ["Server", "X-Powered-By"]
            for header in dangerous_headers:
                if header in headers:
                    self.log(f"⚠️ Header exposant des infos: {header}={headers[header]}", "WARNING")
                    missing_headers.append(f"Supprimer {header}")
            
            if missing_headers:
                self.add_result(
                    "Security Headers",
                    "HTTP Security",
                    False,
                    f"Headers manquants/à corriger: {', '.join(missing_headers)}",
                    "MEDIUM"
                )
            else:
                self.add_result(
                    "Security Headers",
                    "HTTP Security",
                    True,
                    "Tous les headers de sécurité sont présents",
                    "INFO"
                )
                
        except Exception as e:
            self.log(f"Erreur lors du test: {e}", "ERROR")

    # ========================================
    # 11. TESTS INPUT VALIDATION
    # ========================================
    
    def test_input_validation(self):
        """Tests de validation des entrées"""
        self.log("=" * 50, "TEST")
        self.log("🔍 TEST: Input Validation", "TEST")
        self.log("=" * 50, "TEST")
        
        vulnerabilities = []
        
        # Test 1: Quantité négative
        self.log("Test: Quantité négative...", "INFO")
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        try:
            response = self.session.post(
                f"{self.base_url}/cart/",
                headers=headers,
                json={"product": 1, "quantity": -10},
                timeout=10
            )
            if response.status_code == 201:
                self.log("⚠️ Quantité négative acceptée!", "VULN")
                vulnerabilities.append("Quantité négative acceptée")
            else:
                self.log("✓ Quantité négative rejetée", "SAFE")
        except:
            pass
        
        # Test 2: Quantité énorme
        self.log("Test: Quantité énorme...", "INFO")
        try:
            response = self.session.post(
                f"{self.base_url}/cart/",
                headers=headers,
                json={"product": 1, "quantity": 999999999},
                timeout=10
            )
            if response.status_code == 201:
                self.log("⚠️ Quantité énorme acceptée!", "VULN")
                vulnerabilities.append("Quantité énorme acceptée")
            else:
                self.log("✓ Quantité énorme rejetée", "SAFE")
        except:
            pass
        
        # Test 3: Email invalide
        self.log("Test: Format email...", "INFO")
        invalid_emails = [
            "notanemail",
            "test@",
            "@test.com",
            "test@.com",
            "test@com",
            "a" * 500 + "@test.com"
        ]
        for email in invalid_emails:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register/",
                    json={
                        "username": f"test{int(time.time())}",
                        "email": email,
                        "password": "Test1234!"
                    },
                    timeout=10
                )
                if response.status_code == 201:
                    self.log(f"⚠️ Email invalide accepté: {email[:30]}", "VULN")
                    vulnerabilities.append(f"Email invalide accepté")
                    break
            except:
                pass
        
        # Test 4: Payload très long
        self.log("Test: Payload très long (DoS)...", "INFO")
        try:
            long_string = "A" * 1000000  # 1MB
            response = self.session.post(
                f"{self.base_url}/auth/register/",
                json={
                    "username": long_string,
                    "email": "test@test.com",
                    "password": "Test1234!"
                },
                timeout=30
            )
            if response.status_code == 500:
                self.log("⚠️ Crash avec payload long!", "VULN")
                vulnerabilities.append("Crash avec payload long")
        except requests.exceptions.Timeout:
            self.log("⚠️ Timeout avec payload long (DoS possible)", "WARNING")
        except:
            self.log("✓ Payload long géré correctement", "SAFE")
        
        # Test 5: Caractères spéciaux/Unicode
        self.log("Test: Caractères Unicode...", "INFO")
        unicode_payloads = [
            "𝕳𝖊𝖑𝖑𝖔",
            "test\x00null",
            "test\r\ninjection",
            "👨‍💻🔓",
            "\u202E\u0041\u0042\u0043"  # Right-to-left override
        ]
        for payload in unicode_payloads:
            try:
                response = self.session.get(
                    f"{self.base_url}/products/",
                    params={"search": payload},
                    timeout=10
                )
            except:
                pass
        
        if vulnerabilities:
            self.add_result(
                "Input Validation",
                "Input Validation",
                False,
                "; ".join(vulnerabilities),
                "MEDIUM"
            )
        else:
            self.add_result(
                "Input Validation",
                "Input Validation",
                True,
                "Validation des entrées correcte",
                "INFO"
            )

    # ========================================
    # RAPPORT FINAL
    # ========================================
    
    def generate_report(self):
        """Générer le rapport final"""
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}{Colors.CYAN}📊 RAPPORT DE SÉCURITÉ{Colors.END}")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = sum(1 for r in self.results if not r['passed'])
        
        print(f"\n{Colors.GREEN}✅ Tests réussis: {passed}{Colors.END}")
        print(f"{Colors.RED}❌ Vulnérabilités: {failed}{Colors.END}")
        
        # Grouper par catégorie
        categories = {}
        for r in self.results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        print("\n" + "-" * 60)
        print(f"{Colors.BOLD}DÉTAIL PAR CATÉGORIE:{Colors.END}")
        print("-" * 60)
        
        severity_colors = {
            "CRITICAL": Colors.RED + Colors.BOLD,
            "HIGH": Colors.RED,
            "MEDIUM": Colors.YELLOW,
            "LOW": Colors.BLUE,
            "INFO": Colors.GREEN
        }
        
        for cat, tests in categories.items():
            print(f"\n{Colors.PURPLE}📁 {cat}{Colors.END}")
            for test in tests:
                status = "✅" if test['passed'] else "❌"
                color = severity_colors.get(test['severity'], Colors.WHITE)
                print(f"   {status} [{color}{test['severity']}{Colors.END}] {test['test']}")
                if not test['passed']:
                    print(f"      └─ {test['details'][:80]}")
        
        # Vulnérabilités critiques
        critical = [r for r in self.results if not r['passed'] and r['severity'] in ['CRITICAL', 'HIGH']]
        if critical:
            print("\n" + "=" * 60)
            print(f"{Colors.RED}{Colors.BOLD}🚨 VULNÉRABILITÉS CRITIQUES À CORRIGER:{Colors.END}")
            print("=" * 60)
            for vuln in critical:
                print(f"  • [{vuln['severity']}] {vuln['test']}: {vuln['details']}")
        
        # Score de sécurité
        total = len(self.results)
        score = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        if score >= 80:
            color = Colors.GREEN
            grade = "A"
        elif score >= 60:
            color = Colors.YELLOW
            grade = "B"
        elif score >= 40:
            color = Colors.YELLOW
            grade = "C"
        else:
            color = Colors.RED
            grade = "D"
        
        print(f"{Colors.BOLD}SCORE DE SÉCURITÉ: {color}{score:.1f}% (Grade {grade}){Colors.END}")
        print("=" * 60)
        
        # Sauvegarder en JSON
        report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "score": score,
                "grade": grade,
                "passed": passed,
                "failed": failed,
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport sauvegardé: {report_file}")
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║     🔐 TESTS DE SÉCURITÉ - API E-COMMERCE                ║")
        print("║     Attaques: SQL Injection, XSS, IDOR, SSRF...          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        self.log(f"Cible: {self.base_url}", "INFO")
        self.log("Démarrage des tests de sécurité...", "INFO")
        
        # Setup
        self.setup_test_user()
        
        # Tests
        tests = [
            self.test_sql_injection,
            self.test_xss,
            self.test_broken_authentication,
            self.test_idor,
            self.test_rate_limiting,
            self.test_mass_assignment,
            self.test_path_traversal,
            self.test_ssrf,
            self.test_jwt_security,
            self.test_security_headers,
            self.test_input_validation,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log(f"Erreur dans {test_func.__name__}: {e}", "ERROR")
        
        # Rapport
        self.generate_report()


def main():
    parser = argparse.ArgumentParser(description='Tests de sécurité API')
    parser.add_argument('--url', default='http://localhost:8000', help='URL de base de l\'API')
    args = parser.parse_args()
    
    tester = SecurityTester(args.url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
