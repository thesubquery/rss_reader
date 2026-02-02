#!/usr/bin/env python3
"""
Migration script to add is_thumbs_up and is_thumbs_down columns to articles table.
Run this once after updating the model if you have existing data.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "rss_reader.db"

def migrate():
    if not DB_PATH.exists():
        print("Database does not exist yet. No migration needed.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]

    added_columns = []

    if "is_thumbs_up" not in columns:
        print("Adding 'is_thumbs_up' column to articles table...")
        cursor.execute("ALTER TABLE articles ADD COLUMN is_thumbs_up BOOLEAN DEFAULT 0")
        added_columns.append("is_thumbs_up")
    else:
        print("Column 'is_thumbs_up' already exists.")

    if "is_thumbs_down" not in columns:
        print("Adding 'is_thumbs_down' column to articles table...")
        cursor.execute("ALTER TABLE articles ADD COLUMN is_thumbs_down BOOLEAN DEFAULT 0")
        added_columns.append("is_thumbs_down")
    else:
        print("Column 'is_thumbs_down' already exists.")

    if added_columns:
        conn.commit()
        print(f"Migration complete! Added columns: {', '.join(added_columns)}")
    else:
        print("No migration needed.")

    conn.close()

if __name__ == "__main__":
    migrate()
