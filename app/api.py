import sys
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path

from .database import get_db, init_db
from .models import Folder, Feed, Article
from .feed_parser import fetch_and_parse_feed


def get_base_path() -> Path:
    """Get the base path for static files, handling frozen apps."""
    if getattr(sys, 'frozen', False):
        # Running as bundled app - files are in _MEIPASS
        return Path(sys._MEIPASS)
    else:
        # Running in development
        return Path(__file__).parent.parent


app = FastAPI(title="RSS Reader")

# Mount static files
static_path = get_base_path() / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


# Pydantic models
class FolderCreate(BaseModel):
    name: str


class FolderResponse(BaseModel):
    id: int
    name: str
    order: int
    feed_count: int = 0
    unread_count: int = 0

    class Config:
        from_attributes = True


class FeedCreate(BaseModel):
    url: str
    folder_id: Optional[int] = None


class FeedResponse(BaseModel):
    id: int
    title: str
    url: str
    site_url: Optional[str]
    folder_id: Optional[int]
    unread_count: int = 0
    last_fetched: Optional[datetime]

    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    id: int
    feed_id: int
    feed_title: str = ""
    title: str
    link: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    author: Optional[str]
    published: Optional[datetime]
    is_read: bool
    is_starred: bool

    class Config:
        from_attributes = True


class ArticleUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None


class FeedUpdate(BaseModel):
    title: Optional[str] = None
    folder_id: Optional[int] = None


# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()


# Root route - serve index.html
@app.get("/")
async def root():
    return FileResponse(static_path / "index.html")


# Folder routes
@app.get("/api/folders", response_model=list[FolderResponse])
def get_folders(db: Session = Depends(get_db)):
    folders = db.query(Folder).order_by(Folder.order).all()
    result = []
    for folder in folders:
        feed_count = len(folder.feeds)
        unread_count = sum(
            db.query(func.count(Article.id))
            .filter(Article.feed_id == feed.id, Article.is_read == False)
            .scalar()
            for feed in folder.feeds
        )
        result.append(FolderResponse(
            id=folder.id,
            name=folder.name,
            order=folder.order,
            feed_count=feed_count,
            unread_count=unread_count,
        ))
    return result


@app.post("/api/folders", response_model=FolderResponse)
def create_folder(folder: FolderCreate, db: Session = Depends(get_db)):
    max_order = db.query(func.max(Folder.order)).scalar() or 0
    db_folder = Folder(name=folder.name, order=max_order + 1)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return FolderResponse(
        id=db_folder.id,
        name=db_folder.name,
        order=db_folder.order,
        feed_count=0,
        unread_count=0,
    )


