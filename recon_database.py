
import sqlite3
import json

from config import DATABASE_DIR

DB_PATH = DATABASE_DIR / "nemesis.db"


def initialize_database():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reconnaissance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
        """)

        connection.commit()


def save_reconnaissance(data):
    initialize_database()

    hostname = data["system"]["hostname"]
    timestamp = data["system"]["timestamp"]

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("""
            INSERT INTO reconnaissance
            (hostname, timestamp, result_json)
            VALUES (?, ?, ?)
        """, (
            hostname,
            timestamp,
            json.dumps(data)
        ))

        connection.commit()
        return cursor.lastrowid


def get_reconnaissance_history():
    initialize_database()

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT id, hostname, timestamp, result_json
            FROM reconnaissance
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]
