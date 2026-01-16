from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    feeds = relationship("Feed", back_populates="folder", cascade="all, delete-orphan")


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    title = Column(String(255), nullable=False)
    original_title = Column(String(255), nullable=True)
    url = Column(String(500), nullable=False, unique=True)
    site_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    last_fetched = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    folder = relationship("Folder", back_populates="feeds")
    articles = relationship("Article", back_populates="feed", cascade="all, delete-orphan")

    @property
    def unread_count(self):
        return sum(1 for a in self.articles if not a.is_read)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable=False)
    guid = Column(String(500), nullable=False)
    title = Column(String(500), nullable=False)
    link = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    published = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    feed = relationship("Feed", back_populates="articles")
