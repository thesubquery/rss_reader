// State
const state = {
    currentView: 'all',
    currentFeedId: null,
    currentFolderId: null,
    currentArticleId: null,
    currentEditFeedId: null,
    showUnreadOnly: false,
    folders: [],
    feeds: [],
    articles: [],
};

// API helpers
async function api(endpoint, options = {}) {
    const response = await fetch(`/api${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'API error');
    }
    return response.json();
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;

    return date.toLocaleDateString();
}

// Render folders
function renderFolders() {
    const container = document.getElementById('folderList');
    container.innerHTML = state.folders.map(folder => `
        <div class="folder-item ${state.currentView === 'folder' && state.currentFolderId === folder.id ? 'active' : ''}"
             data-folder-id="${folder.id}">
            <span class="folder-icon">📁</span>
            <span class="item-name">${escapeHtml(folder.name)}</span>
            ${folder.unread_count > 0 ? `<span class="item-count">${folder.unread_count}</span>` : ''}
            <button class="btn-icon item-delete" onclick="deleteFolder(${folder.id}, event)" title="Delete folder">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
            </button>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.folder-item').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.closest('.item-delete')) return;
            selectFolder(parseInt(el.dataset.folderId));
        });
    });
}

// Render feeds
function renderFeeds() {
    const container = document.getElementById('feedList');
    // Show feeds not in any folder
    const unfoldered = state.feeds.filter(f => !f.folder_id);

    container.innerHTML = unfoldered.map(feed => `
        <div class="feed-item ${state.currentView === 'feed' && state.currentFeedId === feed.id ? 'active' : ''}"
             data-feed-id="${feed.id}">
            <span class="feed-icon">📄</span>
            <span class="item-name">${escapeHtml(feed.title)}</span>
            ${feed.unread_count > 0 ? `<span class="item-count">${feed.unread_count}</span>` : ''}
            <button class="btn-icon item-edit" onclick="openRenameFeed(${feed.id}, event)" title="Rename feed">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
            </button>
            <button class="btn-icon item-delete" onclick="deleteFeed(${feed.id}, event)" title="Delete feed">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
            </button>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.feed-item').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.closest('.item-delete')) return;
            selectFeed(parseInt(el.dataset.feedId));
        });
    });
}

// Render articles
function renderArticles() {
    const container = document.getElementById('articleList');

    if (state.articles.length === 0) {
        container.innerHTML = '<div class="empty-state">No articles</div>';
        return;
    }

    container.innerHTML = state.articles.map(article => `
        <div class="article-item ${article.id === state.currentArticleId ? 'active' : ''} ${!article.is_read ? 'unread' : ''}"
             data-article-id="${article.id}">
            <div class="article-header">
                <span class="article-feed">${escapeHtml(article.feed_title)}</span>
                <span class="article-star ${article.is_starred ? 'starred' : ''}"
                      onclick="toggleStar(${article.id}, event)">
                    ${article.is_starred ? '★' : '☆'}
                </span>
            </div>
            <div class="article-title">${escapeHtml(article.title)}</div>
            <div class="article-date">${formatDate(article.published)}</div>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.article-item').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target.closest('.article-star')) return;
            selectArticle(parseInt(el.dataset.articleId));
        });
    });
}

// Render article view
function renderArticleView(article) {
    const container = document.getElementById('articleView');

    if (!article) {
        container.innerHTML = '<div class="article-view-placeholder"><p>Select an article to read</p></div>';
        return;
    }

    container.innerHTML = `
        <div class="article-content">
            <header class="article-content-header">
                <h1 class="article-content-title">${escapeHtml(article.title)}</h1>
                <div class="article-content-meta">
                    <span>${escapeHtml(article.feed_title)}</span>
                    ${article.author ? `<span>by ${escapeHtml(article.author)}</span>` : ''}
                    <span>${formatDate(article.published)}</span>
                </div>
                <div class="article-content-actions">
                    <button class="btn btn-secondary" onclick="toggleStar(${article.id})">
                        ${article.is_starred ? '★ Unstar' : '☆ Star'}
                    </button>
                    <button class="btn btn-secondary" onclick="toggleRead(${article.id})">
                        ${article.is_read ? 'Mark unread' : 'Mark read'}
                    </button>
                    ${article.link ? `<a href="${escapeHtml(article.link)}" target="_blank" class="btn btn-secondary">Open original</a>` : ''}
                </div>
            </header>
            <div class="article-content-body">
                ${article.content || article.summary || '<p>No content available</p>'}
            </div>
        </div>
    `;
}

// Load data
async function loadFolders() {
    state.folders = await api('/folders');
    renderFolders();
    updateFolderSelect();
}

async function loadFeeds() {
    state.feeds = await api('/feeds');
    renderFeeds();
    updateStats();
}

