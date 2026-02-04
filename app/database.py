import sys
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from .models import Base


def get_database_path() -> Path:
    """Get the database path, using Application Support for bundled apps."""
    if getattr(sys, 'frozen', False):
        # Running as bundled app - use Application Support
        app_support = Path.home() / "Library" / "Application Support" / "RSS Reader"
        app_support.mkdir(parents=True, exist_ok=True)
        return app_support / "rss_reader.db"
    else:
        # Running in development - use project directory
        return Path(__file__).parent.parent / "rss_reader.db"


DATABASE_PATH = get_database_path()
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_migrations():
    """Run any pending database migrations."""
    if not DATABASE_PATH.exists():
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get existing columns in articles table
    cursor.execute("PRAGMA table_info(articles)")
    existing_columns = {col[1] for col in cursor.fetchall()}

    # Add missing columns
    migrations = [
        ("is_thumbs_up", "ALTER TABLE articles ADD COLUMN is_thumbs_up BOOLEAN DEFAULT 0"),
        ("is_thumbs_down", "ALTER TABLE articles ADD COLUMN is_thumbs_down BOOLEAN DEFAULT 0"),
    ]

    for column_name, sql in migrations:
        if column_name not in existing_columns:
            cursor.execute(sql)

    conn.commit()
    conn.close()


def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)
    run_migrations()


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
