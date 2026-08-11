# pptgen

Generate one PowerPoint design and deliver it in two visually matched forms:

- **Image version** — each approved slide is a full-page image, preserving the AI-generated composition.
- **Text-editable version** — the matching text-free background plus native PowerPoint text boxes.

`pptgen` is a reusable skill for ChatGPT and Codex. It is designed for requests such as 图文分离, 双版本 PPT, 图片版与文字可编辑版, and 先生成整页图再拆字.

## Why this workflow

Image-generated slides can look polished, but their text is difficult to correct. Rebuilding a page directly with native objects makes the text editable, but often changes the visual design.

`pptgen` keeps both advantages by using a single canonical specification:

1. Store the exact approved wording in `dual_spec.json`.
2. Generate a complete text-and-visual slide image.
3. Remove only the intended editable text and reconstruct the background.
4. Restore the canonical wording as native PowerPoint text boxes.
5. Render both decks and compare them page by page.

OCR or vision may help locate text regions, but OCR output never replaces the canonical wording.

## Outputs

Every completed project produces:

```text
YYYYMMDD_topic/
├── YYYYMMDD_topic_image.pptx
├── YYYYMMDD_topic_text-editable.pptx
├── dual_spec.json
├── composite/
├── backgrounds/
├── rendered/image/
├── rendered/editable/
└── review/
    ├── paired-contact-sheet.png
    └── acceptance-report.md
```

The editable version guarantees editable target text. Illustrations, textures, photos, decorative elements, and charts may remain rasterized unless the user explicitly asks for native reconstruction.

## Install

The simplest option is to ask Codex to install the skill from this repository:

```text
Use $skill-installer to install the pptgen skill from
https://github.com/Ericdaany0312/pptgen/tree/main/pptgen
```

For a manual user-level Codex installation:

```bash
git clone https://github.com/Ericdaany0312/pptgen.git
mkdir -p ~/.agents/skills
cp -R pptgen/pptgen ~/.agents/skills/pptgen
```

Codex detects newly installed skills automatically. If it does not appear, restart Codex. See the [official OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Use

Invoke it explicitly with `$pptgen`, for example:

```text
Use $pptgen to turn these notes into a 12-slide 16:9 presentation.
First generate complete visual slides, then separate the intended text,
and deliver both an image-based PPTX and a text-editable PPTX.
```

The skill can also trigger implicitly when a request clearly asks for a dual-output or text-separated PowerPoint workflow.

## Requirements

- ChatGPT or Codex with image generation and presentation capabilities
- Python 3.10 or newer
- Pillow for the deterministic validation and paired-review scripts

The skill delegates actual PowerPoint construction to the installed presentation toolchain. It does not use `python-pptx`.

## Repository layout

```text
.
├── README.md
├── LICENSE
├── .github/workflows/test.yml
└── pptgen/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/templates/
    ├── references/
    ├── scripts/
    └── tests/
```

## Validate locally

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s pptgen/tests -v
python pptgen/scripts/validate_dual_spec.py \
  --spec pptgen/assets/templates/dual_spec.json \
  --stage plan
```

The test suite covers schema validation, path containment, dimensions and aspect ratios, exact-text requirements, and paired contact-sheet generation.

## License

[MIT](LICENSE)
