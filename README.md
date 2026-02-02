# RSS Reader

A desktop RSS reader for macOS. Built with Python, FastAPI, and pywebview.

![Dark mode UI](https://img.shields.io/badge/UI-Dark%20Mode-191919)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)

## Features

- Subscribe to RSS/Atom feeds
- Organize feeds into folders
- Mark articles as read/unread
- Star/favorite articles
- Filter to show unread articles only
- Rename feeds with custom names
- Dark mode UI with modern typography

## Installation

### Option 1: Download the App (Recommended)

1. Download `RSS Reader.dmg` from the [Releases](../../releases) page
2. Open the DMG and drag **RSS Reader** to your Applications folder
3. Launch from Applications

> **Note:** On first launch, macOS may show a security warning. Right-click the app and select "Open" to bypass Gatekeeper.

### Option 2: Build from Source

#### Prerequisites

- macOS 10.13 or later
- Python 3.11+ (via [pyenv](https://github.com/pyenv/pyenv) recommended)

#### Setup

```bash
# Clone the repository
git clone <repository-url> rss_reader
cd rss_reader

# Create virtual environment (if using pyenv)
pyenv install 3.11.11
pyenv virtualenv 3.11.11 rss_reader_311
pyenv local rss_reader_311

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Building the Standalone App

```bash
# Install build dependencies
pip install -r requirements-dev.txt

# Build app and DMG
python scripts/build_app.py
```

Output:
- `dist/RSS Reader.app` - Standalone application
- `dist/RSS Reader.dmg` - Distributable disk image

## Usage

1. Click **+ Add Feed** to subscribe to an RSS feed
2. Paste the feed URL (e.g., `https://feeds.arstechnica.com/arstechnica/index`)
3. Click on articles to read them
4. Use **Unread only** to filter unread articles
5. Click the ⭐ to star articles
6. Hover over feeds to rename or delete them

## Sample Feeds

```
https://feeds.arstechnica.com/arstechnica/index
https://www.theverge.com/rss/index.xml
https://news.ycombinator.com/rss
https://lobste.rs/rss
https://daringfireball.net/feeds/main
```

## Data Storage

- **Standalone app:** `~/Library/Application Support/RSS Reader/rss_reader.db`
- **Development:** `rss_reader.db` in the project root
- **Backup:** Copy `rss_reader.db` to back up all feeds and articles

## License

MIT
