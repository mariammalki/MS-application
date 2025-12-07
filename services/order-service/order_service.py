from flask import Flask, request, jsonify
import psycopg2, requests, os

app = Flask(__name__)

# Configuration DB
DB_HOST = os.getenv("DB_HOST", "database-service")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bookstore_db")
DB_USER = os.getenv("DB_USER", "bookstore_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bookstore_password")

# URL Book Service
BOOK_SERVICE_URL = "http://book-service:5001"

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "order_service": {"status": "healthy"},
        "book_service": {"status": "unknown"}
    }), 200

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        required_fields = ["customer_name", "customer_email", "book_id", "quantity"]
        if not data or not all(f in data for f in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        book_id = int(data["book_id"])
        quantity = int(data["quantity"])
        if quantity <= 0:
            return jsonify({"error": "Quantity must be at least 1"}), 400

        # Vérifier le livre dans Book Service
        book_resp = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}", timeout=5)
        if book_resp.status_code != 200:
            return jsonify({"error": "Book not found"}), 404

        book = book_resp.json()
        if book.get("stock", 0) < quantity:
            return jsonify({"error": "Not enough stock"}), 400

        # Réserver le stock si votre Book Service a une route /reserve
        reserve_resp = requests.post(f"{BOOK_SERVICE_URL}/books/{book_id}/reserve", json={"quantity": quantity}, timeout=5)
        if reserve_resp.status_code != 200:
            return jsonify({"error": "Failed to reserve stock"}), 400

        # Calcul du prix total
        total_price = float(book["price"]) * quantity

        # Insérer la commande dans la DB
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (customer_name, customer_email, book_id, book_title, quantity, total_price, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (data["customer_name"], data["customer_email"], book_id, book["title"], quantity, total_price, 'created'))
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"order_id": order_id, "status": "created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders', methods=['GET'])
def list_orders():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, customer_name, customer_email, book_title, quantity, total_price, status FROM orders")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        orders = [
            {
                "id": r[0], "customer_name": r[1], "customer_email": r[2],
                "book_title": r[3], "quantity": r[4], "total_price": float(r[5]), "status": r[6]
            } for r in rows
        ]
        return jsonify(orders), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
