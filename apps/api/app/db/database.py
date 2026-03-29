import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent.parent / "resumeos.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as connection:
        connection.executescript(schema_sql)
        connection.commit()

