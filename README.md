# E-commerce Backend API using FastAPI

A secure, scalable, and modular RESTful API for managing products, users, carts, and orders using **FastAPI**, **PostgreSQL**, and **SQLAlchemy**.

---

## Features

- User authentication (JWT-based)
- Admin product management (CRUD)
- Public product listing and search
- Cart operations (add, update, remove)
- Dummy checkout and order tracking
- Role-based access control
- Swagger/OpenAPI docs
- PostgreSQL support

---

## Tech Stack

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Pydantic v2 + pydantic-settings
- Uvicorn
- Passlib (for password hashing)
- JWT (python-jose)

---

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
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv fastapi-env
fastapi-env\Scripts\activate

# macOS/Linux
python3 -m venv fastapi-env
source fastapi-env/bin/activate
```

### 3. Install required packages

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet, run:

```bash
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic \
    python-jose[cryptography] passlib[bcrypt] python-multipart \
    pydantic-settings python-dotenv
pip freeze > requirements.txt
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
# Edit alembic.ini and alembic/env.py as per your database.py
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

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| POST   | /auth/signup          | User registration              |
| POST   | /auth/signin          | User login                     |
| GET    | /products             | Public product listing         |
| POST   | /admin/products       | Admin: create product          |
| POST   | /cart                 | Add product to cart            |
| POST   | /checkout             | Simulate checkout              |
| GET    | /orders               | View user order history        |

(See full details in Swagger UI)

---

## Security Features

- JWT authentication (access + refresh)
- Password hashing using bcrypt
- Role-based access (admin/user)
- Secure token-based password reset (optional)

---

## Testing API

Use **Postman** or built-in Swagger UI:
```bash
http://127.0.0.1:8000/docs
```

---

## Code Quality & Linting

Install dev tools:

```bash
pip install black flake8 isort
```

Run:

```bash
black .
flake8 .
```

---

## Author

> Project developed as part of training by `Yashvi Mudgal`

---

## License

This project is for educational and demonstration purposes.