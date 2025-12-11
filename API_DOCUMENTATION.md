# 📖 Documentation API - E-Commerce

Documentation complète de l'API REST du projet e-commerce.

**Base URL** : `http://localhost:8000`

---

## 📑 Table des matières

1. [Authentification](#1-authentification)
2. [Produits](#2-produits)
3. [Panier](#3-panier)
4. [Commandes](#4-commandes)
5. [Paiements](#5-paiements)
6. [API Externes](#6-api-externes)
7. [Codes d'erreur](#7-codes-derreur)

---

## 1. Authentification

### POST `/auth/register/`
Créer un nouveau compte utilisateur.

**Corps de la requête :**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Erreurs possibles :**
- `400` : Email déjà utilisé
- `400` : Mot de passe trop court

---

### POST `/auth/login/`
Connexion et obtention des tokens JWT.

**Corps de la requête :**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Réponse (200 OK) :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Erreurs possibles :**
- `401` : Identifiants incorrects
- `429` : Trop de tentatives (rate limiting)

---

### POST `/auth/token/refresh/`
Rafraîchir le token d'accès.

**Corps de la requête :**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse (200 OK) :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### GET `/auth/me/`
Obtenir le profil de l'utilisateur connecté.

**Headers :**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "is_staff": false,
  "date_joined": "2025-12-01T10:30:00Z"
}
```

---

## 2. Produits

### GET `/products/`
Liste de tous les produits.

**Paramètres de requête (optionnels) :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `search` | string | Recherche par nom |
| `min_price` | number | Prix minimum |
| `max_price` | number | Prix maximum |
| `in_stock` | boolean | Uniquement en stock |

**Réponse (200 OK) :**
```json
[
  {
    "id": 1,
    "title": "T-shirt Premium",
    "description": "T-shirt en coton bio",
    "price": "29.99",
    "stock": 50,
    "image": "https://example.com/image.jpg",
    "created_at": "2025-12-01T10:00:00Z"
  }
]
```

---

### GET `/products/{id}/`
Détails d'un produit spécifique.

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "title": "T-shirt Premium",
  "description": "T-shirt en coton bio de haute qualité...",
  "price": "29.99",
  "stock": 50,
  "image": "https://example.com/image.jpg",
  "created_at": "2025-12-01T10:00:00Z"
}
```

---

### POST `/products/` 🔒 Admin
Créer un nouveau produit.

**Headers :**
```
Authorization: Bearer <admin_access_token>
```

**Corps de la requête :**
```json
{
  "title": "Nouveau Produit",
  "description": "Description du produit",
  "price": 49.99,
  "stock": 100,
  "image": "https://example.com/image.jpg"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 2,
  "title": "Nouveau Produit",
  "description": "Description du produit",
  "price": "49.99",
  "stock": 100,
  "image": "https://example.com/image.jpg",
  "created_at": "2025-12-11T14:00:00Z"
}
```

---

### PUT `/products/{id}/` 🔒 Admin
Modifier un produit existant.

---

### DELETE `/products/{id}/` 🔒 Admin
Supprimer un produit.

---

## 3. Panier

### GET `/cart/` 🔒
Contenu du panier de l'utilisateur.

**Headers :**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK) :**
```json
[
  {
    "id": 1,
    "product": {
      "id": 1,
      "title": "T-shirt Premium",
      "price": "29.99",
      "image": "https://example.com/image.jpg"
    },
    "quantity": 2
  }
]
```

---

### POST `/cart/` 🔒
Ajouter un produit au panier.

**Corps de la requête :**
```json
{
  "product": 1,
  "quantity": 2
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "product": 1,
  "quantity": 2
}
```

---

### PUT `/cart/{id}/` 🔒
Modifier la quantité d'un article.

**Corps de la requête :**
```json
{
  "quantity": 3
}
```

---

### DELETE `/cart/{id}/` 🔒
Retirer un article du panier.

---

## 4. Commandes

### GET `/orders/` 🔒
Liste des commandes de l'utilisateur.

**Réponse (200 OK) :**
```json
[
  {
    "id": 1,
    "status": "pending",
    "total": "89.97",
    "created_at": "2025-12-11T15:00:00Z",
    "items_count": 3
  }
]
```

---

### POST `/orders/` 🔒
Créer une nouvelle commande.

**Corps de la requête :**
```json
{
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 3, "quantity": 1 }
  ]
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "status": "pending",
  "total": "89.97",
  "items": [
    {
      "product": { "id": 1, "title": "T-shirt Premium" },
      "quantity": 2,
      "price": "29.99"
    },
    {
      "product": { "id": 3, "title": "Jean Slim" },
      "quantity": 1,
      "price": "29.99"
    }
  ],
  "created_at": "2025-12-11T15:00:00Z"
}
```

**Notes :**
- Le stock est automatiquement décrémenté
- Transaction SQL pour garantir la cohérence
- Erreur 400 si stock insuffisant

---

### GET `/orders/{id}/` 🔒
Détails d'une commande spécifique.

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "status": "paid",
  "total": "89.97",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "title": "T-shirt Premium",
        "image": "https://example.com/image.jpg"
      },
      "quantity": 2,
      "price": "29.99"
    }
  ],
  "created_at": "2025-12-11T15:00:00Z",
  "updated_at": "2025-12-11T15:05:00Z"
}
```

---

## 5. Paiements

### POST `/payment/create-intent/` 🔒
Créer un Payment Intent Stripe.

**Corps de la requête :**
```json
{
  "order_id": 1
}
```

**Réponse (200 OK) :**
```json
{
  "client_secret": "pi_1234567890_secret_abcdefgh",
  "amount": 8997,
  "currency": "eur"
}
```

**Notes :**
- Le `client_secret` est utilisé côté frontend avec Stripe.js
- Le montant est en centimes

---

### POST `/payment/webhook/`
Webhook Stripe pour confirmer les paiements.

**Headers :**
```
Stripe-Signature: <signature>
```

**Notes :**
- Configuré dans le dashboard Stripe
- Met à jour le statut de la commande automatiquement

---

## 6. API Externes

### GET `/external/products/`
Récupérer des produits depuis FakeStore API.

**Réponse (200 OK) :**
```json
[
  {
    "id": 1,
    "title": "Fjallraven Backpack",
    "price": 109.95,
    "description": "Your perfect pack...",
    "category": "men's clothing",
    "image": "https://fakestoreapi.com/img/81..."
  }
]
```

---

### GET `/external/rates/`
Récupérer les taux de change.

**Paramètres de requête :**
| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `base` | string | Devise de base | EUR |

**Exemple :** `/external/rates/?base=USD`

**Réponse (200 OK) :**
```json
{
  "base": "EUR",
  "date": "2025-12-11",
  "rates": {
    "USD": 1.08,
    "GBP": 0.86,
    "JPY": 158.45,
    "CHF": 0.94
  }
}
```

**Devises supportées :**
EUR, USD, GBP, JPY, CHF, CAD, AUD, NZD, CNY, HKD, SGD, SEK, NOK, DKK, PLN, CZK, HUF, RON, BGN, TRY, ILS, ZAR, MXN, BRL, INR, KRW, THB, MYR, IDR, PHP, RUB

---

### GET `/health/`
Vérifier l'état de l'API.

**Réponse (200 OK) :**
```json
{
  "ok": true
}
```

---

## 7. Codes d'erreur

### Codes HTTP

| Code | Signification |
|------|---------------|
| `200` | Succès |
| `201` | Créé avec succès |
| `400` | Requête invalide |
| `401` | Non authentifié |
| `403` | Accès refusé |
| `404` | Ressource non trouvée |
| `429` | Trop de requêtes (rate limit) |
| `500` | Erreur serveur |
| `503` | Service indisponible |

### Format des erreurs

```json
{
  "detail": "Message d'erreur explicatif"
}
```

Ou pour les erreurs de validation :
```json
{
  "email": ["Ce champ est requis."],
  "password": ["Le mot de passe doit contenir au moins 8 caractères."]
}
```

---

## 🔐 Authentification

### Token JWT

Toutes les requêtes protégées (🔒) nécessitent un header :
```
Authorization: Bearer <access_token>
```

### Durée de vie des tokens
- **Access Token** : 30 minutes
- **Refresh Token** : 1 jour

### Rafraîchir le token
Quand l'access token expire, utilisez le refresh token :
```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

## 📊 Rate Limiting

| Type | Limite |
|------|--------|
| Anonyme | 30 req/min |
| Authentifié | 100 req/min |
| Login | 5 req/min |
| Register | 3 req/min |
| API Externes | 30 req/min |

---

## 🧪 Tester l'API

### Avec cURL

```bash
# Health check
curl http://localhost:8000/health/

# Register
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get products
curl http://localhost:8000/products/

# Get profile (authenticated)
curl http://localhost:8000/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Avec PowerShell

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health/"

# Login
$body = @{email="test@example.com"; password="password123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login/" -Method POST -Body $body -ContentType "application/json"
$token = $response.access

# Get profile
$headers = @{Authorization = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/auth/me/" -Headers $headers
```

---

## 📝 Notes

- Tous les prix sont en EUR
- Les montants Stripe sont en centimes
- Les dates sont au format ISO 8601
- L'API retourne du JSON uniquement
