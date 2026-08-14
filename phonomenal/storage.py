import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "phonomenal.db")

CREATE_COMMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_CLASSIFICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    confidence REAL,
    schema_version INTEGER NOT NULL,
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (comment_id) REFERENCES comments(id)
);
"""

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database():
    conn = get_connection()
    conn.execute(CREATE_COMMENTS_TABLE)
    conn.execute(CREATE_CLASSIFICATIONS_TABLE)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DB_PATH}")