#!/usr/bin/env python3
"""Render 1200×630 social cards for notes that do not already set og-image.

Notes with a figure PNG get that figure letterboxed on the branded cream /
indigo canvas. Notes without a figure get a large-title card. Cards are
committed so the site build does not need this script or Pillow.

Usage:
  python3 scripts/render-og-cards.py
  python3 scripts/render-og-cards.py --slug 2026-08-16-how-the-donor-closes-the-gap
  python3 scripts/render-og-cards.py --force
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    sys.exit(
        "render-og-cards: Pillow is required to generate cards "
        f"(`pip install Pillow`). {exc}"
    )

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
IMAGES = ROOT / "images"

W, H = 1200, 630
CREAM = (245, 242, 234)
INDIGO = (70, 92, 155)
INK = (26, 29, 43)
SLATE = (77, 83, 102)
RULE = (204, 211, 229)
BAR_W = 28
CONTENT_LEFT = 86
CONTENT_RIGHT = 80

MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)

FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/macos/Inter-Bold.ttf"),
)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[text.find("\n") + 1 : end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        value = match.group(2)
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        fields[match.group(1)] = value
    return fields


def figure_src(html: str | None) -> str | None:
    if not html:
        return None
    match = re.search(r"""\ssrc=(?:"([^"]+)"|'([^']+)')""", html)
    if not match:
        return None
    return match.group(1) or match.group(2)


def site_path(url: str | None) -> Path | None:
    if not url:
        return None
    if url.startswith("/"):
        return ROOT / url[1:]
    if url.startswith("https://pvjohnston.com/"):
        return ROOT / url[len("https://pvjohnston.com/") :]
    return ROOT / url


def format_date(iso: str | None) -> str | None:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", iso or "")
    if not match:
        return None
    year, month, day = match.groups()
    return f"{int(day)} {MONTHS[int(month) - 1]} {year}"


def kicker(fields: dict[str, str]) -> str:
    kind = fields.get("post-type")
    if kind == "research":
        return "A research note"
    if kind == "understanding":
        return "An understanding note"
    return "A note"


def title_size(title: str) -> int:
    if len(title) > 110:
        return 36
    if len(title) > 80:
        return 42
    if len(title) > 55:
        return 48
    return 56


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [text]
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def ellipsize(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    if draw.textlength(text, font=font) <= max_width:
        return text
    ellipsis = "…"
    while text and draw.textlength(text + ellipsis, font=font) > max_width:
        text = text[:-1]
    return text + ellipsis


def new_canvas() -> Image.Image:
    image = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, BAR_W, H), fill=INDIGO)
    return image


def render_title_card(fields: dict[str, str]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    title = fields.get("title") or "Untitled note"
    font_kicker = load_font(22)
    font_title = load_font(title_size(title))
    font_meta = load_font(24)
    max_width = W - CONTENT_LEFT - CONTENT_RIGHT

    draw.text((CONTENT_LEFT, 72), "pvjohnston.com", font=font_kicker, fill=INDIGO)
    lines = wrap_text(draw, title, font_title, max_width)
    y = 128
    line_gap = int(title_size(title) * 1.18)
    for line in lines[:5]:
        draw.text((CONTENT_LEFT, y), line, font=font_title, fill=INK)
        y += line_gap

    draw.rectangle((CONTENT_LEFT, H - 92, W - CONTENT_RIGHT, H - 89), fill=RULE)
    meta = " · ".join(part for part in (kicker(fields), format_date(fields.get("date"))) if part)
    draw.text((CONTENT_LEFT, H - 72), meta, font=font_meta, fill=SLATE)
    return image


def render_figure_card(fields: dict[str, str], figure_path: Path) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    title = fields.get("title") or "Untitled note"
    font_title = load_font(26)

    box = (64, 28, W - 36, H - 96)
    box_w = box[2] - box[0]
    box_h = box[3] - box[1]
    figure = Image.open(figure_path).convert("RGBA")
    scale = min(box_w / figure.width, box_h / figure.height)
    new_size = (max(1, int(figure.width * scale)), max(1, int(figure.height * scale)))
    figure = figure.resize(new_size, Image.Resampling.LANCZOS)
    x = box[0] + (box_w - figure.width) // 2
    y = box[1] + (box_h - figure.height) // 2
    if figure.mode == "RGBA":
        image.paste(figure, (x, y), figure)
    else:
        image.paste(figure.convert("RGB"), (x, y))

    max_width = W - CONTENT_LEFT - CONTENT_RIGHT
    draw.text(
        (CONTENT_LEFT, H - 72),
        ellipsize(draw, title, font_title, max_width),
        font=font_title,
        fill=INK,
    )
    return image


def list_posts(slug: str | None) -> list[tuple[str, dict[str, str]]]:
    posts = []
    for path in sorted((*POSTS.glob("*.md"), *POSTS.glob("*.markdown"))):
        if slug and path.stem != slug:
            continue
        posts.append((path.stem, parse_front_matter(path.read_text(encoding="utf-8"))))
    return posts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", help="Generate only this post's card")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated cards")
    args = parser.parse_args()

    posts = list_posts(args.slug)
    if args.slug and not posts:
        print(f"no post matching --slug {args.slug}", file=sys.stderr)
        return 1

    wrote = 0
    skipped = 0
    for slug, fields in posts:
        if fields.get("og-image"):
            skipped += 1
            continue
        out = IMAGES / f"{slug}-og.png"
        if out.is_file() and not args.force:
            skipped += 1
            continue
        src = figure_src(fields.get("figure"))
        figure_file = site_path(src)
        if figure_file is not None and figure_file.is_file():
            image = render_figure_card(fields, figure_file)
        else:
            image = render_title_card(fields)
        image.save(out, format="PNG", optimize=True)
        if image.size != (W, H):
            print(f"{out}: wrote {image.size}, expected {W}×{H}", file=sys.stderr)
            return 1
        print(f"wrote {out.relative_to(ROOT)}")
        wrote += 1

    print(f"render-og-cards: wrote {wrote}, skipped {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
