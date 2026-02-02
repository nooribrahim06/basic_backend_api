from flask import Flask, request, jsonify
import sqlite3

DB_NAME = "Store.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    db = conn.cursor()

    db.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            category_id INTEGER
        )
    """)

    conn.commit()
    conn.close()

app = Flask(__name__)
init_db()

# ----------------------------
# Products CRUD
# JSON keys:
# POST  /api/products:  { "name": "...", "price": 123, "category_name": "..." }
# PATCH /api/products/: { "name": "...", "price": 123, "category_name": "..." } (any subset)
# ----------------------------

@app.route('/api/products', methods=["POST"])
def create_product():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    price = data.get("price")
    category_name = data.get("category_name")  # optional

    if name is None or price is None:
        return jsonify({"error": "name and price are required"}), 400

    conn = get_conn()
    db = conn.cursor()

    db.execute("""
        INSERT INTO Products (name, price, category_id)
        VALUES (?, ?, (SELECT id FROM Categories WHERE name = ?))
    """, (name, price, category_name))

    conn.commit()
    new_id = db.lastrowid
    conn.close()

    return jsonify({"message": "created", "id": new_id}), 201


@app.route('/api/products', methods=["GET"])
def get_all_products():
    conn = get_conn()
    db = conn.cursor()

    db.execute("""
        SELECT p.id, p.name, p.price, c.name AS category_name
        FROM Products p
        LEFT JOIN Categories c ON p.category_id = c.id
    """)
    rows = db.fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows]), 200


@app.route('/api/products/<int:id>', methods=["GET"])
def get_product(id):
    conn = get_conn()
    db = conn.cursor()

    db.execute("""
        SELECT p.id, p.name, p.price, c.name AS category_name, p.category_id
        FROM Products p
        LEFT JOIN Categories c ON p.category_id = c.id
        WHERE p.id = ?
    """, (id,))
    row = db.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Not Found"}), 404

    return jsonify(dict(row)), 200


@app.route('/api/products/<int:id>', methods=["DELETE"])
def delete_product(id):
    conn = get_conn()
    db = conn.cursor()

    db.execute("DELETE FROM Products WHERE id = ?", (id,))
    conn.commit()
    deleted = db.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Not Found"}), 404

    return jsonify({"message": "deleted"}), 200


@app.route('/api/products/<int:id>', methods=["PATCH"])
def update_product(id):
    data = request.get_json(silent=True) or {}
    new_name = data.get("name")
    new_price = data.get("price")
    new_category_name = data.get("category_name")

    if new_name is None and new_price is None and new_category_name is None:
        return jsonify({"error": "No fields to update"}), 400

    conn = get_conn()
    db = conn.cursor()

    if new_category_name is not None:
        db.execute("SELECT id FROM Categories WHERE name = ?", (new_category_name,))
        cat = db.fetchone()
        cat_id = cat["id"] if cat else None
    else:
        cat_id = None

    db.execute("""
        UPDATE Products
        SET
            name = COALESCE(?, name),
            price = COALESCE(?, price),
            category_id = COALESCE(?, category_id)
        WHERE id = ?
    """, (new_name, new_price, cat_id, id))

    conn.commit()
    updated = db.rowcount
    conn.close()

    if updated == 0:
        return jsonify({"error": "Not Found"}), 404

    return jsonify({"message": "updated"}), 200


# ----------------------------
# Categories CRUD
# JSON keys:
# POST/PATCH: { "name": "..." }
# ----------------------------

@app.route('/api/categories', methods=["POST"])
def create_category():
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_conn()
    db = conn.cursor()

    try:
        db.execute("INSERT INTO Categories (name) VALUES (?)", (name,))
        conn.commit()
        new_id = db.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Category already exists"}), 409

    conn.close()
    return jsonify({"message": "created", "id": new_id}), 201


@app.route('/api/categories', methods=["GET"])
def get_all_categories():
    conn = get_conn()
    db = conn.cursor()

    db.execute("SELECT id, name FROM Categories")
    rows = db.fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows]), 200


@app.route('/api/categories/<int:id>', methods=["GET"])
def get_category(id):
    conn = get_conn()
    db = conn.cursor()

    db.execute("SELECT id, name FROM Categories WHERE id = ?", (id,))
    row = db.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Not Found"}), 404

    return jsonify(dict(row)), 200


@app.route('/api/categories/<int:id>', methods=["DELETE"])
def delete_category(id):
    conn = get_conn()
    db = conn.cursor()

    db.execute("DELETE FROM Categories WHERE id = ?", (id,))
    conn.commit()
    deleted = db.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Not Found"}), 404

    return jsonify({"message": "deleted"}), 200


@app.route('/api/categories/<int:id>', methods=["PATCH"])
def update_category(id):
    data = request.get_json(silent=True) or {}
    new_name = data.get("name")

    if not new_name:
        return jsonify({"error": "name is required"}), 400

    conn = get_conn()
    db = conn.cursor()

    try:
        db.execute("""
            UPDATE Categories
            SET name = ?
            WHERE id = ?
        """, (new_name, id))
        conn.commit()
        updated = db.rowcount
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Category already exists"}), 409

    conn.close()

    if updated == 0:
        return jsonify({"error": "Not Found"}), 404

    return jsonify({"message": "updated"}), 200


if __name__ == "__main__":
    app.run(debug=True)
