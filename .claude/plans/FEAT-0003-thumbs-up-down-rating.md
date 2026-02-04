# FEAT-0003: Thumbs Up/Down Rating

## Feature Description
**From BACKLOG.md:** Allow users to rate articles with thumbs up or down

## Clarified Requirements
- Simple visual indicator (thumbs icon filled/highlighted when rated)
- Buttons appear in article content panel only (not in article list)
- Mutually exclusive: selecting thumbs up clears thumbs down and vice versa

## Implementation Plan

### 1. Database Migration
Create `migrations/002_add_article_ratings.py`:
- Add `is_thumbs_up` Boolean column (nullable, default NULL)
- Add `is_thumbs_down` Boolean column (nullable, default NULL)

### 2. Backend Model (app/models.py)
Add to Article class (~line 56):
```python
is_thumbs_up = Column(Boolean, default=False)
is_thumbs_down = Column(Boolean, default=False)
```

### 3. Backend API (app/api.py)
- Add `is_thumbs_up: Optional[bool]` and `is_thumbs_down: Optional[bool]` to `ArticleUpdate` model
- Add same fields to `ArticleResponse` model
- Update PATCH endpoint logic to handle rating fields

### 4. Frontend JavaScript (static/app.js)
Add two functions following `toggleStar()` pattern:
- `toggleThumbsUp(articleId)` - toggle thumbs up, clear thumbs down if set
- `toggleThumbsDown(articleId)` - toggle thumbs down, clear thumbs up if set

Update `renderArticleView()`:
- Add thumbs up/down buttons after existing Star/Read/Open buttons
- Show filled icon when active, outline when inactive

### 5. Frontend CSS (static/styles.css)
- Add `.rating-button` class with appropriate styling
- Add `.rating-button.active` for highlighted state (e.g., accent color)
- Bump cache version in index.html from `v=6` to `v=7`

## Files to Modify
1. `migrations/002_add_article_ratings.py` (new)
2. `app/models.py` - Add rating columns
3. `app/api.py` - Update Pydantic models and PATCH logic
4. `static/app.js` - Add toggle functions and update render
5. `static/styles.css` - Add rating button styles
6. `static/index.html` - Bump CSS cache version

## Additional Feature: Filter by Rating
Added filter buttons in the article list header to filter articles by thumbs up or thumbs down rating.

### Changes:
- `app/api.py` - Added `thumbs_up` and `thumbs_down` query parameters to GET /api/articles
- `static/index.html` - Added 👍 and 👎 filter buttons in article list actions
- `static/app.js` - Added filter state (`filterThumbsUp`, `filterThumbsDown`) and toggle functions
- `static/styles.css` - Added `.filter-rating` class sharing styles with `.rating-button`

## Verification
1. Run the app: `python main.py`
2. Select an article in the content panel
3. Click thumbs up - verify it highlights
4. Click thumbs down - verify thumbs up clears and thumbs down highlights
5. Refresh the page - verify rating persists
6. Click 👍 filter button in article list header - verify only thumbs up articles shown
7. Click 👎 filter button - verify only thumbs down articles shown
8. Check database: `sqlite3 rss_reader.db "SELECT is_thumbs_up, is_thumbs_down FROM articles WHERE is_thumbs_up = 1 OR is_thumbs_down = 1;"`
