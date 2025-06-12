# E-commerce Backend API using FastAPI

## Folder Structure

```
project-root/
├── app/
│   ├── main.py
│   ├── core/          # DB + settings
│   ├── auth/          # Auth logic
│   ├── products/
│   ├── cart/
│   ├── orders/
│   └── ...
├── alembic/           # Migrations
├── .env
└── README.md
```

## Setup Instructions

### 1. Initialize local repository

```bash
git init
```

### 2. Create and activate a virtual environment

```bash
python -m venv fastapi-env
source fastapi-env/bin/activate
```

### 3. Install required packages

```bash
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic \
    python-jose[cryptography] passlib[bcrypt] python-multipart \
    pydantic-settings python-dotenv
```

### 4. Create a `.env` file in the root folder

```ini
# .env
DATABASE_URL=postgresql+psycopg2://postgres:<your_password>@localhost:5432/ecommerce_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Initialize and run Alembic migrations

```bash
alembic init alembic
# Edit alembic.ini and alembic/env.py as per needs
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Run the development server

```bash
uvicorn app.main:app --reload
```

Visit:
- `http://127.0.0.1:8000` – Test root
- `http://127.0.0.1:8000/docs` – Swagger UI
- `http://127.0.0.1:8000/redoc` – ReDoc

---

## API Endpoints Overview

| Method | Endpoint                           | Description                           |
|--------|------------------------------------|---------------------------------------|
| POST   | /auth/signup                       | User registration                     |
| POST   | /auth/signin                       | User login                            |
| POST   | /auth/forgot-password              | Forgot login password                 |
| POST   | /auth/reset-password               | Reset login password                  |
| GET    | /products                          | Public product listing                |
| GET    | /products/{product_id}             | Public product details                |
| GET    | /products/search                   | Public product search by keyword      |
| POST   | /admin/products                    | Admin: create product                 |
| GET    | /admin/products                    | Admin: get all products               |
| GET    | /admin/products/{product_id}       | Admin: get product details            |
| PUT    | /admin/products/{product_id}       | Admin: update product                 |
| DELETE | /admin/products/{product_id}       | Admin: delete product                 |
| POST   | /cart                              | User: Add product to cart             |
| GET    | /cart/{product_id}                 | User: get all products                |
| PUT    | /cart/{product_id}                 | User: update product quantity         |
| DELETE | /cart/{product_id}                 | User: delete product                  |
| POST   | /checkout                          | User: Simulate checkout               |
| GET    | /orders                            | User: View user order history         |
| GET    | /orders/{order_id}                 | User: View user order details         |

---

## Testing API

Use **Postman** or built-in Swagger UI:
```bash
http://127.0.0.1:8000/docs
```

---

## Author

> Project developed as part of training by `Yashvi Mudgal`
