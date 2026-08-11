#!/usr/bin/env python3
"""Create a side-by-side image/editable render contact sheet for review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


BACKGROUND = "#111827"
CARD = "#1F2937"
TEXT = "#F9FAFB"
MUTED = "#D1D5DB"


def _font(size: int) -> ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit(image: Image.Image, width: int) -> Image.Image:
    height = max(1, round(image.height * width / image.width))
    return ImageOps.fit(image.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS)


def _project_path(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"render path must be project-relative: {relative}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"render path escapes project directory: {relative}") from exc
    return resolved


def create_contact_sheet(
    spec_path: Path, output: Path, thumb_width: int = 720, gap: int = 28
) -> Path:
    if thumb_width <= 0:
        raise ValueError("thumb_width must be positive")
    if gap < 0:
        raise ValueError("gap must not be negative")
    spec_path = spec_path.resolve()
    root = spec_path.parent
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    slides = data.get("slides", [])
    if not slides:
        raise ValueError("spec contains no slides")

    rows: list[tuple[int, Image.Image, Image.Image]] = []
    for slide in slides:
        image_path = _project_path(root, slide["image_render"])
        editable_path = _project_path(root, slide["editable_render"])
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        if not editable_path.is_file():
            raise FileNotFoundError(editable_path)
        with Image.open(image_path) as image_render, Image.open(editable_path) as editable_render:
            rows.append(
                (
                    slide["slide"],
                    _fit(image_render, thumb_width),
                    _fit(editable_render, thumb_width),
                )
            )

    title_height = 76
    label_height = 42
    row_gap = 36
    margin = 36
    row_heights = [max(left.height, right.height) + label_height for _, left, right in rows]
    canvas_width = margin * 2 + thumb_width * 2 + gap
    canvas_height = title_height + margin + sum(row_heights) + row_gap * (len(rows) - 1) + margin
    canvas = Image.new("RGB", (canvas_width, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 22), f"{data.get('title', 'PPT')} · 双版本逐页对照", font=_font(28), fill=TEXT)

    y = title_height + margin
    for slide_no, left, right in rows:
        row_height = max(left.height, right.height) + label_height
        draw.rounded_rectangle(
            (margin - 12, y - 12, canvas_width - margin + 12, y + row_height + 12),
            radius=16,
            fill=CARD,
        )
        draw.text((margin, y), f"第 {slide_no} 页 · 图片版", font=_font(20), fill=MUTED)
        draw.text((margin + thumb_width + gap, y), "文字可编辑版", font=_font(20), fill=MUTED)
        canvas.paste(left, (margin, y + label_height))
        canvas.paste(right, (margin + thumb_width + gap, y + label_height))
        y += row_height + row_gap

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--thumb-width", type=int, default=720)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    create_contact_sheet(args.spec, args.output, args.thumb_width)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
