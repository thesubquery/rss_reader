# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for RSS Reader macOS application.
Build with: pyinstaller rss_reader.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root directory
project_root = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Bundle static files
        ('static/index.html', 'static'),
        ('static/styles.css', 'static'),
        ('static/app.js', 'static'),
    ],
    hiddenimports=[
        # FastAPI and dependencies
        'uvicorn.logging',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        # SQLAlchemy
        'sqlalchemy.dialects.sqlite',
        # Webview
        'webview.platforms.cocoa',
        # aiohttp for feed fetching
        'aiohttp',
        # Encodings
        'encodings.idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RSS Reader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window on macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RSS Reader',
)

app = BUNDLE(
    coll,
    name='RSS Reader.app',
    icon='icon.icns',
    bundle_identifier='com.rssreader.app',
    info_plist={
        'CFBundleName': 'RSS Reader',
        'CFBundleDisplayName': 'RSS Reader',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
)
