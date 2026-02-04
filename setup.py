"""
Setup script for creating RSS Reader macOS application.
Run: python setup.py py2app
"""
from setuptools import setup
from app.version import VERSION

APP = ['main.py']
DATA_FILES = [('static', [
    'static/index.html',
    'static/styles.css',
    'static/app.js',
])]
OPTIONS = {
    'argv_emulation': False,
    # 'iconfile': 'icon.icns',  # Add your own icon file here
    'plist': {
        'CFBundleName': 'RSS Reader',
        'CFBundleDisplayName': 'RSS Reader',
        'CFBundleIdentifier': 'com.rssreader.app',
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'NSHighResolutionCapable': True,
    },
    'packages': ['app', 'uvicorn', 'fastapi', 'sqlalchemy', 'feedparser',
                 'webview', 'aiohttp', 'starlette', 'pydantic'],
    'includes': ['webview', 'uvicorn.logging', 'uvicorn.protocols.http',
                 'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl',
                 'uvicorn.lifespan', 'uvicorn.lifespan.on'],
}

setup(
    name='RSS Reader',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
