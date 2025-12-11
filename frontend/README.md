# 🎨 Frontend React + Vite

Interface utilisateur moderne pour la plateforme e-commerce.

---

## 📋 Table des matières

- [🛠️ Technologies](#️-technologies)
- [🚀 Installation](#-installation)
- [📁 Structure](#-structure)
- [🔧 Configuration](#-configuration)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🎯 Composants](#-composants)

---

## 🛠️ Technologies

| Technologie | Version | Rôle |
|-------------|---------|------|
| React | 19.1 | Librairie UI |
| Vite | 7.x | Build tool |
| ESLint | 9.x | Linting |

---

## 🚀 Installation

### 1. Installer les dépendances

```powershell
cd frontend
npm install
```

### 2. Lancer en développement

```powershell
npm run dev
```

✅ **Application disponible sur** : http://localhost:5173

### 3. Build production

```powershell
npm run build
```

### 4. Prévisualiser le build

```powershell
npm run preview
```

---

## 📁 Structure

```
frontend/
├── package.json              # Dépendances et scripts
├── vite.config.js            # Configuration Vite
├── eslint.config.js          # Configuration ESLint
├── index.html                # Point d'entrée HTML
│
├── public/                   # Assets statiques
│
└── src/
    ├── main.jsx              # Point d'entrée React
    ├── App.jsx               # Composant principal
    ├── App.css               # Styles de l'application
    ├── index.css             # Styles globaux
    ├── api.js                # Client API
    │
    ├── components/           # Composants réutilisables
    │   ├── Header.jsx
    │   ├── ProductCard.jsx
    │   ├── Cart.jsx
    │   ├── OrderHistory.jsx
    │   ├── CurrencyConverter.jsx
    │   └── ExternalProducts.jsx
    │
    ├── pages/                # Pages de l'application
    │   └── Orders.jsx
    │
    └── assets/               # Images, icônes
```

---

## 🔧 Configuration

### Proxy API (vite.config.js)

Le proxy redirige les appels `/api` vers le backend Django :

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

### Variables d'environnement (optionnel)

Créer un fichier `.env` à la racine de `frontend/` :

```env
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLIC_KEY=pk_test_xxxxx
```

Utilisation dans le code :
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

---

## ✨ Fonctionnalités

### 🛒 Catalogue Produits
- Affichage en grille responsive
- Indicateur de stock (rupture, stock faible)
- Bouton "Ajouter au panier"
- Image produit avec fallback

### 🛍️ Panier
- Sidebar latérale
- Modification des quantités
- Calcul automatique du total
- Persistance en localStorage
- Validation du stock

### 🔐 Authentification
- Formulaires Login / Register
- Gestion JWT (access + refresh tokens)
- Déconnexion sécurisée
- Protection des routes

### 📦 Commandes
- Création de commande depuis le panier
- Historique des commandes
- Détail de chaque commande
- Statut de paiement

### 💳 Paiement Stripe
- Intégration Stripe Elements
- Formulaire de carte sécurisé
- Confirmation de paiement

### 🌐 API Externes
- Import de produits depuis FakeStore
- Convertisseur de devises

### 🔔 Notifications
- Toast messages (succès/erreur)
- Feedback utilisateur

---

## 🎯 Composants Principaux

### App.jsx
Composant racine gérant :
- État global (user, cart, products)
- Authentification
- Navigation
- Modales

### api.js
Client API avec :
- Gestion automatique des tokens JWT
- Refresh token automatique
- Gestion des erreurs
- Sanitization

```javascript
// Exemples d'utilisation
import { apiGet, apiPost, getProducts } from './api';

// GET simple
const products = await getProducts();

// GET authentifié
const profile = await apiGet('/api/auth/me/', token);

// POST authentifié
const order = await apiPost('/api/orders/', data, token);
```

---

## 🎨 Styles

L'application utilise du CSS personnalisé avec :
- Variables CSS pour les couleurs
- Design responsive (mobile-first)
- Animations et transitions
- Dark mode (optionnel)

### Classes principales

```css
.app              /* Container principal */
.header           /* Barre de navigation */
.products-grid    /* Grille de produits */
.product-card     /* Carte produit */
.cart-sidebar     /* Panier latéral */
.modal            /* Modales (auth, etc.) */
.toast            /* Notifications */
```

---

## 📱 Responsive Design

| Breakpoint | Comportement |
|------------|--------------|
| < 480px | Mobile - 1 colonne |
| 480-768px | Tablette - 2 colonnes |
| 768-1024px | Desktop - 3 colonnes |
| > 1024px | Large - 4 colonnes |

---

## 🧪 Tests

### Linting

```powershell
npm run lint
```

### Tests unitaires (à configurer)

```powershell
npm install -D vitest @testing-library/react
npm test
```

---

## 📝 Scripts disponibles

| Script | Description |
|--------|-------------|
| `npm run dev` | Développement avec HMR |
| `npm run build` | Build production |
| `npm run preview` | Prévisualiser le build |
| `npm run lint` | Vérifier le code |

---

## 📚 Documentation complémentaire

- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) - Documentation API
- [instruction.md](../instruction.md) - Guide d'installation
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
