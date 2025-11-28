# Phase 1 - Authentification, Commandes et Paiement

## Nouvelles fonctionnalités

### 1. Authentification JWT
- **POST /api/auth/register** - Inscription (email, password, name)
- **POST /api/auth/login** - Connexion (retourne un token JWT)
- **GET /api/auth/me** - Profil utilisateur (protégé par token)

### 2. Gestion des commandes
- **POST /api/orders** - Créer une commande (protégé)
  - Vérifie le stock
  - Calcule le total
  - Décrémente automatiquement le stock
  - Utilise des transactions SQL
- **GET /api/orders** - Liste des commandes de l'utilisateur
- **GET /api/orders/:id** - Détail d'une commande

### 3. Paiement Stripe
- **POST /api/payment/create-intent** - Créer un Payment Intent
- **POST /api/payment/webhook** - Webhook Stripe (confirme le paiement)
- **POST /api/payment/confirm** - Confirmation manuelle (dev uniquement)

### 4. Base de données
- Table `order_items` ajoutée (relation commandes ↔ produits)
- Colonne `role` ajoutée à la table `users` (user/admin)

## Configuration requise

### Variables d'environnement (.env)
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=ecommerce_db
PORT=5000
JWT_SECRET=changez_moi_en_production
STRIPE_SECRET_KEY=sk_test_votre_cle_stripe
STRIPE_WEBHOOK_SECRET=whsec_votre_webhook_secret
```

### Mettre à jour la base de données
```powershell
cd 'C:\Program Files\MySQL\MySQL Server 8.0\bin'
.\mysql -u root -p -e "source C:\Users\natha\OneDrive\ING2\test aapi\db\schema.sql"
```

## Test des endpoints

### 1. Inscription
```bash
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123",
  "name": "Test User"
}
```

### 2. Connexion
```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```
Retourne : `{ "token": "...", "user": {...} }`

### 3. Créer une commande (avec token)
```bash
POST http://localhost:5000/api/orders
Authorization: Bearer VOTRE_TOKEN
Content-Type: application/json

{
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 2, "quantity": 1 }
  ]
}
```

### 4. Créer un Payment Intent
```bash
POST http://localhost:5000/api/payment/create-intent
Authorization: Bearer VOTRE_TOKEN
Content-Type: application/json

{
  "order_id": 1
}
```

### 5. Profil utilisateur
```bash
GET http://localhost:5000/api/auth/me
Authorization: Bearer VOTRE_TOKEN
```

## Sécurité

- Mots de passe hashés avec bcrypt (10 rounds)
- Tokens JWT avec expiration (7 jours)
- Middleware de protection des routes
- Validation des données avec Joi
- Transactions SQL pour les commandes (intégrité des données)

## Prochaines étapes (Phase 2)

- CRUD produits protégé admin
- Pagination et filtres
- Frontend : routing, state management, formulaires
- Upload d'images produits
- Tests et documentation Swagger
