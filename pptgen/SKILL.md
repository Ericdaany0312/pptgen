---
name: pptgen
description: Create two visually matched PowerPoint decks from the same source by first generating complete text-and-visual slide images, then separating intended text from each image and restoring the exact wording as native editable text boxes. Use when the user asks for 图文分离, 双版本 PPT, 图片版与文字可编辑版, 先生成整页图再拆字, or a presentation that preserves AI-generated visual composition while allowing later text edits. Output both an image-based deck and a text-editable deck plus paired visual QA. Do not use for a single ordinary deck when ppt-auto-generator is sufficient.
---

# PPTGen

Create one visual design and deliver it twice:

1. **图片版** — each slide is the approved composite image, including text.
2. **文字可编辑版** — the matching text-free background plus native PowerPoint text boxes.

“可编辑” means the intended text is editable. Illustrations, textures, photos, decorative shapes, and charts may remain rasterized unless the user explicitly asks to rebuild them as native objects.

## Required supporting skills

Read and follow the installed `imagegen` skill before generating or editing slide images. Read and follow the installed `presentations` skill before creating, rendering, or inspecting PowerPoint files. Use its required artifact-tool workflow for actual deck construction; do not use `python-pptx`.

## Workflow

1. Collect the purpose, audience, page count, source material, exact required wording, brand assets, target aspect ratio, and delivery directory. Ask only questions that materially change the deck. Default to 16:9.
2. Create the project structure described in [references/dual-render-workflow.md](references/dual-render-workflow.md). Copy `assets/templates/dual_spec.json`, `prompt_confirmation.md`, and `review.md` into the project.
3. Build the outline and a concise style guide. Put all visible wording in `dual_spec.json` before image generation. Treat this canonical text as the only source of truth.
4. Run the plan-stage validator. Fix every reported error before generating images.
5. Generate one complete composite slide image per page, including the approved wording. Keep typography legible and the text volume modest. Inspect each image at full size; regenerate pages with incorrect, invented, warped, clipped, or unreadable text.
6. For every approved composite, use image editing to remove only the intended editable text and reconstruct the newly exposed background. Preserve composition, visual assets, colors, texture, spacing, and slide dimensions. Follow [references/text-separation.md](references/text-separation.md).
7. Inspect composite and clean-background images side by side. Record normalized text boxes and native text styles in `dual_spec.json`. OCR or vision may suggest geometry, but must never replace canonical wording.
8. Run the assets-stage validator. Repair missing files, mismatched dimensions, residual glyphs, holes, or layout drift before building either deck.
9. Use the presentation toolchain to create two files from the same spec:
   - image deck: place `composite_image` full-bleed on every slide;
   - text-editable deck: place `clean_background` full-bleed, then add each canonical `text_element` as a native text box.
10. Render both complete decks to the paths recorded in `image_render` and `editable_render`. Run the rendered-stage validator and create the paired contact sheet.
11. Review every pair using [references/quality-gates.md](references/quality-gates.md). Repair only affected pages. Stop after two failed text-removal edits on one page and regenerate a clean background from the composite reference instead of accumulating artifacts.
12. Deliver both PPTX files, the paired contact sheet, and the completed review report.

## Canonical spec rules

Read [references/layout-spec.md](references/layout-spec.md) before editing `dual_spec.json`.

- Keep slide numbers unique, ordered, and continuous from 1.
- Use project-relative paths only. Never use absolute paths or `..` path traversal.
- Store text boxes as normalized `x`, `y`, `w`, `h` values from 0 to 1.
- Keep every text element ID unique within its slide.
- Preserve exact wording, punctuation, figures, names, dates, and policy language.
- Never copy OCR-recognized text into the spec without comparing it to the source.
- If wording changes, update the editable deck directly. Regenerate the composite page only when the image version must also change.

## Commands

Use a Python environment containing Pillow. In the Codex desktop app, prefer the bundled workspace Python.

```bash
python scripts/validate_dual_spec.py --spec dual_spec.json --stage plan
python scripts/validate_dual_spec.py --spec dual_spec.json --stage assets
python scripts/validate_dual_spec.py --spec dual_spec.json --stage rendered

python scripts/create_pair_contact_sheet.py \
  --spec dual_spec.json \
  --output review/双版本逐页对照.png
```

## Required output

```text
YYYYMMDD_主题/
├── source/
├── outline.md
├── style_guide.md
├── prompt_confirmation.md
├── dual_spec.json
├── composite/slide_01.png
├── backgrounds/slide_01.png
├── rendered/image/slide_01.png
├── rendered/editable/slide_01.png
├── review/双版本逐页对照.png
├── review/验收报告.md
├── YYYYMMDD_主题_图片版.pptx
└── YYYYMMDD_主题_文字可编辑版.pptx
```

Keep all intermediate artifacts unless the user asks to remove them.

## Release rules

- Do not claim both decks match until both are rendered and reviewed page by page.
- Do not release a clean background with visible letter fragments, shadows, halos, or repaired-area smearing.
- Do not cover baked-in text with opaque boxes and call it separated.
- Do not claim full editability unless all requested visual elements were rebuilt as native objects.
- Do not flatten the native text layer in the editable deliverable.
- Do not deliver stale renders after changing a source image, text box, or font.
- Document unavoidable font substitution or accepted visual differences in the review report.
