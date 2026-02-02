#!/usr/bin/env python3
"""
Build script for RSS Reader macOS application.

Creates:
1. RSS Reader.app - Standalone macOS application
2. RSS Reader.dmg - Distributable disk image

Usage:
    python scripts/build_app.py
"""

import subprocess
import shutil
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
APP_NAME = "RSS Reader"
DMG_NAME = f"{APP_NAME}.dmg"


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
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


def build_app():
    """Build the application using PyInstaller."""
    return run_command(
        ["pyinstaller", "--clean", "rss_reader.spec"],
        "Building application with PyInstaller"
    )


def create_dmg():
    """Create a DMG disk image for distribution."""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    dmg_path = DIST_DIR / DMG_NAME

    if not app_path.exists():
        print(f"ERROR: Application not found at {app_path}")
        return False

    # Remove existing DMG if present
    if dmg_path.exists():
        dmg_path.unlink()

    # Create DMG using hdiutil
    return run_command(
        [
            "hdiutil", "create",
            "-volname", APP_NAME,
            "-srcfolder", str(app_path),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ],
        "Creating DMG disk image"
    )


def print_summary():
    """Print build summary with file locations."""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    dmg_path = DIST_DIR / DMG_NAME

    print("\n" + "="*60)
    print("BUILD COMPLETE")
    print("="*60)

    if app_path.exists():
        print(f"\nApplication: {app_path}")

    if dmg_path.exists():
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"DMG Image:   {dmg_path} ({size_mb:.1f} MB)")

    print("\nTo install:")
    print("  1. Open the DMG file")
    print("  2. Drag 'RSS Reader' to Applications")
    print("  3. Launch from Applications folder")
    print("\nNote: On first launch, you may need to right-click the app")
    print("      and select 'Open' to bypass Gatekeeper.")
    print("\nData location: ~/Library/Application Support/RSS Reader/")


def main():
    """Main build process."""
    print("RSS Reader Build Script")
    print("="*60)

    # Check PyInstaller is available
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: PyInstaller not found. Install with:")
        print("  pip install pyinstaller")
        sys.exit(1)

    # Check we're in the right directory
    if not (PROJECT_ROOT / "main.py").exists():
        print("ERROR: main.py not found. Run from project root.")
        sys.exit(1)

    # Build process
    clean_previous_build()

    if not build_app():
        sys.exit(1)

    if not create_dmg():
        print("WARNING: DMG creation failed, but app was built successfully.")

    print_summary()


if __name__ == "__main__":
    main()
