# Flask Table Fetching API

Professional REST API for managing users, products, and orders.

## Features

- ✅ RESTful API with CRUD operations
- 📊 Pagination & filtering
- 🔒 CORS enabled
- 🗃️ SQLAlchemy ORM
- ⚡ SQLite database

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run
python app.py
```

Server runs at `http://localhost:5000`

## API Endpoints

### Tables
```
GET /api/tables          # List all tables
```

### Users
```
GET    /api/users        # List users
GET    /api/users/:id    # Get user
POST   /api/users        # Create user
```

### Products
```
GET    /api/products     # List products
GET    /api/products/:id # Get product
POST   /api/products     # Create product
```

### Orders
```
GET    /api/orders       # List orders
GET    /api/orders/:id   # Get order
POST   /api/orders       # Create order
```

## Examples

**Create User:**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com"}'
```

**Get Products (paginated):**
```bash
curl "http://localhost:5000/api/products?page=1&per_page=10"
```

**Filter by category:**
```bash
curl "http://localhost:5000/api/products?category=electronics"
```

## Tech Stack

- Flask 3.0
- Flask-SQLAlchemy 3.1
- Flask-CORS 4.0
- SQLite
