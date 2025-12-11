# 📋 Instructions - Projet E-Commerce

Guide d'installation et d'exécution complet du projet e-commerce.

## 🛠️ Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Frontend** | React + Vite | React 19.x |
| **Backend** | Django REST Framework | Django 5.2.x |
| **Base de données** | PostgreSQL / SQLite | PostgreSQL 15+ |
| **Authentification** | JWT (Simple JWT) | - |
| **Paiements** | Stripe | - |

---

## 📋 Prérequis

- **Python** 3.11 ou supérieur
- **Node.js** 18 ou supérieur
- **npm** ou **yarn**
- **PostgreSQL** (optionnel, SQLite par défaut en dev)
- **Git**
- **PowerShell** (Windows)

---

## 📁 Structure du Projet

```
-Project_API-/
├── backend_py/          # API Django REST Framework
│   ├── backend_py/      # Configuration et apps Django
│   │   ├── users/       # Authentification & utilisateurs
│   │   ├── products/    # Gestion des produits
│   │   ├── cart/        # Panier utilisateur
│   │   ├── orders/      # Commandes
│   │   ├── payments/    # Intégration Stripe
│   │   └── external/    # API externes
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/            # Application React + Vite
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── components/
│   │   └── pages/
│   ├── package.json
│   └── vite.config.js
│
├── db/                  # Scripts SQL de référence
├── README.md            # Documentation principale
├── API_DOCUMENTATION.md # Documentation API complète
└── instruction.md       # Ce fichier
```

---

## 🚀 Installation Backend (Django)

### 1. Accéder au dossier backend

```powershell
cd "C:\Users\natha\OneDrive\ING2\API\projet Api\-Project_API-\backend_py"
```

### 2. Créer un environnement virtuel Python

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```powershell
# Copier le fichier exemple
cp .env.example .env

# Éditer le fichier .env avec vos valeurs
notepad .env
```

**Contenu minimal du `.env` :**
```env
SECRET_KEY=votre-cle-secrete-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 5. Appliquer les migrations

```powershell
python manage.py migrate
```

### 6. Charger les données de test (optionnel)

```powershell
python manage.py seed_products
```

### 7. Créer un superutilisateur (optionnel)

```powershell
python manage.py createsuperuser
```

### 8. Lancer le serveur

```powershell
python manage.py runserver
```

✅ **Backend disponible sur** : http://localhost:8000

---

## 🎨 Installation Frontend (React)

### 1. Accéder au dossier frontend

```powershell
cd "C:\Users\natha\OneDrive\ING2\API\projet Api\-Project_API-\frontend"
```

### 2. Installer les dépendances

```powershell
npm install
```

### 3. Lancer le serveur de développement

```powershell
npm run dev
```

✅ **Frontend disponible sur** : http://localhost:5173

---

## 🔗 Configuration Proxy (Vite → Django)

Le fichier `vite.config.js` est configuré pour rediriger les appels API :

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## 🧪 Vérifications

### Test du backend

```powershell
# Endpoint de santé
curl http://localhost:8000/health/
# Réponse attendue : {"ok": true}

# Liste des produits
curl http://localhost:8000/products/
```

### Test du frontend

1. Ouvrir http://localhost:5173
2. Vérifier que les produits s'affichent
3. Tester l'inscription/connexion
4. Ajouter un produit au panier

---

## 🐳 Utilisation avec Docker

### Lancer avec Docker Compose

```powershell
cd backend_py
docker-compose up --build
```

Cela démarre :
- **PostgreSQL** sur le port 5432
- **Django** sur le port 8000

---

## 📊 Endpoints API Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health/` | GET | Vérification santé API |
| `/auth/register/` | POST | Inscription |
| `/auth/login/` | POST | Connexion (JWT) |
| `/auth/me/` | GET | Profil utilisateur |
| `/products/` | GET | Liste des produits |
| `/cart/` | GET/POST | Gestion panier |
| `/orders/` | GET/POST | Gestion commandes |
| `/payment/create-intent/` | POST | Paiement Stripe |
| `/external/products/` | GET | Produits FakeStore |
| `/external/rates/` | GET | Taux de change |

> 📖 Documentation complète : [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 🔒 Sécurité

### Mesures implémentées

- ✅ **JWT** avec tokens à durée limitée (30 min)
- ✅ **Rate Limiting** (30-100 req/min selon le type)
- ✅ **CORS** configuré pour le frontend uniquement
- ✅ **Headers sécurisés** (HSTS, CSP, X-Frame-Options)
- ✅ **Validation des entrées** côté backend et frontend
- ✅ **Protection CSRF** native Django
- ✅ **Hashing des mots de passe** (PBKDF2)

---

## 🛠️ Commandes Utiles

### Backend

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer le serveur
python manage.py runserver

# Créer une migration après modification des modèles
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Lancer les tests
python manage.py test

# Tests de sécurité
python security_tests.py

# Shell Django
python manage.py shell
```

### Frontend

```powershell
# Développement
npm run dev

# Build production
npm run build

# Preview du build
npm run preview

# Linting
npm run lint
```

---

## 🔧 Variables d'Environnement

### Backend (.env)

| Variable | Description | Défaut |
|----------|-------------|--------|
| `SECRET_KEY` | Clé secrète Django | (obligatoire) |
| `DEBUG` | Mode debug | False |
| `ALLOWED_HOSTS` | Hôtes autorisés | localhost |
| `DB_ENGINE` | Type de BDD (sqlite3/postgresql) | postgresql |
| `DB_NAME` | Nom de la base | project_api |
| `DB_USER` | Utilisateur DB | postgres |
| `DB_PASSWORD` | Mot de passe DB | - |
| `DB_HOST` | Hôte DB | localhost |
| `DB_PORT` | Port DB | 5432 |
| `CORS_ALLOWED_ORIGINS` | Origins CORS | http://localhost:5173 |
| `STRIPE_SECRET_KEY` | Clé secrète Stripe | - |
| `STRIPE_WEBHOOK_SECRET` | Secret webhook Stripe | - |

---

## 🐛 Dépannage

### Erreur CORS

Vérifier que `CORS_ALLOWED_ORIGINS` dans `.env` contient l'URL du frontend.

### Erreur de migration

```powershell
python manage.py migrate --run-syncdb
```

### Port déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus
taskkill /PID <PID> /F
```

### Problème de dépendances Python

```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Documentation Complémentaire

- [README.md](README.md) - Vue d'ensemble du projet
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentation API détaillée
- [backend_py/README.md](backend_py/README.md) - Documentation backend
- [frontend/README.md](frontend/README.md) - Documentation frontend

---

## 👥 Auteurs

Projet réalisé dans le cadre du cours **API** - ING2 2025