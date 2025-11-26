from flask import Flask, request, jsonify
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Подключение к БД
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://serverless_db_3go8_user:cpVHqRDwbYlG7uC7qObKazoTlmGApZiU@dpg-d4jot1buibrs73f0segg-a.oregon-postgres.render.com/serverless_db_3go8')

if DATABASE_URL:
    try:
        # Парсим URL базы данных
        url = urlparse(DATABASE_URL)
        
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            database=url.path[1:],  # убираем первый символ '/'
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        print("Успешное подключение к БД")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        conn = None
else:
    conn = None

# Создание таблицы при старте
if conn:
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
            print("Таблица messages создана или уже существует")
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")

@app.route('/')
def home():
    return jsonify({"status": "Server is running", "db_connected": conn is not None})

@app.route('/save', methods=['POST'])
def save_message():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
            conn.commit()
        return jsonify({"status": "saved", "message": message})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/messages')
def get_messages():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()

        messages = [{"id": r[0], "text": r[1], "time": r[2].isoformat()} for r in rows]
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
