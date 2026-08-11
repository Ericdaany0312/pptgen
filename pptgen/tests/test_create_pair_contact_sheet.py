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


contact_sheet = load_script("create_pair_contact_sheet")


class PairContactSheetTests(unittest.TestCase):
    def test_creates_labeled_side_by_side_review_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "rendered/image/slide_01.png"
            right = root / "rendered/editable/slide_01.png"
            left.parent.mkdir(parents=True)
            right.parent.mkdir(parents=True)
            Image.new("RGB", (1600, 900), "#21409A").save(left)
            Image.new("RGB", (1600, 900), "#F0A000").save(right)
            spec = {
                "version": 1,
                "title": "测试",
                "slide_size": {"width": 1920, "height": 1080},
                "slides": [
                    {
                        "slide": 1,
                        "image_render": str(left.relative_to(root)),
                        "editable_render": str(right.relative_to(root)),
                    }
                ],
            }
            spec_path = root / "dual_spec.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            output = root / "review/pairs.png"
            contact_sheet.create_contact_sheet(spec_path, output, thumb_width=640)

            self.assertTrue(output.exists())
            with Image.open(output) as rendered:
                self.assertGreater(rendered.width, 1280)
                self.assertGreater(rendered.height, 360)
                self.assertGreater(len(rendered.getcolors(maxcolors=1_000_000)), 3)

    def test_rejects_missing_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "dual_spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "title": "测试",
                        "slide_size": {"width": 1920, "height": 1080},
                        "slides": [
                            {
                                "slide": 1,
                                "image_render": "missing-image.png",
                                "editable_render": "missing-editable.png",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(FileNotFoundError):
                contact_sheet.create_contact_sheet(spec_path, root / "pairs.png")

    def test_rejects_render_path_outside_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "dual_spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "title": "测试",
                        "slide_size": {"width": 1920, "height": 1080},
                        "slides": [
                            {
                                "slide": 1,
                                "image_render": "../outside.png",
                                "editable_render": "rendered/editable/slide_01.png",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                contact_sheet.create_contact_sheet(spec_path, root / "pairs.png")

    def test_rejects_nonpositive_thumbnail_width(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "dual_spec.json"
            spec_path.write_text(
                json.dumps({"version": 1, "title": "测试", "slides": [{"slide": 1}]}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                contact_sheet.create_contact_sheet(spec_path, root / "pairs.png", thumb_width=0)


if __name__ == "__main__":
    unittest.main()
