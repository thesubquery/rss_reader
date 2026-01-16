#!/usr/bin/env python3
"""
RSS Reader - Desktop application for reading RSS/Atom feeds.
"""
import threading
import webview
import uvicorn
from app.api import app
from app.database import init_db

# Server configuration
HOST = "127.0.0.1"
PORT = 8765


def start_server():
    """Start the FastAPI server in a separate thread."""
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


def main():
    # Initialize database
    init_db()

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Create and start the webview window
    window = webview.create_window(
        title="RSS Reader",
        url=f"http://{HOST}:{PORT}",
        width=1200,
        height=800,
        min_size=(800, 600),
    )

    # Start the webview (blocks until window is closed)
    webview.start()


if __name__ == "__main__":
    main()
