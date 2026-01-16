import feedparser
from datetime import datetime
from dateutil import parser as date_parser
from typing import Optional
import aiohttp
import asyncio


async def fetch_feed_content(url: str) -> Optional[str]:
    """Fetch feed content from URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
    return None


def parse_feed(content: str) -> dict:
    """Parse RSS/Atom feed content."""
    return feedparser.parse(content)


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        return None


def extract_feed_info(parsed: dict) -> dict:
    """Extract feed metadata."""
    feed = parsed.get("feed", {})
    return {
        "title": feed.get("title", "Untitled Feed"),
        "site_url": feed.get("link", ""),
        "description": feed.get("description", ""),
    }


def extract_articles(parsed: dict) -> list[dict]:
    """Extract articles from parsed feed."""
    articles = []
    for entry in parsed.get("entries", []):
        # Get content - prefer content, fall back to summary
        content = ""
        if entry.get("content"):
            content = entry["content"][0].get("value", "")
        elif entry.get("description"):
            content = entry["description"]

        # Get summary
        summary = entry.get("summary", "")
        if not summary and content:
            # Create summary from content (first 300 chars)
            summary = content[:300] + "..." if len(content) > 300 else content

        # Get unique identifier
        guid = entry.get("id") or entry.get("link") or entry.get("title", "")

        # Parse published date
        published = None
        if entry.get("published"):
            published = parse_date(entry["published"])
        elif entry.get("updated"):
            published = parse_date(entry["updated"])

        articles.append({
            "guid": guid,
            "title": entry.get("title", "Untitled"),
            "link": entry.get("link", ""),
            "content": content,
            "summary": summary,
            "author": entry.get("author", ""),
            "published": published,
        })

    return articles


async def fetch_and_parse_feed(url: str) -> Optional[dict]:
    """Fetch and parse a feed URL, returning feed info and articles."""
    content = await fetch_feed_content(url)
    if not content:
        return None

    parsed = parse_feed(content)
    if parsed.bozo and not parsed.entries:
        # Feed parsing failed completely
        return None

    feed_info = extract_feed_info(parsed)
    articles = extract_articles(parsed)

    return {
        "feed_info": feed_info,
        "articles": articles,
    }
