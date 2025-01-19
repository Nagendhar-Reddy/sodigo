from flask import Flask, request, jsonify, redirect
import sqlite3
from utils import generate_short_url, validate_url, get_expiry_time
from models import initialize_db
from datetime import datetime

app = Flask(__name__)

initialize_db()

@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.json
    original_url = data.get("url")
    expiry_hours = data.get("expiry_hours", 24)

    if not validate_url(original_url):
        return jsonify({"error": "Invalid URL"}), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    short_url = generate_short_url(original_url)
    expires_at = get_expiry_time(expiry_hours)

    cursor.execute("SELECT * FROM urls WHERE original_url = ?", (original_url,))
    existing = cursor.fetchone()
    if existing:
        return jsonify({"short_url": existing[2]}), 200

    cursor.execute("INSERT INTO urls (original_url, short_url, expires_at) VALUES (?, ?, ?)",
                   (original_url, short_url, expires_at))
    conn.commit()
    conn.close()

    return jsonify({"short_url": short_url}), 201
@app.route("/<short_url>", methods=["GET"])
def redirect_url(short_url):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    full_short_url = f"https://short.ly/{short_url}"
    cursor.execute("SELECT original_url, expires_at FROM urls WHERE short_url = ?", (full_short_url,))
    record = cursor.fetchone()

    if not record:
        return jsonify({"error": "URL not found"}), 404

    original_url, expires_at = record
    if datetime.now() > datetime.fromisoformat(expires_at):
        return jsonify({"error": "URL has expired"}), 410

    cursor.execute("INSERT INTO analytics (short_url, ip_address) VALUES (?, ?)",
                   (full_short_url, request.remote_addr))
    conn.commit()
    conn.close()

    return redirect(original_url)


@app.route("/analytics/<short_url>", methods=["GET"])
def get_analytics(short_url):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    full_short_url = f"https://short.ly/{short_url}"
    cursor.execute("SELECT * FROM analytics WHERE short_url = ?", (full_short_url,))
    logs = cursor.fetchall()

    if not logs:
        return jsonify({"error": "No analytics available for this URL"}), 404

    analytics_data = [{
        "accessed_at": log[2],
        "ip_address": log[3]
    } for log in logs]

    conn.close()
    return jsonify(analytics_data), 200

if __name__ == "__main__":
    app.run(debug=True)
