# E‑Commerce API

## Project Overview

A **FastAPI‑based** backend for an e‑commerce platform. It provides RESTful endpoints for authentication, user management, product catalog, categories, shopping cart, orders, wish‑list and payment processing. The API is built with **SQLAlchemy** for data persistence (SQLite in the repo, but can be swapped for any DB) and serves static files via FastAPI's `StaticFiles` mount.

---

## Tech Stack

- **Python 3.11** (or newer)
- **FastAPI** – high‑performance web framework
- **SQLAlchemy** – ORM for database interactions
- **SQLite** – default dev database (replaceable with PostgreSQL, MySQL, etc.)
- **Uvicorn** – ASGI server
- **Pydantic** – data validation & schema definitions
- **Docker** (optional, for containerised development)
- **Git** – version control

---

## Prerequisites

- **Python** >= 3.11
- **pip** (Python package manager)
- **Git**
- *(Optional)* **Docker** & **Docker Compose** for containerised setup

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/your‑org/ecommerce-api.git
cd ecommerce-api

# 2. Create a virtual environment (recommended)
python -m venv venv
# Activate the environment
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up the database (SQLite example)
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 5. Run the development server
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` in your browser. Swagger UI is available at `http://127.0.0.1:8000/docs`.

---

## Environment Variables

Create a `.env` file in the project root with:

```dotenv
DATABASE_URL=sqlite:///./ecommerce.db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,https://myfrontend.com
```

---

## Project Architecture

```
(ecommerce-api)/
│
├── app/
│   ├── main.py            # FastAPI app instance & router registration
│   ├── database.py        # SQLAlchemy engine & Base definition
│   ├── models/            # ORM model definitions
│   ├── schemas/           # Pydantic schemas
│   ├── routers/           # API route groups
│   ├── utils/             # Helper utilities
│   └── crud.py            # Core CRUD operations
│
├── uploads/               # Static uploads
├── requirements.txt       # Dependencies
├── test_api.py            # Tests
└── README.md              # <-- This file
```

---

## Running Tests

```bash
pytest test_api.py
```

---

## Contribution Guidelines

1. Fork the repository.
2. Create a feature branch.
3. Write clean code and tests.
4. Ensure tests pass.
5. Open a PR.

---

## License

MIT License – see `LICENSE`.
