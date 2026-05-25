#!/usr/bin/env python3
"""Emit a compact JSONL snapshot of Obsidian Inbox notes.

The script is intentionally read-only. It helps Codex triage notes by exposing
basic metadata without moving, deleting, or modifying anything.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IGNORE_PARTS = {"Empty Notes", "Duplicate Candidates", "Needs Review"}
TAG_RE = re.compile(r"(?<!\w)#([\w/-]+)")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text)


def words(text: str) -> list[str]:
    return re.findall(r"[\w\u4e00-\u9fff]+", text)


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def snapshot_note(path: Path, vault: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(raw)
    body_words = words(body)
    tags = sorted(set(TAG_RE.findall(raw)))
    wikilinks = sorted(set(link.split("|", 1)[0].split("#", 1)[0].strip() for link in WIKILINK_RE.findall(raw)))
    first_line = first_nonempty_line(body)
    title = path.stem
    if first_line.startswith("#"):
        title = first_line.lstrip("#").strip() or title

    signal_chars = re.sub(r"[\s#\[\]\-_*`>]", "", body)
    near_empty = len(body_words) < 12 and len(wikilinks) <= 2 and len(signal_chars) < 80

    return {
        "path": str(path.relative_to(vault)),
        "title": title,
        "word_count": len(body_words),
        "near_empty": near_empty,
        "tags": tags,
        "wikilinks": wikilinks[:30],
        "first_line": first_line[:160],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot Markdown notes in an Obsidian Inbox.")
    parser.add_argument("vault", type=Path, help="Path to the Obsidian vault root")
    parser.add_argument("--inbox", default="99 - Inbox", help="Inbox folder relative to the vault root")
    args = parser.parse_args()

    vault = args.vault.expanduser().resolve()
    inbox = vault / args.inbox
    if not inbox.is_dir():
        raise SystemExit(f"Inbox folder not found: {inbox}")

    for path in sorted(inbox.rglob("*.md")):
        rel_parts = path.relative_to(inbox).parts
        if any(part in IGNORE_PARTS for part in rel_parts[:-1]):
            continue
        print(json.dumps(snapshot_note(path, vault), ensure_ascii=False, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
