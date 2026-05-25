#!/usr/bin/env python3
"""List or replace text nodes in one PowerPoint slide without touching formatting."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile
from html import unescape
from pathlib import Path
from xml.sax.saxutils import escape


TEXT_RE = re.compile(r"<a:t>(.*?)</a:t>")


def slide_name(slide_number: int) -> str:
    if slide_number < 1:
        raise SystemExit("--slide must be 1 or greater")
    return f"ppt/slides/slide{slide_number}.xml"


def list_text(pptx: Path, slide_number: int) -> None:
    member = slide_name(slide_number)
    with zipfile.ZipFile(pptx) as deck:
        xml = deck.read(member).decode("utf-8")
    for index, raw in enumerate(TEXT_RE.findall(xml)):
        print(f"{index}: {unescape(raw)}")


def replace_text(pptx: Path, slide_number: int, replacements: dict[str, str], backup_tag: str) -> Path:
    member = slide_name(slide_number)
    backup = pptx.with_name(f"{pptx.stem}.before_{backup_tag}_edit{pptx.suffix}")
    if not backup.exists():
        shutil.copy2(pptx, backup)

    fd, tmp_name = tempfile.mkstemp(suffix=".pptx")
    os.close(fd)
    tmp = Path(tmp_name)

    replaced: dict[str, int] = {old: 0 for old in replacements}
    with zipfile.ZipFile(pptx, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == member:
                xml = data.decode("utf-8")
                for old, new in replacements.items():
                    old_node = f"<a:t>{escape(old)}</a:t>"
                    new_node = f"<a:t>{escape(new)}</a:t>"
                    count = xml.count(old_node)
                    replaced[old] = count
                    xml = xml.replace(old_node, new_node)
                data = xml.encode("utf-8")
            zout.writestr(item, data)

    shutil.copy2(tmp, pptx)
    tmp.unlink()

    missing = [old for old, count in replaced.items() if count == 0]
    if missing:
        print("Warning: no exact match for:")
        for old in missing:
            print(f"- {old}")
    print(f"Updated {pptx}")
    print(f"Backup: {backup}")
    return backup


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path, nargs="?", help="PPTX file to edit")
    parser.add_argument("--slide", type=int, required=True, help="1-based slide number")
    parser.add_argument("--list", action="store_true", help="List text nodes on the slide")
    parser.add_argument("--replace-json", help="JSON object mapping exact old text to new text")
    parser.add_argument("--backup-tag", default="text", help="Backup filename tag")
    args = parser.parse_args()

    if not args.pptx:
        raise SystemExit("pptx path is required")
    if args.list:
        list_text(args.pptx, args.slide)
        return
    if not args.replace_json:
        raise SystemExit("--replace-json is required unless --list is used")
    replacements = json.loads(args.replace_json)
    if not isinstance(replacements, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in replacements.items()):
        raise SystemExit("--replace-json must be a JSON object of string keys and values")
    replace_text(args.pptx, args.slide, replacements, args.backup_tag)


if __name__ == "__main__":
    main()
