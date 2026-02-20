#!/usr/bin/env python3
"""
Check that any file in dist/ contains the expected version string.
Usage: python scripts/check_dist_version.py 0.1.5
Exits with 0 if ok, 1 if mismatch or no files.
"""
import glob
import os
import sys

if len(sys.argv) != 2:
    print("Usage: check_dist_version.py VERSION", file=sys.stderr)
    sys.exit(2)

v = sys.argv[1]
files = glob.glob("dist/*")
print("dist files:", files)
if not files:
    print("ERROR: dist/ is empty", file=sys.stderr)
    sys.exit(1)

# Build the substring to search for: -<version>-
needle = "-{}-".format(v)
found = False
for f in files:
    name = os.path.basename(f)
    if needle in name:
        found = True
        break

if not found:
    print("ERROR: Built artifacts do not contain version {}".format(v), file=sys.stderr)
    sys.exit(1)

print("OK: artifacts contain version {}".format(v))
sys.exit(0)
