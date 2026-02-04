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
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
APP_DIR = DIST_DIR / "RSS Reader.app"
PLIST_PATH = APP_DIR / "Contents" / "Info.plist"
DMG_PATH = DIST_DIR / "RSS Reader.dmg"
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
        print(f"ERROR: {description} failed with code {result.returncode}")
        return False
    return True


def clean_previous_build():
    """Remove previous build artifacts."""
    print("\nCleaning previous build artifacts...")

    for path in [DIST_DIR, BUILD_DIR]:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed: {path}")


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
        print(f"ERROR: Info.plist not found at {PLIST_PATH}")
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
        print(f"ERROR: Failed to update Info.plist: {e}")
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
        print("ERROR: DMG creation failed")
        return False

    # Get DMG size
    size_mb = DMG_PATH.stat().st_size / (1024 * 1024)
    print(f"Created: {DMG_PATH} ({size_mb:.1f} MB)")
    return True


def print_summary(include_dmg: bool):
    """Print build summary with file locations."""
    print("\n" + "="*60)
    print("BUILD COMPLETE")
    print("="*60)

    print(f"\nVersion: {VERSION}")

    if APP_DIR.exists():
        print(f"Application: {APP_DIR}")

    if include_dmg and DMG_PATH.exists():
        size_mb = DMG_PATH.stat().st_size / (1024 * 1024)
        print(f"DMG Image:   {DMG_PATH} ({size_mb:.1f} MB)")

    print("\nTo install:")
    print("  1. Open the DMG file")
    print("  2. Drag 'RSS Reader' to Applications")
    print("  3. Launch from Applications folder")
    print("\nNote: On first launch, you may need to right-click the app")
    print("      and select 'Open' to bypass Gatekeeper.")
    print("\nData location: ~/Library/Application Support/RSS Reader/")


def main():
    parser = argparse.ArgumentParser(description="Build RSS Reader macOS application")
    parser.add_argument("--no-dmg", action="store_true", help="Skip DMG creation")
    parser.add_argument("--skip-build", action="store_true", help="Skip PyInstaller build (only update plist)")
    args = parser.parse_args()

    print(f"RSS Reader Build Script - v{VERSION}")
    print("="*60)

    # Check PyInstaller is available
    if not args.skip_build:
        try:
            subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: PyInstaller not found. Install with:")
            print("  pip install -r requirements-dev.txt")
            sys.exit(1)

    # Check we're in the right directory
    if not (PROJECT_ROOT / "main.py").exists():
        print("ERROR: main.py not found. Run from project root.")
        sys.exit(1)

    # Clean previous build
    if not args.skip_build:
        clean_previous_build()

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
            print("WARNING: DMG creation failed, but app was built successfully.")

    print_summary(include_dmg=not args.no_dmg)


if __name__ == "__main__":
    main()
