#!/usr/bin/env python3
"""Warn (never fail) when a recipe's **Tags:** line uses a tag outside .github/allowed-tags.txt.

Usage: check_tags.py [recipe.md ...]   (no args = scan every recipes/*.md)
Emits GitHub Actions ::warning annotations.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = [
    l.strip()
    for l in (ROOT / ".github" / "allowed-tags.txt").read_text(encoding="utf-8").splitlines()
    if l.strip() and not l.startswith("#")
]
TAGS_RE = re.compile(r"^\*\*Tags:\*\*\s*(.*)$")


def warn(path, line, msg):
    print(f"::warning file={path},line={line},title=Recipe tags::{msg}")


def check(path):
    rel = path.relative_to(ROOT).as_posix()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = TAGS_RE.match(line.strip())
        if not m:
            continue
        tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
        if not tags:
            warn(rel, n, "Tags line is empty.")
            return 1
        bad = [t for t in tags if t not in ALLOWED]
        if bad:
            warn(rel, n, f"Unknown tag(s): {', '.join(bad)}. Allowed: {', '.join(ALLOWED)}.")
            return 1
        return 0
    warn(rel, 1, "No **Tags:** line found.")
    return 1


def main(argv):
    files = [ROOT / a for a in argv] if argv else sorted((ROOT / "recipes").glob("*.md"))
    files = [f for f in files if f.suffix == ".md" and f.exists()]
    bad = sum(check(f) for f in files)
    print(f"Checked {len(files)} recipe(s): {bad} with tag warnings.")
    return 0  # warning only


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
