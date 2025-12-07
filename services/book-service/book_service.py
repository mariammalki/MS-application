from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# --- Configuration DB ---
DB_HOST = os.getenv("DB_HOST", "bookstore_db")  # Nom du service DB dans Docker Compose
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bookstore_db")
DB_USER = os.getenv("DB_USER", "bookstore_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bookstore_password")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# --- Health check ---
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# --- CRUD Routes ---

# Lister tous les livres
@app.route('/books', methods=['GET'])
def list_books():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, price, stock FROM books ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        "id": r[0], "title": r[1], "author": r[2], "price": float(r[3]), "stock": r[4]
    } for r in rows])

# Récupérer un livre par ID
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, price, stock FROM books WHERE id=%s", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify({
            "id": row[0], "title": row[1], "author": row[2],
            "price": float(row[3]), "stock": row[4]
        })
    else:
        return jsonify({"error": "Book not found"}), 404

# Ajouter un livre
@app.route('/books', methods=['POST'])
def create_book():
    data = request.json
    required_fields = ['title', 'author', 'price', 'stock']
    if not data or not all(f in data for f in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    title = str(data['title']).strip()
    author = str(data['author']).strip()
    try:
        price = float(data['price'])
        stock = int(data['stock'])
    except ValueError:
        return jsonify({"error": "Price must be a number and stock must be an integer"}), 400

    if not title or not author or price < 0 or stock < 0:
        return jsonify({"error": "Invalid input values"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO books (title, author, price, stock) VALUES (%s, %s, %s, %s) RETURNING id",
        (title, author, price, stock)
    )
    book_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": book_id, "status": "created"}), 201

# Mettre à jour un livre
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    fields = []
    values = []

    if 'title' in data:
        fields.append("title=%s")
        values.append(str(data['title']).strip())
    if 'author' in data:
        fields.append("author=%s")
        values.append(str(data['author']).strip())
    if 'price' in data:
        fields.append("price=%s")
        values.append(float(data['price']))
    if 'stock' in data:
        fields.append("stock=%s")
        values.append(int(data['stock']))

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    values.append(id)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE books SET {', '.join(fields)} WHERE id=%s RETURNING id", values)
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if result:
        return jsonify({"id": result[0], "status": "updated"})
    else:
        return jsonify({"error": "Book not found"}), 404

# Supprimer un livre
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id=%s RETURNING id", (id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if result:
        return jsonify({"id": result[0], "status": "deleted"})
    else:
        return jsonify({"error": "Book not found"}), 404

# --- Gestion stock ---

@app.route('/books/<int:id>/reserve', methods=['POST'])
def reserve_book(id):
    data = request.json or {}
    quantity = int(data.get("quantity", 1))
    if quantity <= 0:
        return jsonify({"error": "Quantity must be at least 1"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE books SET stock = stock - %s WHERE id=%s AND stock >= %s RETURNING id, stock",
        (quantity, id, quantity)
    )
    result = cur.fetchone()
    if not result:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "Not enough stock"}), 400
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "reserved", "book_id": result[0], "remaining_stock": result[1]})

@app.route('/books/<int:id>/release', methods=['POST'])
def release_stock(id):
    data = request.json or {}
    quantity = int(data.get("quantity", 1))
    if quantity <= 0:
        return jsonify({"error": "Quantity must be at least 1"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE books SET stock = stock + %s WHERE id=%s RETURNING id, stock", (quantity, id))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if result:
        return jsonify({"status": "released", "book_id": result[0], "stock": result[1]})
    else:
        return jsonify({"error": "Book not found"}), 404

# --- Lancer l'application ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
