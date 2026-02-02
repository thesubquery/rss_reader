#!/usr/bin/env python3
"""
Build the RSS Reader macOS application.

This script:
1. Reads version from app/version.py
2. Runs PyInstaller to create the app bundle
3. Updates Info.plist with the current version
4. Creates a DMG for distribution

Usage:
    python scripts/build_app.py           # Build app and DMG
    python scripts/build_app.py --no-dmg  # Build app only
"""

import argparse
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = PROJECT_ROOT / "dist" / "RSS Reader.app"
PLIST_PATH = APP_DIR / "Contents" / "Info.plist"
DMG_PATH = PROJECT_ROOT / "dist" / "RSS Reader.dmg"
ICON_PATH = PROJECT_ROOT / "icon.icns"

# Add project root to path so we can import app.version
sys.path.insert(0, str(PROJECT_ROOT))
from app.version import VERSION


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n{'='*60}")
    print(f"{description}...")
    print(f"{'='*60}")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"Error: {description} failed with code {result.returncode}")
        return False
    return True


def build_with_pyinstaller() -> bool:
    """Build the app using PyInstaller."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "RSS Reader",
        "--windowed",
        "--icon", str(ICON_PATH),
        "--add-data", "static:static",
        "--add-data", "app:app",
        "--noconfirm",
        "--clean",
        # macOS specific options
        "--osx-bundle-identifier", "com.rssreader.app",
        "main.py"
    ]
    return run_command(cmd, "Building with PyInstaller")


def update_plist() -> bool:
    """Update Info.plist with version from app/version.py."""
    print(f"\n{'='*60}")
    print(f"Updating Info.plist with version {VERSION}...")
    print(f"{'='*60}")

    if not PLIST_PATH.exists():
        print(f"Error: Info.plist not found at {PLIST_PATH}")
        return False

    try:
        with open(PLIST_PATH, "rb") as f:
            plist = plistlib.load(f)

        plist["CFBundleVersion"] = VERSION
        plist["CFBundleShortVersionString"] = VERSION

        with open(PLIST_PATH, "wb") as f:
            plistlib.dump(plist, f)

        print(f"Updated CFBundleVersion to {VERSION}")
        print(f"Updated CFBundleShortVersionString to {VERSION}")
        return True

    except Exception as e:
        print(f"Error updating Info.plist: {e}")
        return False


def create_dmg() -> bool:
    """Create a DMG file for distribution."""
    print(f"\n{'='*60}")
    print("Creating DMG...")
    print(f"{'='*60}")

    # Remove existing DMG
    if DMG_PATH.exists():
        DMG_PATH.unlink()

    # Create DMG using hdiutil
    cmd = [
        "hdiutil", "create",
        "-volname", "RSS Reader",
        "-srcfolder", str(APP_DIR),
        "-ov",
        "-format", "UDZO",
        str(DMG_PATH)
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"Error: DMG creation failed")
        return False

    # Get DMG size
    size_mb = DMG_PATH.stat().st_size / (1024 * 1024)
    print(f"Created: {DMG_PATH} ({size_mb:.1f} MB)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build RSS Reader macOS application")
    parser.add_argument("--no-dmg", action="store_true", help="Skip DMG creation")
    parser.add_argument("--skip-build", action="store_true", help="Skip PyInstaller build (only update plist)")
    args = parser.parse_args()

    print(f"Building RSS Reader v{VERSION}")

    # Build with PyInstaller
    if not args.skip_build:
        if not build_with_pyinstaller():
            sys.exit(1)

    # Update Info.plist
    if not update_plist():
        sys.exit(1)

    # Create DMG
    if not args.no_dmg:
        if not create_dmg():
            sys.exit(1)

    print(f"\n{'='*60}")
    print("Build complete!")
    print(f"{'='*60}")
    print(f"App: {APP_DIR}")
    if not args.no_dmg:
        print(f"DMG: {DMG_PATH}")
    print(f"Version: {VERSION}")


if __name__ == "__main__":
    main()
