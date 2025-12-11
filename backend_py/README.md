# 🔧 Backend Django REST Framework

API REST sécurisée pour la plateforme e-commerce.

---

## 📋 Table des matières

- [🛠️ Technologies](#️-technologies)
- [🚀 Installation](#-installation)
- [📁 Structure](#-structure)
- [🔌 API Endpoints](#-api-endpoints)
- [🔒 Sécurité](#-sécurité)
- [🧪 Tests](#-tests)
- [🐳 Docker](#-docker)

---

## 🛠️ Technologies

| Technologie | Version | Rôle |
|-------------|---------|------|
| Django | 5.2.8 | Framework web |
| Django REST Framework | 3.16.1 | API REST |
| Simple JWT | 5.5.1 | Authentification JWT |
| PostgreSQL | 15+ | Base de données (prod) |
| SQLite | - | Base de données (dev) |
| Stripe | 14.0.1 | Paiements |
| Gunicorn | 23.0.0 | Serveur WSGI |

---

## 🚀 Installation

### 1. Environnement virtuel

```powershell
cd backend_py
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Dépendances

```powershell
pip install -r requirements.txt
```

### 3. Configuration

```powershell
# Copier le fichier exemple
cp .env.example .env

# Éditer avec vos valeurs
notepad .env
```

**Variables essentielles :**
```env
SECRET_KEY=votre-cle-secrete-tres-longue
DEBUG=True
DB_ENGINE=sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 4. Base de données

```powershell
python manage.py migrate
```

### 5. Données de test

```powershell
python manage.py seed_products
```

### 6. Superutilisateur (optionnel)

```powershell
python manage.py createsuperuser
```

### 7. Lancer le serveur

```powershell
python manage.py runserver
```

✅ **API disponible sur** : http://localhost:8000

---

## 📁 Structure

```
backend_py/
├── manage.py                    # CLI Django
├── requirements.txt             # Dépendances Python
├── .env.example                 # Template variables d'env
├── docker-compose.yml           # Config Docker
├── Dockerfile                   # Image Docker
├── gunicorn.conf.py             # Config production
├── security_tests.py            # Tests de sécurité
│
└── backend_py/
    ├── __init__.py
    ├── settings.py              # Configuration Django
    ├── urls.py                  # Routes principales
    ├── middleware.py            # Middlewares custom
    ├── utils.py                 # Utilitaires
    ├── wsgi.py                  # Point d'entrée WSGI
    ├── asgi.py                  # Point d'entrée ASGI
    │
    ├── users/                   # 👤 Authentification
    │   ├── models.py            # Modèle User custom
    │   ├── serializers.py       # Sérialisation
    │   ├── views.py             # Vues API
    │   └── urls.py              # Routes /auth/
    │
    ├── products/                # 📦 Produits
    │   ├── models.py            # Modèle Product
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py              # Routes /products/
    │   └── management/
    │       └── commands/
    │           └── seed_products.py  # Données de test
    │
    ├── cart/                    # 🛒 Panier
    │   ├── models.py            # Modèle CartItem
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py              # Routes /cart/
    │
    ├── orders/                  # 📋 Commandes
    │   ├── models.py            # Models Order, OrderItem
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py              # Routes /orders/
    │
    ├── payments/                # 💳 Stripe
    │   ├── views.py             # Payment Intent, Webhook
    │   └── urls.py              # Routes /payment/
    │
    └── external/                # 🌐 API Externes
        ├── views.py             # FakeStore, Rates
        └── urls.py              # Routes /external/
```

---

## 🔌 API Endpoints

### Authentification (`/auth/`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/auth/register/` | Inscription | Non |
| POST | `/auth/login/` | Connexion JWT | Non |
| POST | `/auth/token/refresh/` | Refresh token | Non |
| GET | `/auth/me/` | Profil utilisateur | Oui |

### Produits (`/products/`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/products/` | Liste produits | Non |
| GET | `/products/{id}/` | Détail produit | Non |
| POST | `/products/` | Créer produit | Admin |
| PUT | `/products/{id}/` | Modifier produit | Admin |
| DELETE | `/products/{id}/` | Supprimer produit | Admin |

### Panier (`/cart/`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/cart/` | Mon panier | Oui |
| POST | `/cart/` | Ajouter article | Oui |
| PUT | `/cart/{id}/` | Modifier quantité | Oui |
| DELETE | `/cart/{id}/` | Retirer article | Oui |

### Commandes (`/orders/`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/orders/` | Mes commandes | Oui |
| POST | `/orders/` | Créer commande | Oui |
| GET | `/orders/{id}/` | Détail commande | Oui |

### Paiements (`/payment/`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/payment/create-intent/` | Payment Intent | Oui |
| POST | `/payment/webhook/` | Webhook Stripe | Non |

### API Externes (`/external/`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/external/products/` | FakeStore API | Non |
| GET | `/external/rates/` | Taux de change | Non |

### Utilitaires

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health/` | Santé de l'API |
| GET | `/admin/` | Interface admin |

---

## 🔒 Sécurité

### JWT Configuration

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

### Rate Limiting

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/min",
        "user": "100/min",
        "login": "5/min",
        "register": "3/min",
    },
}
```

### Headers Sécurisés

- HSTS (HTTP Strict Transport Security)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Content-Security-Policy
- Referrer-Policy

### Middlewares Custom

```python
# backend_py/middleware.py
class SecurityHeadersMiddleware:
    # Ajoute automatiquement les headers de sécurité
```

---

## 🧪 Tests

### Tests unitaires

```powershell
python manage.py test
```

### Tests de sécurité

```powershell
python security_tests.py
```

### Avec couverture

```powershell
pip install coverage
coverage run manage.py test
coverage report -m
coverage html  # Génère un rapport HTML
```

---

## 🐳 Docker

### Développement

```powershell
docker-compose up --build
```

### Production

```powershell
docker-compose -f docker-compose.prod.yml up -d
```

### Variables Docker

Le `docker-compose.yml` configure :
- **PostgreSQL** : Port 5432
- **Django** : Port 8000
- **Volumes** : Persistance des données

---

## 📝 Commandes utiles

```powershell
# Créer une migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Shell Django
python manage.py shell

# Créer superuser
python manage.py createsuperuser

# Collecter les fichiers statiques (prod)
python manage.py collectstatic

# Vérifier les problèmes de déploiement
python manage.py check --deploy
```

---

## 📚 Documentation complémentaire

- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) - Documentation API complète
- [instruction.md](../instruction.md) - Guide d'installation global
