# Restaurant API Backend

Ce projet fournit un backend FastAPI complet pour un système de gestion de restaurant, incluant la gestion des produits, catégories, suppléments, options, et un système de commande robuste avec calcul des frais de livraison et gestion des statuts.

## Fonctionnalités

- **Gestion des entités** : Catégories, Produits, Suppléments, Options, Choix d'Options, Commandes, Articles de Commande.
- **API RESTful** : Endpoints CRUD complets pour toutes les entités, sous `/api`.
- **Calcul des commandes** : Calcul côté serveur du coût des articles (avec options et suppléments) et du total de la commande.
- **Frais de livraison dynamiques** : Calcul basés sur la distance (formule Haversine) entre le restaurant et l'adresse du client, avec géocodage via Nominatim si les coordonnées ne sont pas fournies.
- **Snapshots** : Les détails des produits, choix et suppléments sont stockés au moment de la commande pour garantir l'immutabilité historique.
- **Endpoints Admin** : Les opérations sensibles (création/mise à jour/suppression de données de menu, lecture/mise à jour du statut des commandes) sont protégées par un token d'administration.
- **Documentation API** : Génération automatique de la documentation OpenAPI (Swagger UI et ReDoc).
- **CORS** : Activé pour toutes les origines, permettant l'intégration avec n'importe quel frontend.
- **Configuration** : Utilisation de variables d'environnement pour la configuration sensible.
- **Migrations de base de données** : Configuration de base avec Alembic.
- **Script Seeder** : Pour peupler la base de données avec des données d'exemple.

## Tech Stack

- **Langage** : Python 3.11+
- **Framework** : FastAPI
- **Base de données** : PostgreSQL (via `asyncpg` et SQLAlchemy 2.0)
- **ORM** : SQLAlchemy (mode asynchrone)
- **Migrations** : Alembic
- **Configuration** : `python-dotenv`, `pydantic-settings`
- **Géocodage/Distance** : `httpx` (pour Nominatim), `geopy` (pour Haversine)

## Installation et Lancement

### Prérequis

- Python 3.11+
- PostgreSQL (local ou Docker)

### Étapes

1.  **Cloner le dépôt** (si applicable) ou naviguer vers le dossier `backend`.

2.  **Créer un environnement virtuel** et activer :
    ```bash
    python -m venv venv
    # Sur Windows
    .\venv\Scripts\activate
    # Sur macOS/Linux
    source venv/bin/activate
    ```

3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurer les variables d'environnement** :
    Créez un fichier `.env` à la racine du dossier `backend` en vous basant sur `.env.example` :
    ```
    DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/restaurant_db"
    ADMIN_TOKEN="your_super_secret_admin_token"
    RESTAURANT_LAT=43.610769
    RESTAURANT_LNG=3.876716
    DELIVERY_BASE_FEE=2.0
    DELIVERY_PER_KM_FEE=1.0
    ```
    *Assurez-vous que `DATABASE_URL` pointe vers votre instance PostgreSQL.*

5.  **Initialiser et exécuter les migrations de base de données** :
    *   Initialiser Alembic (une seule fois, si ce n'est pas déjà fait) :
        ```bash
        alembic init alembic
        ```
        *(Note: Le fichier `alembic/env.py` et `alembic.ini` sont déjà fournis dans le projet.)*
    *   Générer la première migration (après avoir configuré `DATABASE_URL` et créé les modèles) :
        ```bash
        alembic revision --autogenerate -m "Initial database setup"
        ```
    *   Appliquer les migrations à la base de données :
        ```bash
        alembic upgrade head
        ```
    *(Alternativement, pour le développement initial, les tables seront créées automatiquement au démarrage de l'application si elles n'existent pas, grâce à `@app.on_event("startup")` dans `main.py`.)*

6.  **Exécuter le script seeder** (pour peupler la base de données avec des données d'exemple) :
    ```bash
    python seed_menu.py
    ```

7.  **Lancer le serveur FastAPI** :
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    Le serveur sera accessible à `http://localhost:8000`.

## Utilisation de l'API

La documentation interactive de l'API est disponible via Swagger UI et ReDoc :
- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

### Exemple de création de commande (`POST /api/orders`)

Pour créer une commande, envoyez une requête `POST` à `http://localhost:8000/api/orders` avec un corps JSON similaire à celui-ci :

```json
{
  "name": "Alice Dupont",
  "address": "12 rue de la République, 34000 Montpellier",
  "phone": "0601020304",
  "delivery_mode": "maison",
  "payment_mode": "cb",
  "latitude": 43.610769,          
  "longitude": 3.876716,
  "fee": 3.5,                     
  "items": [
    {
      "product_id": 1,
      "quantity": 1,
      "choices": [
        { "option_id": 1, "choice_id": 3 },
        { "option_id": 2, "choice_id": 4 }
      ],
      "supplements": [5]
    },
    {
      "product_id": 3,
      "quantity": 2,
      "choices": [
        { "option_id": 4, "choice_id": 7 }
      ],
      "supplements": []
    }
  ]
}
```
*(Les IDs des produits, options, choix et suppléments doivent correspondre à ceux existant dans votre base de données, créés par le seeder ou via les endpoints CRUD.)*

### Endpoints Admin

Les endpoints nécessitant une authentification admin (POST/PUT/DELETE pour les entités de menu, GET/PATCH pour les commandes) requièrent un en-tête `X-Admin-Token` avec la valeur définie dans votre fichier `.env`.

Exemple avec `curl` :
```bash
curl -X GET "http://localhost:8000/api/orders" \
     -H "X-Admin-Token: your_super_secret_admin_token"
```

## Structure du Projet

```
backend/
├── .env.example
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── core/
│   ├── config.py
│   └── security.py
├── crud/
│   ├── base.py
│   └── crud_operations.py
├── database/
│   ├── base.py
│   └── session.py
├── models/
│   ├── __init__.py
│   └── models.py
├── schemas/
│   ├── __init__.py
│   └── schemas.py
├── api/
│   ├── __init__.py
│   ├── deps.py
│   └── routers/
│       ├── __init__.py
│       ├── categories.py
│       ├── products.py
│       ├── supplements.py
│       ├── options.py
│       ├── choice_options.py
│       └── orders.py
├── main.py
├── requirements.txt
├── README.md
└── seed_menu.py
```

## Point d'Intégration Uber Eats

Un point d'intégration pour l'API Uber Eats est préparé dans la logique de création de commande. Vous pouvez ajouter votre logique d'intégration dans la méthode `create` de `CRUDOrder` après la création de la commande :

```python
# TODO: Future Uber Eats integration point
# if db_order.delivery_mode == DeliveryMode.ubereats:
#     await send_order_to_uber_eats(db_order)
```