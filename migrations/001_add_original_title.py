#!/usr/bin/env python3
"""
Migration script to add original_title column to feeds table.
Run this once after updating the model if you have existing data.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "rss_reader.db"

def migrate():
    if not DB_PATH.exists():
        print("Database does not exist yet. No migration needed.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if original_title column already exists
    cursor.execute("PRAGMA table_info(feeds)")
    columns = [col[1] for col in cursor.fetchall()]

    if "original_title" in columns:
        print("Column 'original_title' already exists. No migration needed.")
        conn.close()
        return

    print("Adding 'original_title' column to feeds table...")

    # Add the column
    cursor.execute("ALTER TABLE feeds ADD COLUMN original_title VARCHAR(255)")

    # Copy existing titles to original_title
    cursor.execute("UPDATE feeds SET original_title = title WHERE original_title IS NULL")

    conn.commit()
    conn.close()

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
