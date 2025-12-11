# 🛒 Projet E-Commerce API

[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19.1-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

Plateforme e-commerce complète avec **API REST sécurisée** (Django REST Framework) et **interface React moderne**.

## 📋 Table des matières

- [🎯 Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [🚀 Installation rapide](#-installation-rapide)
- [📁 Structure du projet](#-structure-du-projet)
- [🔌 Endpoints API](#-endpoints-api)
- [🔒 Sécurité](#-sécurité)
- [🧪 Tests](#-tests)
- [🐳 Docker](#-docker)
- [📚 Documentation](#-documentation)

---

## 🎯 Fonctionnalités

### Backend (Django REST Framework)
- ✅ **Authentification JWT** - Inscription, connexion, refresh tokens
- ✅ **Gestion des produits** - CRUD complet avec permissions admin
- ✅ **Panier utilisateur** - Persistant côté serveur
- ✅ **Commandes** - Création avec gestion transactionnelle du stock
- ✅ **Paiement Stripe** - Intégration Payment Intent
- ✅ **API externe** - FakeStore API + taux de change
- ✅ **Rate limiting** - Protection contre les abus
- ✅ **Sécurité avancée** - Headers, CORS, validation

### Frontend (React + Vite)
- ✅ **Interface moderne** - Design responsive
- ✅ **Catalogue produits** - Affichage avec filtres
- ✅ **Panier interactif** - Sidebar avec gestion quantités
- ✅ **Authentification** - Login/Register avec JWT
- ✅ **Historique commandes** - Page "Mes commandes"
- ✅ **Paiement Stripe** - Formulaire sécurisé
- ✅ **API externe** - Import produits + convertisseur devises

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React (Vite)   │────▶│  Django REST    │────▶│  PostgreSQL     │
│  Port 5173      │     │  Port 8000      │     │  Port 5432      │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │  Stripe API   │         │ FakeStore API │
           │  (Paiements)  │         │ (Produits)    │
           └───────────────┘         └───────────────┘
```

---

## 🚀 Installation rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL (ou SQLite pour dev)

### 1. Cloner le projet
```powershell
git clone https://github.com/Nathan2412/-Project_API-.git
cd -Project_API-
```

### 2. Backend (Django)
```powershell
cd backend_py

# Créer environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# Migrations
python manage.py migrate

# Charger données de test
python manage.py seed_products

# Créer superuser (optionnel)
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### 3. Frontend (React)
```powershell
cd frontend

# Installer dépendances
npm install

# Lancer en développement
npm run dev
```

### 4. Accès
- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **Admin Django** : http://localhost:8000/admin

---

## 📁 Structure du projet

```
-Project_API-/
├── 📄 README.md                 # Ce fichier
├── 📄 instruction.md            # Guide d'installation détaillé
├── 📄 API_DOCUMENTATION.md      # Documentation complète des endpoints
│
├── 📁 backend_py/               # Backend Django REST Framework
│   ├── 📄 manage.py
│   ├── 📄 requirements.txt
│   ├── 📄 .env.example
│   ├── 📄 docker-compose.yml
│   ├── 📄 Dockerfile
│   │
│   └── 📁 backend_py/
│       ├── 📄 settings.py       # Configuration Django
│       ├── 📄 urls.py           # Routes principales
│       ├── 📁 users/            # Auth & utilisateurs
│       ├── 📁 products/         # Gestion produits
│       ├── 📁 cart/             # Panier
│       ├── 📁 orders/           # Commandes
│       ├── 📁 payments/         # Stripe
│       └── 📁 external/         # API externes
│
├── 📁 frontend/                 # Frontend React + Vite
│   ├── 📄 package.json
│   ├── 📄 vite.config.js
│   └── 📁 src/
│       ├── 📄 App.jsx           # Composant principal
│       ├── 📄 api.js            # Client API
│       ├── 📁 components/       # Composants React
│       └── 📁 pages/            # Pages de l'application
│
└── 📁 db/
    └── 📄 schema.sql            # Schéma SQL (référence)
```

---

## 🔌 Endpoints API

### Authentification
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register/` | Inscription |
| POST | `/auth/login/` | Connexion (retourne JWT) |
| POST | `/auth/token/refresh/` | Rafraîchir le token |
| GET | `/auth/me/` | Profil utilisateur |

### Produits
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/products/` | Liste des produits |
| GET | `/products/{id}/` | Détail d'un produit |
| POST | `/products/` | Créer (admin) |
| PUT | `/products/{id}/` | Modifier (admin) |
| DELETE | `/products/{id}/` | Supprimer (admin) |

### Panier
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/cart/` | Contenu du panier |
| POST | `/cart/` | Ajouter au panier |
| PUT | `/cart/{id}/` | Modifier quantité |
| DELETE | `/cart/{id}/` | Retirer du panier |

### Commandes
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/orders/` | Mes commandes |
| POST | `/orders/` | Créer une commande |
| GET | `/orders/{id}/` | Détail commande |

### Paiement
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/payment/create-intent/` | Créer Payment Intent |
| POST | `/payment/webhook/` | Webhook Stripe |

### API Externes
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/external/products/` | Produits FakeStore |
| GET | `/external/rates/?base=EUR` | Taux de change |
| GET | `/health/` | Santé de l'API |

> 📖 Voir [API_DOCUMENTATION.md](API_DOCUMENTATION.md) pour la documentation complète avec exemples.

---

## 🔒 Sécurité

### Mesures implémentées

| Catégorie | Protection |
|-----------|------------|
| **Authentification** | JWT avec refresh tokens, expiration courte (30min) |
| **Rate Limiting** | 30 req/min (anon), 100 req/min (auth), 5 req/min (login) |
| **Headers** | HSTS, X-Content-Type-Options, X-Frame-Options, CSP |
| **CORS** | Origines autorisées configurables |
| **Validation** | Sanitization des entrées, validation Django/DRF |
| **SQL** | ORM Django (protection injection) |
| **XSS** | Sanitization côté frontend et backend |
| **CSRF** | Protection Django native |

### Configuration sécurisée
```python
# backend_py/settings.py
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
}
```

---

## 🧪 Tests

### Backend
```powershell
cd backend_py

# Tests unitaires
python manage.py test

# Tests de sécurité
python security_tests.py

# Avec couverture
pip install coverage
coverage run manage.py test
coverage report
```

### Frontend
```powershell
cd frontend

# Linting
npm run lint
```

---

## 🐳 Docker

### Développement
```powershell
cd backend_py
docker-compose up --build
```

### Production
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

Le fichier `docker-compose.yml` inclut :
- Application Django (Gunicorn)
- PostgreSQL
- Volumes persistants

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Vue d'ensemble (ce fichier) |
| [instruction.md](instruction.md) | Guide d'installation détaillé |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Documentation API complète |
| [backend_py/README.md](backend_py/README.md) | Documentation backend |
| [frontend/README.md](frontend/README.md) | Documentation frontend |

---

## 👥 Équipe

Projet réalisé dans le cadre du cours **API** - ING2 2025

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.
