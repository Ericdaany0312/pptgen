import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = SKILL_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_script("validate_dual_spec")


def base_spec():
    return {
        "version": 1,
        "title": "测试演示",
        "slide_size": {"width": 1920, "height": 1080},
        "slides": [
            {
                "slide": 1,
                "page_type": "cover",
                "composite_image": "composite/slide_01.png",
                "clean_background": "backgrounds/slide_01.png",
                "image_render": "rendered/image/slide_01.png",
                "editable_render": "rendered/editable/slide_01.png",
                "text_elements": [
                    {
                        "id": "title",
                        "text": "准确标题",
                        "role": "title",
                        "x": 0.1,
                        "y": 0.1,
                        "w": 0.8,
                        "h": 0.2,
                        "font_family": "Microsoft YaHei",
                        "font_size_pt": 36,
                        "bold": True,
                        "color": "#FFFFFF",
                        "align": "center",
                        "valign": "middle",
                    }
                ],
            }
        ],
    }


class ValidateDualSpecTests(unittest.TestCase):
    def test_valid_plan_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(base_spec(), Path(tmp), "plan")
        self.assertEqual(errors, [])

    def test_slide_numbers_must_be_continuous_and_unique(self):
        spec = base_spec()
        duplicate = dict(spec["slides"][0])
        duplicate["page_type"] = "content"
        spec["slides"].append(duplicate)
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("slide numbers" in error for error in errors))

    def test_slide_number_must_be_integer_not_boolean(self):
        spec = base_spec()
        spec["slides"][0]["slide"] = True
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("slide must be an integer" in error for error in errors))

    def test_exact_text_must_not_be_empty(self):
        spec = base_spec()
        spec["slides"][0]["text_elements"][0]["text"] = "   "
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("text must not be empty" in error for error in errors))

    def test_text_box_must_stay_inside_slide(self):
        spec = base_spec()
        spec["slides"][0]["text_elements"][0]["x"] = 0.8
        spec["slides"][0]["text_elements"][0]["w"] = 0.4
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("outside normalized slide bounds" in error for error in errors))

    def test_relative_paths_cannot_escape_spec_directory(self):
        spec = base_spec()
        spec["slides"][0]["composite_image"] = "../escape.png"
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("must stay inside the spec directory" in error for error in errors))

    def test_assets_stage_requires_both_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(base_spec(), Path(tmp), "assets")
        self.assertTrue(any("missing composite_image" in error for error in errors))
        self.assertTrue(any("missing clean_background" in error for error in errors))

    def test_rendered_stage_rejects_dimension_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = base_spec()
            for field in ("composite_image", "clean_background"):
                path = root / spec["slides"][0][field]
                path.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (1920, 1080), "white").save(path)
            image_path = root / spec["slides"][0]["image_render"]
            editable_path = root / spec["slides"][0]["editable_render"]
            image_path.parent.mkdir(parents=True, exist_ok=True)
            editable_path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (1920, 1080), "white").save(image_path)
            Image.new("RGB", (1280, 720), "white").save(editable_path)
            errors = validator.validate_spec(spec, root, "rendered")
        self.assertTrue(any("render dimensions differ" in error for error in errors))

    def test_assets_stage_rejects_wrong_aspect_ratio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = base_spec()
            for field in ("composite_image", "clean_background"):
                path = root / spec["slides"][0][field]
                path.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (1200, 900), "white").save(path)
            errors = validator.validate_spec(spec, root, "assets")
        self.assertTrue(any("aspect ratio differs" in error for error in errors))

    def test_color_must_be_valid_hex(self):
        spec = base_spec()
        spec["slides"][0]["text_elements"][0]["color"] = "#NOTHEX"
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("color must use #RRGGBB" in error for error in errors))

    def test_font_family_and_bold_are_typed(self):
        spec = base_spec()
        element = spec["slides"][0]["text_elements"][0]
        element["font_family"] = ""
        element["bold"] = "yes"
        with tempfile.TemporaryDirectory() as tmp:
            errors = validator.validate_spec(spec, Path(tmp), "plan")
        self.assertTrue(any("font_family must not be empty" in error for error in errors))
        self.assertTrue(any("bold must be a Boolean" in error for error in errors))

    def test_cli_returns_nonzero_for_invalid_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "dual_spec.json"
            invalid = base_spec()
            invalid["slides"][0]["text_elements"] = []
            path.write_text(json.dumps(invalid), encoding="utf-8")
            result = validator.main(["--spec", str(path), "--stage", "plan"])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
