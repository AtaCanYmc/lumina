#!/usr/bin/env python3
"""
Simple script to bump the version in pyproject.toml inside the [project] section.
Usage: python scripts/bump_version.py 0.1.5
Exits with non-zero on failure.
"""
import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: bump_version.py NEW_VERSION", file=sys.stderr)
    sys.exit(2)

new_version = sys.argv[1]
file = Path("pyproject.toml")
if not file.exists():
    print("pyproject.toml not found", file=sys.stderr)
    sys.exit(3)

s = file.read_text(encoding="utf-8")
pattern = re.compile(r'(\[project\][\s\S]*?\nversion\s*=\s*")([^"]+)(")', re.M)
match = pattern.search(s)
if not match:
    print("Could not find [project].version in pyproject.toml", file=sys.stderr)
    sys.exit(4)

current = match.group(2)
if current == new_version:
    print(f"No change: version already {new_version}")
    sys.exit(0)

s2 = pattern.sub(r"\1" + new_version + r"\3", s, count=1)
file.write_text(s2, encoding="utf-8")
print(f"Bumped version: {current} -> {new_version}")
sys.exit(0)
