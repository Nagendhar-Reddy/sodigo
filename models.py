import sqlite3

def initialize_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY,
        original_url TEXT NOT NULL,
        short_url TEXT NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY,
        short_url TEXT NOT NULL,
        accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT NOT NULL,
        FOREIGN KEY (short_url) REFERENCES urls (short_url)
    )''')

    conn.commit()
    conn.close()
