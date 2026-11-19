
"""
NEMESIS CORE
Simulation and Detection Database

Stores inert simulation events and their defensive
detection results in a local SQLite database.
"""

import json
import sqlite3

from contextlib import contextmanager

from config import DATABASE_DIR


DB_PATH = DATABASE_DIR / "nemesis.db"


@contextmanager
def database_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_simulation_database():

    with database_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS simulation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id TEXT NOT NULL UNIQUE,
                scenario_id TEXT NOT NULL,
                scenario_name TEXT NOT NULL,
                event_code TEXT NOT NULL,
                severity TEXT NOT NULL,
                detection_status TEXT NOT NULL,
                matched_rule TEXT,
                event_json TEXT NOT NULL,
                detection_json TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


def save_simulation(event, detection):

    if not isinstance(event, dict):
        raise ValueError("Event must be a dictionary.")

    if not isinstance(detection, dict):
        raise ValueError("Detection must be a dictionary.")

    if event.get("status") != "SIMULATED":
        raise ValueError("Only simulated events can be saved.")

    if detection.get("status") not in [
        "DETECTED",
        "NOT_DETECTED",
    ]:
        raise ValueError("Invalid detection status.")

    initialize_simulation_database()

    with database_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO simulation_records (
                simulation_id,
                scenario_id,
                scenario_name,
                event_code,
                severity,
                detection_status,
                matched_rule,
                event_json,
                detection_json,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["simulation_id"],
                event["scenario_id"],
                event["scenario_name"],
                event["event_code"],
                event["severity"],
                detection["status"],
                detection.get("matched_rule"),
                json.dumps(event),
                json.dumps(detection),
                event["timestamp"],
            ),
        )

        return cursor.lastrowid


def get_simulation_history(limit=20):

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("Limit must be an integer.")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    initialize_simulation_database()

    with database_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                simulation_id,
                scenario_id,
                scenario_name,
                event_code,
                severity,
                detection_status,
                matched_rule,
                timestamp
            FROM simulation_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]


def get_simulation_count():

    initialize_simulation_database()

    with database_connection() as connection:

        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM simulation_records
            """
        ).fetchone()

        return row["total"]