async function loadArticles() {
    let endpoint = '/articles?limit=100';

    if (state.currentView === 'starred') {
        endpoint += '&starred=true';
    } else if (state.currentView === 'feed' && state.currentFeedId) {
        endpoint += `&feed_id=${state.currentFeedId}`;
    } else if (state.currentView === 'folder' && state.currentFolderId) {
        endpoint += `&folder_id=${state.currentFolderId}`;
    }

    if (state.showUnreadOnly) {
        endpoint += '&unread=true';
    }

    state.articles = await api(endpoint);
    renderArticles();
}

async function updateStats() {
    const stats = await api('/stats');
    document.getElementById('allCount').textContent = stats.unread_articles;
    document.getElementById('starredCount').textContent = stats.starred_articles;
}

// Selection handlers
function selectView(view) {
    state.currentView = view;
    state.currentFeedId = null;
    state.currentFolderId = null;
    state.currentArticleId = null;

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.view === view);
    });
    document.querySelectorAll('.folder-item, .feed-item').forEach(el => {
        el.classList.remove('active');
    });

    // Update title
    const titles = { all: 'All Items', starred: 'Starred' };
    document.getElementById('currentViewTitle').textContent = titles[view] || 'All Items';

    loadArticles();
    renderArticleView(null);
}

function selectFolder(folderId) {
    state.currentView = 'folder';
    state.currentFolderId = folderId;
    state.currentFeedId = null;
    state.currentArticleId = null;

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.folder-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.folderId) === folderId);
    });
    document.querySelectorAll('.feed-item').forEach(el => el.classList.remove('active'));

    const folder = state.folders.find(f => f.id === folderId);
    document.getElementById('currentViewTitle').textContent = folder?.name || 'Folder';

    loadArticles();
    renderArticleView(null);
}

function selectFeed(feedId) {
    state.currentView = 'feed';
    state.currentFeedId = feedId;
    state.currentFolderId = null;
    state.currentArticleId = null;

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.folder-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.feed-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.feedId) === feedId);
    });

    const feed = state.feeds.find(f => f.id === feedId);
    document.getElementById('currentViewTitle').textContent = feed?.title || 'Feed';

    loadArticles();
    renderArticleView(null);
}

async function selectArticle(articleId) {
    state.currentArticleId = articleId;

    // Update article list
    document.querySelectorAll('.article-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.articleId) === articleId);
    });

    // Load and show article
    const article = await api(`/articles/${articleId}`);
    renderArticleView(article);

    // Mark as read
    if (!article.is_read) {
        await api(`/articles/${articleId}`, {
            method: 'PATCH',
            body: JSON.stringify({ is_read: true }),
        });

        // Update local state and re-render
        const idx = state.articles.findIndex(a => a.id === articleId);
        if (idx >= 0) {
            state.articles[idx].is_read = true;
            renderArticles();
        }
        loadFeeds();
        loadFolders();
    }
}

// Actions
async function toggleStar(articleId, event) {
    if (event) event.stopPropagation();

    const article = state.articles.find(a => a.id === articleId);
    if (!article) return;

    const newStarred = !article.is_starred;
    await api(`/articles/${articleId}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_starred: newStarred }),
    });

    article.is_starred = newStarred;
    renderArticles();
    if (state.currentArticleId === articleId) {
        renderArticleView(article);
    }
    updateStats();
}

async function toggleRead(articleId) {
    const article = state.articles.find(a => a.id === articleId);
    if (!article) return;

    const newRead = !article.is_read;
    await api(`/articles/${articleId}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_read: newRead }),
    });

    article.is_read = newRead;
    renderArticles();
    if (state.currentArticleId === articleId) {
        renderArticleView(article);
    }
    loadFeeds();
    loadFolders();
}

async function markAllRead() {
    let endpoint = '/articles/mark-all-read';
    const params = [];

    if (state.currentView === 'feed' && state.currentFeedId) {
        params.push(`feed_id=${state.currentFeedId}`);
    } else if (state.currentView === 'folder' && state.currentFolderId) {
        params.push(`folder_id=${state.currentFolderId}`);
    }

    if (params.length) endpoint += '?' + params.join('&');

    await api(endpoint, { method: 'POST' });
    loadArticles();
    loadFeeds();
    loadFolders();
}

function toggleUnreadFilter() {
    state.showUnreadOnly = !state.showUnreadOnly;
    updateUnreadButton();
    loadArticles();
}

function updateUnreadButton() {
    const btn = document.getElementById('toggleUnread');
    btn.textContent = state.showUnreadOnly ? 'Show all' : 'Unread only';
    btn.classList.toggle('active', state.showUnreadOnly);
}

