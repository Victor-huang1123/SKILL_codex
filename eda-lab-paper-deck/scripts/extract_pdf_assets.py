#!/usr/bin/env python3
"""Extract paper figures/tables for EDA Lab paper decks.

Typical workflow:
  1. Render candidate PDF pages to PNG.
  2. Inspect the rendered page and crop a tight figure/table image.
  3. Insert the cropped PNG with scripts/build_deck.py.

Requires:
  pip install pymupdf pillow
"""

from __future__ import annotations

import argparse
from pathlib import Path


def require_fitz():
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install pymupdf") from exc
    return fitz


def require_pillow():
    try:
        from PIL import Image  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install pillow") from exc
    return Image


def parse_pages(spec: str | None, page_count: int) -> list[int]:
    if spec is None or spec.lower() == "all":
        return list(range(1, page_count + 1))

    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))

    unique_pages = sorted(set(pages))
    bad_pages = [page for page in unique_pages if page < 1 or page > page_count]
    if bad_pages:
        raise SystemExit(f"Page(s) out of range 1-{page_count}: {bad_pages}")
    return unique_pages


def parse_bbox(text: str) -> tuple[float, float, float, float]:
    parts = [float(item.strip()) for item in text.split(",")]
    if len(parts) != 4:
        raise SystemExit("--bbox must be x1,y1,x2,y2")
    x1, y1, x2, y2 = parts
    if x2 <= x1 or y2 <= y1:
        raise SystemExit("--bbox requires x2 > x1 and y2 > y1")
    return x1, y1, x2, y2


def command_render(args: argparse.Namespace) -> None:
    fitz = require_fitz()
    pdf_path = Path(args.pdf)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    zoom = args.dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    for page_no in parse_pages(args.pages, doc.page_count):
        page = doc[page_no - 1]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        out_path = out_dir / f"page_{page_no:03d}.png"
        pix.save(out_path)
        print(out_path)


def command_extract_images(args: argparse.Namespace) -> None:
    fitz = require_fitz()
    pdf_path = Path(args.pdf)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    for page_no in parse_pages(args.pages, doc.page_count):
        page = doc[page_no - 1]
        for idx, image_info in enumerate(page.get_images(full=True), start=1):
            xref = image_info[0]
            extracted = doc.extract_image(xref)
            width = int(extracted.get("width", 0))
            height = int(extracted.get("height", 0))
            if width < args.min_width or height < args.min_height:
                continue
            ext = extracted.get("ext", "png")
            out_path = out_dir / f"page_{page_no:03d}_image_{idx:02d}.{ext}"
            out_path.write_bytes(extracted["image"])
            print(out_path)


def command_crop(args: argparse.Namespace) -> None:
    Image = require_pillow()
    image_path = Path(args.image)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(image_path)
    x1, y1, x2, y2 = parse_bbox(args.bbox)
    if args.normalized:
        width, height = image.size
        x1, x2 = x1 * width, x2 * width
        y1, y2 = y1 * height, y2 * height
    crop = image.crop((round(x1), round(y1), round(x2), round(y2)))
    crop.save(out_path)
    print(out_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Render PDF pages to PNG")
    render.add_argument("pdf")
    render.add_argument("--pages", default="all", help="1-indexed pages, e.g. 2,4-6")
    render.add_argument("--dpi", type=int, default=220)
    render.add_argument("--out", default="figures/pages")
    render.set_defaults(func=command_render)

    extract = subparsers.add_parser("extract-images", help="Extract embedded PDF raster images")
    extract.add_argument("pdf")
    extract.add_argument("--pages", default="all", help="1-indexed pages, e.g. 2,4-6")
    extract.add_argument("--out", default="figures/raw")
    extract.add_argument("--min-width", type=int, default=300)
    extract.add_argument("--min-height", type=int, default=200)
    extract.set_defaults(func=command_extract_images)

    crop = subparsers.add_parser("crop", help="Crop a rendered page/image")
    crop.add_argument("image")
    crop.add_argument("--bbox", required=True, help="x1,y1,x2,y2 in pixels by default")
    crop.add_argument("--normalized", action="store_true", help="Treat bbox values as 0-1 fractions")
    crop.add_argument("--out", required=True)
    crop.set_defaults(func=command_crop)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
