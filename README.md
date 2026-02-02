# Store Backend API (Flask + SQLite)

A simple REST API for managing **Products** and **Categories** using **Flask** and **SQLite**.  
Includes full CRUD operations and returns JSON responses with proper HTTP status codes.

## Tech Stack
- Python 3.x
- Flask
- SQLite (via Python `sqlite3`)

## Project Structure
```

.
├── app.py
└── Store.db          # created automatically on first run

````

## Setup & Run

### 1) Create and activate a virtual environment (recommended)
Windows (PowerShell):
```bash
python -m venv .venv
.venv\Scripts\activate
````

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install flask
```

### 3) Run the server

```bash
python app.py
```

Server will start at:

* `http://127.0.0.1:5000`

> The database file `Store.db` is created automatically on first run.

## API Endpoints

### Categories

| Method | Endpoint               | Description          |
| ------ | ---------------------- | -------------------- |
| POST   | `/api/categories`      | Create category      |
| GET    | `/api/categories`      | List categories      |
| GET    | `/api/categories/<id>` | Get category by id   |
| PATCH  | `/api/categories/<id>` | Update category name |
| DELETE | `/api/categories/<id>` | Delete category      |

### Products

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| POST   | `/api/products`      | Create product           |
| GET    | `/api/products`      | List products            |
| GET    | `/api/products/<id>` | Get product by id        |
| PATCH  | `/api/products/<id>` | Update product (partial) |
| DELETE | `/api/products/<id>` | Delete product           |

## Request/Response Examples

### Create a category

**POST** `/api/categories`

```json
{
  "name": "Tech"
}
```

Success (201):

```json
{
  "message": "created",
  "id": 1
}
```

Duplicate name (409):

```json
{
  "error": "Category already exists"
}
```

---

### Create a product

**POST** `/api/products`

```json
{
  "name": "Laptop",
  "price": 15000,
  "category_name": "Tech"
}
```

Success (201):

```json
{
  "message": "created",
  "id": 1
}
```

Notes:

* `category_name` is optional.
* If `category_name` does not exist, product is created with `category_id = null`.

---

### List products

**GET** `/api/products`

Example response (200):

```json
[
  {
    "id": 1,
    "name": "Laptop",
    "price": 15000,
    "category_name": "Tech"
  }
]
```

---

### Update product (PATCH)

**PATCH** `/api/products/1`

Update only the price:

```json
{
  "price": 16000
}
```

Success (200):

```json
{
  "message": "updated"
}
```

If no fields provided (400):

```json
{
  "error": "No fields to update"
}
```

---

### Delete product

**DELETE** `/api/products/1`

Success (200):

```json
{
  "message": "deleted"
}
```

Not found (404):

```json
{
  "error": "Not Found"
}
```

## Testing The API 

### Using curl

Create category:

```bash
curl -X POST http://127.0.0.1:5000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"Tech"}'
```

Create product:

```bash
curl -X POST http://127.0.0.1:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":15000,"category_name":"Tech"}'
```

List products:

```bash
curl http://127.0.0.1:5000/api/products
```

## Status Codes Used

* `200 OK` — successful GET, PATCH, DELETE
* `201 Created` — successful POST
* `400 Bad Request` — missing/invalid input
* `404 Not Found` — resource does not exist
* `409 Conflict` — unique constraint violation (duplicate category name)

## Notes

* This project uses SQLite for simplicity and stores data in `Store.db`.
* Debug mode is enabled by default for development (`debug=True`).

