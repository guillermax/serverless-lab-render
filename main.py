from flask import Flask, request, jsonify
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Подключение к БД
DATABASE_URL = os.environ.get('postgresql://serverless_db_3go8_user:cpVHqRDwbYlG7uC7qObKazoTlmGApZiU@dpg-d4jot1buibrs73f0segg-a/serverless_db_3go8')
if DATABASE_URL:
    url = urlparse(postgresql://serverless_db_3go8_user:cpVHqRDwbYlG7uC7qObKazoTlmGApZiU@dpg-d4jot1buibrs73f0segg-a/serverless_db_3go8)
    conn = psycopg2.connect(
        database=serverless_db_3go8,
        user=serverless_db_3go8_user,
        password=cpVHqRDwbYlG7uC7qObKazoTlmGApZiU,
        host=dpg-d4jot1buibrs73f0segg-a,
        port=5432
    )
else:
    conn = None

# Создание таблицы при старте
if conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()

@app.route('/save', methods=['POST'])
def save_message():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    data = request.get_json()
    message = data.get('message', '') if data else ''

    with conn.cursor() as cur:
        cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
        conn.commit()

    return jsonify({"status": "saved", "message": message})

@app.route('/messages')
def get_messages():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    with conn.cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()

    messages = [{"id": r[0], "text": r[1], "time": r[2].isoformat()} for r in rows]
    return jsonify(messages)
