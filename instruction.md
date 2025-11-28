# Instructions - Projet e-commerce (React + Node.js + MySQL)

Ce document décrit les étapes d'initialisation et d'exécution du projet en utilisant :
- Frontend : React
- Backend : Node.js + Express
- Base de données : MySQL

## Prérequis
- Node.js (v16+ recommandé)
- npm ou yarn
- MySQL (local) ou accès à une instance distante
- Git (optionnel)
- PowerShell (Windows) — commandes fournies pour PowerShell

## Arborescence recommandée

- /backend   -> code Node.js / Express
- /frontend  -> code React
- /db        -> scripts SQL (migrations / seed)
- .env       -> variables d'environnement (backend)

## Backend (Node.js + Express)

1) Initialiser le projet backend

PowerShell:

```powershell
cd C:\Users\natha\OneDrive\ING2\test aapi
mkdir backend; cd backend
npm init -y
```

2) Installer les dépendances courantes

```powershell
npm install express dotenv mysql2 sequelize sequelize-cli
npm install --save-dev nodemon
```

3) Exemples de scripts `package.json`

Ajouter dans `package.json` (backend) :

```json
"scripts": {
  "start": "node src/index.js",
  "dev": "nodemon src/index.js"
}
```

4) Exemple minimal `src/index.js`

- Créez `src/index.js` et chargez les variables d'environnement :

```js
require('dotenv').config();
const express = require('express');
const app = express();
app.use(express.json());

app.get('/api/health', (req, res) => res.json({ok: true}));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server listening on ${PORT}`));
```

5) Configuration de la base MySQL

- Créer une base de données via MySQL Workbench ou en ligne de commande.
- Exemple de `.env` (backend) :

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=motdepasse
DB_NAME=ecommerce_db
PORT=5000
JWT_SECRET=une_chaine_secrete
```

6) Exemple simple de script SQL (créer tables de base)

Fichier `db/schema.sql` :

```sql
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  stock INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Executez ce fichier SQL avec MySQL Workbench ou :

```powershell
mysql -u root -p < .\\db\\schema.sql
```

(Remplacez `root` et fournissez le mot de passe)

## Frontend (React)

1) Créer l'application React (create-react-app) :

```powershell
cd C:\Users\natha\OneDrive\ING2\test aapi
npx create-react-app frontend
cd frontend
npm start
```

2) Configuration pour dev local :
- Option 1 : ajouter dans `frontend/package.json` la propriété `proxy` pour rediriger les requêtes API vers le backend en dev :

```json
"proxy": "http://localhost:5000"
```

- Option 2 : configurer CORS côté backend (recommandé pour plus de contrôle) :

```powershell
npm install cors
```

Puis dans `src/index.js` du backend :

```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000' }));
```

## Commandes utiles (PowerShell)

- Lancer le backend en développement :

```powershell
cd backend
npm run dev
```

- Lancer le frontend en développement :

```powershell
cd frontend
npm start
```

- Construire le frontend pour la production :

```powershell
cd frontend
npm run build
```

- Exécuter le script SQL pour initialiser la BDD :

```powershell
mysql -u <user> -p < .\\db\\schema.sql
```

## Intégration API / Exemple d'appel

- Exemple fetch depuis React :

```js
fetch('/api/products')
  .then(r => r.json())
  .then(data => console.log(data));
```

(Si vous n'utilisez pas `proxy`, utilisez l'URL complète `http://localhost:5000/api/products`)

## Tests rapides et vérifications

- Backend : visiter `http://localhost:5000/api/health` doit renvoyer `{ok:true}`
- Frontend : l'application React doit démarrer sur `http://localhost:3000`
- DB : se connecter et vérifier que la base `ecommerce_db` et les tables existent

## Bonnes pratiques & prochaines étapes

- Utiliser un ORM (Sequelize ou Prisma) pour gérer les migrations et modèles.
- Ajouter l'authentification (JWT) et le hashing des mots de passe (bcrypt).
- Ajouter des tests unitaires et d'intégration (Jest, supertest).
- Versionner le projet avec Git et ajouter un README détaillé.

---

Si tu veux, je peux :
- créer automatiquement la structure de dossiers (`backend`, `frontend`, `db`) et ajouter les fichiers de démarrage (index.js, package.json modifié),
- générer un fichier `.env.example` et `db/schema.sql` dans le dossier `db`,
- ou adapter ces instructions pour utiliser Vite/Prisma/Docker selon ta préférence.

Dis-moi ce que tu veux que je fasse ensuite.