@app.delete("/api/folders/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    db.delete(folder)
    db.commit()
    return {"status": "ok"}


# Feed routes
@app.get("/api/feeds", response_model=list[FeedResponse])
def get_feeds(folder_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Feed)
    if folder_id is not None:
        query = query.filter(Feed.folder_id == folder_id)
    feeds = query.all()
    result = []
    for feed in feeds:
        unread_count = db.query(func.count(Article.id)).filter(
            Article.feed_id == feed.id, Article.is_read == False
        ).scalar()
        result.append(FeedResponse(
            id=feed.id,
            title=feed.title,
            url=feed.url,
            site_url=feed.site_url,
            folder_id=feed.folder_id,
            unread_count=unread_count,
            last_fetched=feed.last_fetched,
        ))
    return result


@app.post("/api/feeds", response_model=FeedResponse)
async def create_feed(feed: FeedCreate, db: Session = Depends(get_db)):
    # Check if feed already exists
    existing = db.query(Feed).filter(Feed.url == feed.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feed already exists")

    # Fetch and parse the feed
    result = await fetch_and_parse_feed(feed.url)
    if not result:
        raise HTTPException(status_code=400, detail="Could not fetch or parse feed")

    feed_info = result["feed_info"]
    articles = result["articles"]

    # Create feed
    db_feed = Feed(
        url=feed.url,
        title=feed_info["title"],
        original_title=feed_info["title"],
        site_url=feed_info["site_url"],
        description=feed_info["description"],
        folder_id=feed.folder_id,
        last_fetched=datetime.utcnow(),
    )
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    # Add articles
    for article_data in articles:
        article = Article(
            feed_id=db_feed.id,
            guid=article_data["guid"],
            title=article_data["title"],
            link=article_data["link"],
            content=article_data["content"],
            summary=article_data["summary"],
            author=article_data["author"],
            published=article_data["published"],
        )
        db.add(article)
    db.commit()

    return FeedResponse(
        id=db_feed.id,
        title=db_feed.title,
        url=db_feed.url,
        site_url=db_feed.site_url,
        folder_id=db_feed.folder_id,
        unread_count=len(articles),
        last_fetched=db_feed.last_fetched,
    )


@app.patch("/api/feeds/{feed_id}", response_model=FeedResponse)
def update_feed(feed_id: int, update: FeedUpdate, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    if update.title is not None:
        feed.title = update.title
    if update.folder_id is not None:
        feed.folder_id = update.folder_id

    db.commit()
    db.refresh(feed)

    unread_count = db.query(func.count(Article.id)).filter(
        Article.feed_id == feed.id, Article.is_read == False
    ).scalar()

    return FeedResponse(
        id=feed.id,
        title=feed.title,
        url=feed.url,
        site_url=feed.site_url,
        folder_id=feed.folder_id,
        unread_count=unread_count,
        last_fetched=feed.last_fetched,
    )


@app.delete("/api/feeds/{feed_id}")
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    db.delete(feed)
    db.commit()
    return {"status": "ok"}


@app.post("/api/feeds/{feed_id}/refresh", response_model=FeedResponse)
async def refresh_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    result = await fetch_and_parse_feed(feed.url)
    if not result:
        raise HTTPException(status_code=400, detail="Could not fetch feed")

    articles = result["articles"]
    existing_guids = {a.guid for a in feed.articles}

    new_count = 0
    for article_data in articles:
        if article_data["guid"] not in existing_guids:
            article = Article(
                feed_id=feed.id,
                guid=article_data["guid"],
                title=article_data["title"],
                link=article_data["link"],
                content=article_data["content"],
                summary=article_data["summary"],
                author=article_data["author"],
                published=article_data["published"],
            )
            db.add(article)
            new_count += 1

    feed.last_fetched = datetime.utcnow()
    db.commit()

    unread_count = db.query(func.count(Article.id)).filter(
        Article.feed_id == feed.id, Article.is_read == False
    ).scalar()

    return FeedResponse(
        id=feed.id,
        title=feed.title,
        url=feed.url,
        site_url=feed.site_url,
        folder_id=feed.folder_id,
        unread_count=unread_count,
        last_fetched=feed.last_fetched,
    )


@app.post("/api/feeds/refresh-all")
async def refresh_all_feeds(db: Session = Depends(get_db)):
    feeds = db.query(Feed).all()
    results = {"refreshed": 0, "failed": 0, "new_articles": 0}

    for feed in feeds:
        try:
            result = await fetch_and_parse_feed(feed.url)
            if result:
                articles = result["articles"]
                existing_guids = {a.guid for a in feed.articles}
                for article_data in articles:
                    if article_data["guid"] not in existing_guids:
                        article = Article(
                            feed_id=feed.id,
                            guid=article_data["guid"],
                            title=article_data["title"],
                            link=article_data["link"],
                            content=article_data["content"],
                            summary=article_data["summary"],
                            author=article_data["author"],
                            published=article_data["published"],
                        )
                        db.add(article)
                        results["new_articles"] += 1
                feed.last_fetched = datetime.utcnow()
                results["refreshed"] += 1
            else:
                results["failed"] += 1
        except Exception:
            results["failed"] += 1

    db.commit()
    return results


# Article routes
@app.get("/api/articles", response_model=list[ArticleResponse])
def get_articles(
    feed_id: Optional[int] = None,
    folder_id: Optional[int] = None,
    starred: Optional[bool] = None,
    unread: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Article).join(Feed)

    if feed_id is not None:
        query = query.filter(Article.feed_id == feed_id)
    if folder_id is not None:
        query = query.filter(Feed.folder_id == folder_id)
    if starred is not None:
        query = query.filter(Article.is_starred == starred)
    if unread is not None:
        query = query.filter(Article.is_read == (not unread))

    articles = query.order_by(Article.published.desc().nullslast()).offset(offset).limit(limit).all()

    return [
        ArticleResponse(
            id=a.id,
            feed_id=a.feed_id,
            feed_title=a.feed.title,
            title=a.title,
            link=a.link,
            content=a.content,
            summary=a.summary,
            author=a.author,
            published=a.published,
            is_read=a.is_read,
            is_starred=a.is_starred,
        )
        for a in articles
    ]


@app.get("/api/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleResponse(
        id=article.id,
        feed_id=article.feed_id,
        feed_title=article.feed.title,
        title=article.title,
        link=article.link,
        content=article.content,
        summary=article.summary,
        author=article.author,
        published=article.published,
        is_read=article.is_read,
        is_starred=article.is_starred,
    )


@app.patch("/api/articles/{article_id}", response_model=ArticleResponse)
def update_article(article_id: int, update: ArticleUpdate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if update.is_read is not None:
        article.is_read = update.is_read
    if update.is_starred is not None:
        article.is_starred = update.is_starred

    db.commit()
    db.refresh(article)

    return ArticleResponse(
        id=article.id,
        feed_id=article.feed_id,
        feed_title=article.feed.title,
        title=article.title,
        link=article.link,
        content=article.content,
        summary=article.summary,
        author=article.author,
        published=article.published,
        is_read=article.is_read,
        is_starred=article.is_starred,
    )


@app.post("/api/articles/mark-all-read")
def mark_all_read(
    feed_id: Optional[int] = None,
    folder_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Article)

    if feed_id is not None:
        query = query.filter(Article.feed_id == feed_id)
    elif folder_id is not None:
        feed_ids = [f.id for f in db.query(Feed).filter(Feed.folder_id == folder_id).all()]
        query = query.filter(Article.feed_id.in_(feed_ids))

    count = query.filter(Article.is_read == False).update({"is_read": True})
    db.commit()
    return {"marked_read": count}


# Stats
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_feeds = db.query(func.count(Feed.id)).scalar()
    total_articles = db.query(func.count(Article.id)).scalar()
    unread_articles = db.query(func.count(Article.id)).filter(Article.is_read == False).scalar()
    starred_articles = db.query(func.count(Article.id)).filter(Article.is_starred == True).scalar()
    return {
        "total_feeds": total_feeds,
        "total_articles": total_articles,
        "unread_articles": unread_articles,
        "starred_articles": starred_articles,
    }
