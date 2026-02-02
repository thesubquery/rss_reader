#!/usr/bin/env python3
"""
Bump the version number in app/version.py.

Usage:
    python scripts/bump_version.py          # bump patch: 1.0.0 -> 1.0.1
    python scripts/bump_version.py --minor  # bump minor: 1.0.0 -> 1.1.0
    python scripts/bump_version.py --major  # bump major: 1.0.0 -> 2.0.0
"""

import argparse
import re
import sys
from pathlib import Path

# Path to version file relative to project root
VERSION_FILE = Path(__file__).parent.parent / "app" / "version.py"


def get_current_version() -> str:
    """Read current version from version.py."""
    content = VERSION_FILE.read_text()
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find VERSION in {VERSION_FILE}")
    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse version string into (major, minor, patch) tuple."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}. Expected MAJOR.MINOR.PATCH")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to bump_type (major, minor, or patch)."""
    major, minor, patch = parse_version(version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def write_version(new_version: str) -> None:
    """Write new version to version.py."""
    content = VERSION_FILE.read_text()
    new_content = re.sub(
        r'(VERSION\s*=\s*["\'])[^"\']+(["\'])',
        rf'\g<1>{new_version}\g<2>',
        content
    )
    VERSION_FILE.write_text(new_content)


def main():
    parser = argparse.ArgumentParser(description="Bump the app version number")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--major", action="store_true", help="Bump major version (X.0.0)")
    group.add_argument("--minor", action="store_true", help="Bump minor version (x.X.0)")
    group.add_argument("--patch", action="store_true", help="Bump patch version (x.x.X) [default]")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")

    args = parser.parse_args()

    if args.major:
        bump_type = "major"
    elif args.minor:
        bump_type = "minor"
    else:
        bump_type = "patch"

    try:
        current = get_current_version()
        new = bump_version(current, bump_type)

        if args.dry_run:
            print(f"Would bump version: {current} -> {new}")
        else:
            write_version(new)
            print(f"Bumped version: {current} -> {new}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
