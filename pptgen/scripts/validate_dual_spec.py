#!/usr/bin/env python3
"""Validate pptgen's canonical dual-output specification."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image


STAGES = ("plan", "assets", "rendered")
PATH_FIELDS = (
    "composite_image",
    "clean_background",
    "image_render",
    "editable_render",
)
ASSET_FIELDS = ("composite_image", "clean_background")
RENDER_FIELDS = ("image_render", "editable_render")
ALIGNMENTS = {"left", "center", "right", "justify"}
VERTICAL_ALIGNMENTS = {"top", "middle", "bottom"}
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\Z")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _inside_root(root: Path, relative: Any) -> bool:
    if not isinstance(relative, str) or not relative.strip():
        return False
    candidate = Path(relative)
    if candidate.is_absolute():
        return False
    try:
        (root / candidate).resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _read_dimensions(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        image.verify()
        return image.size


def validate_spec(data: Any, root: Path, stage: str = "plan") -> list[str]:
    """Return human-readable validation errors; an empty list means valid."""
    errors: list[str] = []
    root = root.resolve()
    if stage not in STAGES:
        return [f"stage must be one of: {', '.join(STAGES)}"]
    if not isinstance(data, dict):
        return ["spec root must be a JSON object"]

    if data.get("version") != 1:
        errors.append("version must be 1")
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        errors.append("title must not be empty")

    slide_size = data.get("slide_size")
    if not isinstance(slide_size, dict):
        errors.append("slide_size must be an object")
    else:
        for key in ("width", "height"):
            value = slide_size.get(key)
            if not _is_number(value) or value <= 0:
                errors.append(f"slide_size.{key} must be a positive number")

    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return errors + ["slides must be a non-empty array"]

    numbers = [slide.get("slide") for slide in slides if isinstance(slide, dict)]
    expected_numbers = list(range(1, len(slides) + 1))
    if numbers != expected_numbers:
        errors.append("slide numbers must be unique, ordered, and continuous from 1")

    for index, slide in enumerate(slides, start=1):
        prefix = f"slide {index}"
        if not isinstance(slide, dict):
            errors.append(f"{prefix} must be an object")
            continue
        slide_number = slide.get("slide")
        if not isinstance(slide_number, int) or isinstance(slide_number, bool):
            errors.append(f"{prefix}: slide must be an integer")
        if not isinstance(slide.get("page_type"), str) or not slide["page_type"].strip():
            errors.append(f"{prefix}: page_type must not be empty")

        for field in PATH_FIELDS:
            value = slide.get(field)
            if not _inside_root(root, value):
                errors.append(
                    f"{prefix}: {field} must be a non-empty relative path and must stay inside the spec directory"
                )

        elements = slide.get("text_elements")
        if not isinstance(elements, list) or not elements:
            errors.append(f"{prefix}: text_elements must be a non-empty array")
            elements = []
        seen_ids: set[str] = set()
        for element_index, element in enumerate(elements, start=1):
            element_prefix = f"{prefix} text element {element_index}"
            if not isinstance(element, dict):
                errors.append(f"{element_prefix} must be an object")
                continue
            element_id = element.get("id")
            if not isinstance(element_id, str) or not element_id.strip():
                errors.append(f"{element_prefix}: id must not be empty")
            elif element_id.strip() in seen_ids:
                errors.append(f"{prefix}: duplicate text element id '{element_id.strip()}'")
            else:
                seen_ids.add(element_id.strip())
            text = element.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{element_prefix}: text must not be empty")
            if not isinstance(element.get("role"), str) or not element["role"].strip():
                errors.append(f"{element_prefix}: role must not be empty")

            box: dict[str, float] = {}
            for key in ("x", "y", "w", "h"):
                value = element.get(key)
                if not _is_number(value):
                    errors.append(f"{element_prefix}: {key} must be numeric")
                else:
                    box[key] = float(value)
            if len(box) == 4:
                if box["x"] < 0 or box["y"] < 0 or box["w"] <= 0 or box["h"] <= 0:
                    errors.append(f"{element_prefix}: text box coordinates and size are invalid")
                elif box["x"] + box["w"] > 1 or box["y"] + box["h"] > 1:
                    errors.append(f"{element_prefix}: text box is outside normalized slide bounds")

            font_size = element.get("font_size_pt")
            if not _is_number(font_size) or font_size <= 0:
                errors.append(f"{element_prefix}: font_size_pt must be positive")
            font_family = element.get("font_family")
            if not isinstance(font_family, str) or not font_family.strip():
                errors.append(f"{element_prefix}: font_family must not be empty")
            if not isinstance(element.get("bold"), bool):
                errors.append(f"{element_prefix}: bold must be a Boolean")
            color = element.get("color")
            if not isinstance(color, str) or HEX_COLOR.fullmatch(color) is None:
                errors.append(f"{element_prefix}: color must use #RRGGBB")
            if element.get("align") not in ALIGNMENTS:
                errors.append(f"{element_prefix}: align must be one of {sorted(ALIGNMENTS)}")
            if element.get("valign") not in VERTICAL_ALIGNMENTS:
                errors.append(
                    f"{element_prefix}: valign must be one of {sorted(VERTICAL_ALIGNMENTS)}"
                )

        if stage in ("assets", "rendered"):
            dimensions: dict[str, tuple[int, int]] = {}
            for field in ASSET_FIELDS:
                value = slide.get(field)
                if not _inside_root(root, value):
                    continue
                path = root / value
                if not path.is_file():
                    errors.append(f"{prefix}: missing {field}: {value}")
                    continue
                try:
                    dimensions[field] = _read_dimensions(path)
                except Exception as exc:
                    errors.append(f"{prefix}: unreadable {field}: {exc}")
            if len(dimensions) == 2 and len(set(dimensions.values())) != 1:
                errors.append(f"{prefix}: composite and clean background dimensions differ")
            if (
                isinstance(slide_size, dict)
                and _is_number(slide_size.get("width"))
                and _is_number(slide_size.get("height"))
                and slide_size["width"] > 0
                and slide_size["height"] > 0
            ):
                expected_ratio = slide_size["width"] / slide_size["height"]
                for field, (width, height) in dimensions.items():
                    if abs(width / height - expected_ratio) > 0.002:
                        errors.append(f"{prefix}: {field} aspect ratio differs from slide_size")

        if stage == "rendered":
            dimensions = {}
            for field in RENDER_FIELDS:
                value = slide.get(field)
                if not _inside_root(root, value):
                    continue
                path = root / value
                if not path.is_file():
                    errors.append(f"{prefix}: missing {field}: {value}")
                    continue
                try:
                    dimensions[field] = _read_dimensions(path)
                except Exception as exc:
                    errors.append(f"{prefix}: unreadable {field}: {exc}")
            if len(dimensions) == 2 and len(set(dimensions.values())) != 1:
                errors.append(f"{prefix}: image and editable render dimensions differ")
            if (
                isinstance(slide_size, dict)
                and _is_number(slide_size.get("width"))
                and _is_number(slide_size.get("height"))
                and slide_size["width"] > 0
                and slide_size["height"] > 0
            ):
                expected_ratio = slide_size["width"] / slide_size["height"]
                for field, (width, height) in dimensions.items():
                    if abs(width / height - expected_ratio) > 0.002:
                        errors.append(f"{prefix}: {field} aspect ratio differs from slide_size")

    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="Path to dual_spec.json")
    parser.add_argument("--stage", choices=STAGES, default="plan")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: cannot read spec: {exc}")
        return 1
    errors = validate_spec(data, args.spec.parent, args.stage)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID: {args.stage} stage ({len(data['slides'])} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
