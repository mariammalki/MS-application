from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BOOK_SERVICE_URL = "http://book-service:5001"
ORDER_SERVICE_URL = "http://order-service:5002"

# ---- Health ----
@app.route('/health', methods=['GET'])
def health():
    try:
        book_health = requests.get(f"{BOOK_SERVICE_URL}/health").json()
    except:
        book_health = {"status": "unavailable"}
    try:
        order_health = requests.get(f"{ORDER_SERVICE_URL}/health").json()
    except:
        order_health = {"status": "unavailable"}
    return jsonify({
        "gateway": "healthy",
        "book_service": book_health,
        "order_service": order_health
    })

# ---- BOOK ROUTES ----
@app.route('/api/books', methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        try:
            resp = requests.get(f"{BOOK_SERVICE_URL}/books")
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            data = request.json
            resp = requests.post(f"{BOOK_SERVICE_URL}/books", json=data)
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/books/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def book_by_id(id):
    if request.method == 'GET':
        try:
            resp = requests.get(f"{BOOK_SERVICE_URL}/books/{id}")
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'PUT':
        try:
            data = request.json
            resp = requests.put(f"{BOOK_SERVICE_URL}/books/{id}", json=data)
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'DELETE':
        try:
            resp = requests.delete(f"{BOOK_SERVICE_URL}/books/{id}")
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# ---- ORDER ROUTES ----
@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        try:
            resp = requests.get(f"{ORDER_SERVICE_URL}/orders")
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            data = request.json
            resp = requests.post(f"{ORDER_SERVICE_URL}/orders", json=data)
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
