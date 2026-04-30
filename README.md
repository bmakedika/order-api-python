# Order API

> Backoffice et API REST headless de gestion e-commerce — sécurisée, observable et orientée données.

[![CI](https://github.com/bmakedika/order-api/actions/workflows/tests.yml/badge.svg)](https://github.com/bmakedika/order-api/actions)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Vue d'ensemble

Order API est un backoffice REST construit avec **FastAPI**, **PostgreSQL** et **Redis**.  
Le projet couvre l'intégralité du cycle de vie d'une commande e-commerce : authentification, gestion des produits, commandes, paiements idempotents, facturation automatique et monitoring en temps réel.

Il est conçu selon les principes d'une API de production :

- Architecture en couches (API → Middlewares → Services → Repository)
- Contrôle d'accès basé sur les rôles (RBAC) — `user` et `admin`
- Observabilité intégrée — métriques Prometheus, dashboards Grafana
- Qualité assurée — 25 tests automatisés, CI GitHub Actions sur chaque push

**Docs interactives :** `http://localhost:8000/docs`  
**Métriques :** `http://localhost:8000/metrics`  
**Grafana :** `http://localhost:3001`  
**Prometheus :** `http://localhost:9090`

---

## Fonctionnalités

### Authentification & sécurité

- JWT Bearer — access token + refresh token avec rotation
- Blacklist des tokens révoqués via Redis
- Contrôle d'accès par rôle (`require_role()`) — user et admin
- Rate limiting par IP et par famille de routes

### Catalogue produits

- CRUD complet réservé aux admins (POST / PATCH / DELETE)
- Consultation publique sans authentification (GET)
- Pagination, filtres et tri

### Commandes

- Cycle de vie complet : draft → items → paiement → livraison
- Filtrage par utilisateur connecté — un user ne voit que ses commandes
- Mise à jour de statut réservée aux admins

### Paiements

- Paiement idempotent via header `Idempotency-Key` (cache Redis 24h)
- Facturation automatique à chaque paiement validé
- Zéro double débit garanti

### Observabilité

- Endpoint `/metrics` exposé pour Prometheus
- Métriques HTTP : `http_requests_total`, `http_request_duration_seconds`
- Dashboard Grafana auto-provisionné au démarrage : latency p95, RPS, error rate

### Qualité & CI

- 25 tests pytest (auth, orders, products, invoices, RBAC)
- Base SQLite en mémoire pour les tests — isolation totale
- GitHub Actions — pipeline CI sur chaque push

---

## Stack technique

| Technologie        | Rôle                          | Pourquoi ce choix                                                  |
| ------------------ | ----------------------------- | ------------------------------------------------------------------ |
| **FastAPI**        | Framework API REST            | Performance async, validation Pydantic native, Swagger auto-généré |
| **PostgreSQL 15**  | Base de données relationnelle | Fiabilité, transactions ACID, support UUID natif                   |
| **SQLAlchemy 2**   | ORM                           | Abstraction de la DB, pattern Repository facilité                  |
| **Alembic**        | Migrations de schéma          | Versioning des changements de DB, rollback possible                |
| **Redis 7**        | Cache multi-usage             | Idempotency des paiements, blacklist JWT, rate limiting            |
| **Prometheus**     | Collecte de métriques         | Standard industrie, scrape toutes les 5s                           |
| **Grafana 11**     | Dashboards                    | Provisioning automatique via fichiers JSON                         |
| **Docker Compose** | Orchestration locale          | Reproductibilité de l'environnement en une commande                |
| **pytest**         | Tests automatisés             | Fixtures isolées, mode strict asyncio                              |
| **GitHub Actions** | CI/CD                         | Pipeline automatique sur chaque push vers `main`                   |

---

## Architecture

```
order-api-python/
├── app/
│   ├── api/                  # Endpoints REST (auth, products, orders, invoices, users)
│   ├── core/
│   │   ├── auth.py           # JWT, require_role(), backward-compatible aliases
│   │   ├── config.py         # Variables d'environnement (pydantic-settings)
│   │   ├── database.py       # Engine SQLAlchemy, SessionLocal
│   │   ├── redis_client.py   # Client Redis partagé
│   │   ├── token_blacklist.py
│   │   ├── metrics/
│   │   │   └── prometheus.py # Middleware + endpoint /metrics
│   │   └── middlewares/
│   │       ├── audit.py      # Log CSV de chaque requête
│   │       ├── cors.py       # CORS middleware
│   │       └── rate_limit.py # Rate limiting par IP
│   ├── models/               # Modèles SQLAlchemy
│   ├── repos/                # Couche Repository — requêtes DB
│   ├── schemas/              # Schémas Pydantic (request / response)
│   └── services/             # Logique métier
├── monitoring/
│   ├── prometheus.yml        # Config scrape Prometheus
│   └── grafana/
│       ├── provisioning/     # Datasource + dashboard provider
│       └── dashboards/       # Dashboard Order API (JSON)
├── tests/                    # Suite de tests pytest
├── docker-compose.yml        # PostgreSQL + Redis
├── docker-compose.monitoring.yml  # Prometheus + Grafana
└── alembic/                  # Migrations de schéma
```

---

## Démarrage rapide

### Prérequis

- Python 3.11+
- Docker Desktop
- Git

### 1. Cloner le dépôt

```bash
git clone https://github.com/bmakedika/order-api.git
cd order-api-python
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

> **Conseil :** Utilisez un mot de passe sans caractères spéciaux dans `POSTGRES_PASSWORD` et `DATABASE_URL` pour éviter les problèmes d'encodage URL.

### 5. Démarrer l'infrastructure

```bash
docker compose up -d
```

### 6. Appliquer les migrations

```bash
alembic upgrade head
```

> Si les migrations échouent (volume Docker avec d'anciens credentials) :
>
> ```bash
> docker compose down -v
> docker compose up -d
> alembic upgrade head
> ```
>
> ⚠️ Cette commande supprime toutes les données existantes.

### 7. Lancer l'API

```bash
uvicorn app.main:app --reload --env-file .env
```

L'API est disponible sur `http://localhost:8000/docs`

---

## Monitoring (optionnel)

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

| Service       | URL                             | Credentials   |
| ------------- | ------------------------------- | ------------- |
| Grafana       | `http://localhost:3001`         | admin / admin |
| Prometheus    | `http://localhost:9090`         | —             |
| Métriques API | `http://localhost:8000/metrics` | —             |

Le dashboard **Order API — Overview** se charge automatiquement dans Grafana (provisioning).

---

## Endpoints

### Authentification

| Méthode | Endpoint         | Description               | Auth           |
| ------- | ---------------- | ------------------------- | -------------- |
| POST    | `/auth/register` | Créer un compte           | —              |
| POST    | `/auth/login`    | Obtenir les tokens JWT    | —              |
| POST    | `/auth/refresh`  | Renouveler l'access token | Cookie refresh |
| POST    | `/auth/logout`   | Révoquer les tokens       | Bearer         |

### Produits

| Méthode | Endpoint         | Description          | Auth  |
| ------- | ---------------- | -------------------- | ----- |
| GET     | `/products`      | Lister les produits  | —     |
| GET     | `/products/{id}` | Détail d'un produit  | —     |
| POST    | `/products`      | Créer un produit     | admin |
| PATCH   | `/products/{id}` | Modifier un produit  | admin |
| DELETE  | `/products/{id}` | Supprimer un produit | admin |

### Commandes

| Méthode | Endpoint                       | Description                | Auth                |
| ------- | ------------------------------ | -------------------------- | ------------------- |
| POST    | `/orders`                      | Créer une commande (draft) | user                |
| GET     | `/orders/{id}`                 | Détail d'une commande      | user (propriétaire) |
| POST    | `/orders/{id}/items`           | Ajouter un article         | user                |
| DELETE  | `/orders/{id}/items/{item_id}` | Retirer un article         | user                |
| POST    | `/orders/{id}/pay`             | Payer (idempotent)         | user                |
| PATCH   | `/orders/{id}/status`          | Mettre à jour le statut    | admin               |

### Factures

| Méthode | Endpoint                | Description             | Auth                |
| ------- | ----------------------- | ----------------------- | ------------------- |
| GET     | `/invoices/{id}`        | Détail d'une facture    | user (propriétaire) |
| GET     | `/orders/{id}/invoices` | Factures d'une commande | user (propriétaire) |

### Utilisateur

| Méthode | Endpoint    | Description                      | Auth |
| ------- | ----------- | -------------------------------- | ---- |
| GET     | `/users/me` | Profil de l'utilisateur connecté | user |

---

## Authentification — exemple curl

```bash
# 1. Créer un compte
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'

# 2. Se connecter
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret123"}'

# 3. Utiliser le token
curl http://localhost:8000/orders \
  -H "Authorization: Bearer <access_token>"
```

---

## Paiement idempotent — exemple curl

```bash
curl -X POST http://localhost:8000/orders/{id}/pay \
  -H "Authorization: Bearer <access_token>" \
  -H "Idempotency-Key: commande-001-tentative-1"
```

Appeler `/pay` plusieurs fois avec la même clé retourne toujours la même réponse sans re-débiter.

---

## Tests

```bash
# Lancer tous les tests
pytest -v

# Avec couverture
pytest --cov=app --cov-report=term-missing
```

La suite de tests utilise une base SQLite en mémoire et un Redis isolé (flushdb avant chaque test). Aucune dépendance à l'infrastructure Docker.

---

## Commandes utiles

```bash
# Redémarrer l'infrastructure
docker compose down && docker compose up -d

# Créer une nouvelle migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Rollback d'une migration
alembic downgrade -1

# Lancer les tests en mode verbose
pytest -v

# Vérifier le linting
ruff check app/
```

---

## Roadmap

| Horizon           | Fonctionnalités                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| **À court terme** | Exports CSV/Excel (admin) · Dashboards métier Grafana · Script KPI automatisé (APScheduler)          |
| **À moyen terme** | Déploiement cloud (Railway/Render) · Intégration paiement réel (Stripe) · Documentation API enrichie |
| **À long terme**  | Multi-tenant · Publication open source · Métriques métier avancées                                   |

---

## Licence

MIT — voir [LICENSE](LICENSE)

---

_Projet académique — Prépa Master Digital · Bienvenu MAKEDIKA · 2026_  
_[github.com/bmakedika/order-api](https://github.com/bmakedika/order-api)_