async function refreshAllFeeds() {
    const btn = document.getElementById('refreshAll');
    btn.classList.add('loading');

    try {
        await api('/feeds/refresh-all', { method: 'POST' });
        loadFeeds();
        loadFolders();
        loadArticles();
    } finally {
        btn.classList.remove('loading');
    }
}

async function deleteFeed(feedId, event) {
    if (event) event.stopPropagation();
    if (!confirm('Delete this feed and all its articles?')) return;

    await api(`/feeds/${feedId}`, { method: 'DELETE' });
    loadFeeds();
    loadFolders();

    if (state.currentFeedId === feedId) {
        selectView('all');
    } else {
        loadArticles();
    }
}

async function deleteFolder(folderId, event) {
    if (event) event.stopPropagation();
    if (!confirm('Delete this folder and all its feeds?')) return;

    await api(`/folders/${folderId}`, { method: 'DELETE' });
    loadFolders();
    loadFeeds();

    if (state.currentFolderId === folderId) {
        selectView('all');
    } else {
        loadArticles();
    }
}

function openRenameFeed(feedId, event) {
    if (event) event.stopPropagation();
    state.currentEditFeedId = feedId;
    const feed = state.feeds.find(f => f.id === feedId);
    if (feed) {
        document.getElementById('feedNewName').value = feed.title;
        openModal('renameFeedModal');
    }
}

async function submitRenameFeed() {
    const newName = document.getElementById('feedNewName').value.trim();
    if (!newName) return alert('Please enter a feed name');
    if (!state.currentEditFeedId) return;

    try {
        await api(`/feeds/${state.currentEditFeedId}`, {
            method: 'PATCH',
            body: JSON.stringify({ title: newName }),
        });

        closeModal('renameFeedModal');
        state.currentEditFeedId = null;
        loadFeeds();
        loadArticles();
    } catch (err) {
        alert('Error renaming feed: ' + err.message);
    }
}

// Modals
function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function updateFolderSelect() {
    const select = document.getElementById('feedFolder');
    select.innerHTML = '<option value="">No folder</option>' +
        state.folders.map(f => `<option value="${f.id}">${escapeHtml(f.name)}</option>`).join('');
}

async function submitFeed() {
    const url = document.getElementById('feedUrl').value.trim();
    const folderId = document.getElementById('feedFolder').value;

    if (!url) return alert('Please enter a feed URL');

    const btn = document.getElementById('submitFeed');
    btn.classList.add('loading');
    btn.textContent = 'Adding...';

    try {
        await api('/feeds', {
            method: 'POST',
            body: JSON.stringify({
                url,
                folder_id: folderId ? parseInt(folderId) : null,
            }),
        });

        closeModal('addFeedModal');
        document.getElementById('feedUrl').value = '';
        document.getElementById('feedFolder').value = '';

        loadFeeds();
        loadFolders();
        loadArticles();
    } catch (err) {
        alert('Error adding feed: ' + err.message);
    } finally {
        btn.classList.remove('loading');
        btn.textContent = 'Add Feed';
    }
}

async function submitFolder() {
    const name = document.getElementById('folderName').value.trim();
    if (!name) return alert('Please enter a folder name');

    try {
        await api('/folders', {
            method: 'POST',
            body: JSON.stringify({ name }),
        });

        closeModal('addFolderModal');
        document.getElementById('folderName').value = '';

        loadFolders();
    } catch (err) {
        alert('Error creating folder: ' + err.message);
    }
}

// Helper
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Nav items
    document.querySelectorAll('.nav-item').forEach(el => {
        el.addEventListener('click', () => selectView(el.dataset.view));
    });

    // Buttons
    document.getElementById('refreshAll').addEventListener('click', refreshAllFeeds);
    document.getElementById('addFeed').addEventListener('click', () => openModal('addFeedModal'));
    document.getElementById('addFolder').addEventListener('click', () => openModal('addFolderModal'));
    document.getElementById('markAllRead').addEventListener('click', markAllRead);
    document.getElementById('toggleUnread').addEventListener('click', toggleUnreadFilter);
    document.getElementById('submitFeed').addEventListener('click', submitFeed);
    document.getElementById('submitFolder').addEventListener('click', submitFolder);
    document.getElementById('submitRenameFeed').addEventListener('click', submitRenameFeed);

    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(el => {
        el.addEventListener('click', () => {
            el.closest('.modal').classList.remove('active');
        });
    });

    // Close modals on backdrop click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('active');
        });
    });

    // Enter key in inputs
    document.getElementById('feedUrl').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitFeed();
    });
    document.getElementById('folderName').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitFolder();
    });
    document.getElementById('feedNewName').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitRenameFeed();
    });

    // Initial load
    loadFolders();
    loadFeeds();
    loadArticles();
});
