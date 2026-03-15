# Order API

A production-like REST API built with FastAPI, PostgreSQL, and Redis.  
Designed as a portfolio project showcasing clean architecture, JWT authentication, and idempotent payments.

---

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — persistent database
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **Redis** — idempotency key storage
- **Docker** — containerized services
- **pytest** — automated tests

---

## Project Structure

```
app/
├── api/          # endpoints (products, orders, auth)
├── core/         # config, auth, security, database, redis
├── models/       # SQLAlchemy models
├── repos/        # database queries (repository pattern)
├── schemas/      # Pydantic schemas
├── services/     # business logic
└── storage/      # legacy fake DB (replaced by PostgreSQL)
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bmakedika/order-api-python.git
cd order-api-python
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

> **Note (Linux/WSL):** Replace `localhost` with `127.0.0.1` in `DATABASE_URL`.
> If your password contains special characters (e.g. `@`), encode them in the URL:
> `@` → `%40`, `!` → `%21`

### 5. Start Docker services

```bash
docker-compose up -d
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn app.main:app --reload --env-file .env
```

Visit **http://127.0.0.1:8000/docs** for the Swagger UI.

---

## API Endpoints

### Auth

| Method | Endpoint      | Description   |
| ------ | ------------- | ------------- |
| POST   | `/auth/login` | Get JWT token |

### Products

| Method | Endpoint         | Description                               | Auth  |
| ------ | ---------------- | ----------------------------------------- | ----- |
| GET    | `/products`      | List products (pagination, filters, sort) | —     |
| GET    | `/products/{id}` | Get product by ID                         | —     |
| POST   | `/products`      | Create product                            | admin |
| PATCH  | `/products/{id}` | Update product                            | admin |
| DELETE | `/products/{id}` | Soft delete product                       | admin |

### Orders

| Method | Endpoint                       | Description            | Auth |
| ------ | ------------------------------ | ---------------------- | ---- |
| POST   | `/orders`                      | Create order (draft)   | user |
| GET    | `/orders/{id}`                 | Get order details      | user |
| POST   | `/orders/{id}/items`           | Add item to order      | user |
| DELETE | `/orders/{id}/items/{item_id}` | Remove item            | user |
| POST   | `/orders/{id}/pay`             | Pay order (idempotent) | user |

---

## Authentication

The API uses **JWT Bearer tokens**.

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin-secret"}'

# 2. Use the token
curl http://localhost:8000/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Mock credentials:**

| Username | Password     | Role  |
| -------- | ------------ | ----- |
| admin    | admin-secret | admin |
| user     | user-secret  | user  |

---

## Idempotent Payments

The `/pay` endpoint uses an `Idempotency-Key` header to prevent double charges.

```bash
curl -X POST http://localhost:8000/orders/{id}/pay \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Idempotency-Key: unique-key-per-attempt"
```

Calling `/pay` multiple times with the same key returns the same response without re-charging.

---

## Running Tests

```bash
pytest -v
```

Expected output: **12 passed**

---

## License

MIT
