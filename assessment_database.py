
import sqlite3
import json

from contextlib import contextmanager
from config import DATABASE_DIR


DB_PATH = DATABASE_DIR / "nemesis.db"


@contextmanager
def database_connection():
    """Open a SQLite connection and always close it."""

    connection = sqlite3.connect(DB_PATH)

    try:
        yield connection
    finally:
        connection.close()


def initialize_database():
    """Create the assessment table if it does not exist."""

    with database_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS security_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                assessment TEXT NOT NULL,
                total_checks INTEGER NOT NULL,
                pass_count INTEGER NOT NULL,
                warning_count INTEGER NOT NULL,
                error_count INTEGER NOT NULL,
                result_json TEXT NOT NULL
            )
        """)

        connection.commit()


def calculate_summary(data):
    """Calculate assessment status totals."""

    checks = data.get("checks", {})

    if not isinstance(checks, dict):
        raise ValueError("Assessment checks must be a dictionary.")

    summary = {
        "total_checks": len(checks),
        "pass_count": 0,
        "warning_count": 0,
        "error_count": 0
    }

    for check in checks.values():
        if not isinstance(check, dict):
            continue

        status = str(check.get("status", "")).upper()

        if status == "PASS":
            summary["pass_count"] += 1

        elif status == "WARNING":
            summary["warning_count"] += 1

        elif status in ("ERROR", "UNSUPPORTED"):
            summary["error_count"] += 1

    return summary


def save_assessment(data):
    """Save an assessment result to SQLite."""

    if not isinstance(data, dict):
        raise ValueError("Assessment data must be a dictionary.")

    if not data.get("timestamp"):
        raise ValueError("Assessment timestamp is required.")

    if not data.get("assessment"):
        raise ValueError("Assessment name is required.")

    if not isinstance(data.get("checks"), dict):
        raise ValueError("Assessment checks must be a dictionary.")

    initialize_database()

    summary = calculate_summary(data)

    with database_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO security_assessments (
                timestamp,
                assessment,
                total_checks,
                pass_count,
                warning_count,
                error_count,
                result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["timestamp"],
            data["assessment"],
            summary["total_checks"],
            summary["pass_count"],
            summary["warning_count"],
            summary["error_count"],
            json.dumps(data)
        ))

        connection.commit()

        return cursor.lastrowid


def get_assessment_history(limit=20):
    """Return the newest assessment records."""

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("Limit must be a positive integer.")

    initialize_database()

    with database_connection() as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT
                id,
                timestamp,
                assessment,
                total_checks,
                pass_count,
                warning_count,
                error_count,
                result_json
            FROM security_assessments
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def get_assessment_count():
    """Return the total number of stored assessments."""

    initialize_database()

    with database_connection() as connection:
        result = connection.execute("""
            SELECT COUNT(*)
            FROM security_assessments
        """).fetchone()

        return result[0]
