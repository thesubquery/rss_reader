# RSS Reader

A desktop RSS reader for macOS. Built with Python, FastAPI, and pywebview.

![Dark mode UI](https://img.shields.io/badge/UI-Dark%20Mode-191919)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)

## Features

- Subscribe to RSS/Atom feeds
- Organize feeds into folders
- Mark articles as read/unread
- Star/favorite articles
- Filter to show unread articles only
- Rename feeds with custom names
- Dark mode UI with modern typography

## Installation

### Prerequisites

- macOS 10.13 or later
- [Homebrew](https://brew.sh/)

### Step 1: Install pyenv and Python

```bash
# Install pyenv and pyenv-virtualenv
brew install pyenv pyenv-virtualenv

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.10
pyenv install 3.10.0
```

### Step 2: Clone and set up the project

```bash
# Clone the repository
git clone <repository-url> rss_reader
cd rss_reader

# Create virtual environment
pyenv virtualenv 3.10.0 rss_reader
pyenv local rss_reader

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the application

```bash
python main.py
```

This opens a native macOS window with the RSS reader.

## Installing as a macOS App

A pre-built app bundle is included at `RSS Reader.app`.

**To install:**

1. Move the `rss_reader` folder to a permanent location:
   ```bash
   mv rss_reader ~/Applications/
   ```

2. Copy `RSS Reader.app` to your Applications folder:
   ```bash
   cp -r ~/Applications/rss_reader/RSS\ Reader.app /Applications/
   ```

3. Launch from Applications or add to Dock

**Note:** The app bundle references the project folder. If you move the project, update the path in `RSS Reader.app/Contents/MacOS/RSS Reader`.

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

- **Database:** `rss_reader.db` (SQLite) in the project root
- **Backup:** Copy `rss_reader.db` to back up all feeds and articles

## License

MIT
