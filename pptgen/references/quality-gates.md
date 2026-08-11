# Quality gates

Release only after all four gates pass.

## Gate 1: canonical content

- Outline and exact wording are approved or user-authorized for direct execution.
- `dual_spec.json` passes the `plan` stage.
- Names, dates, figures, quotations, policy text, and official terms match the source.
- No OCR result has silently replaced canonical wording.

## Gate 2: image assets

- Every composite image is visually approved at full size.
- Every clean background matches its composite in dimensions and visual composition.
- Removed text leaves no glyph fragments, halos, flat patches, or broken decoration.
- The `assets` stage passes.

## Gate 3: deck integrity

- Both decks have the same page count, order, dimensions, and visual identity.
- Image slides are full-bleed with no accidental margins.
- Native text remains selectable and editable in the editable PPTX.
- Text boxes do not clip, overflow, collide, or wrap differently enough to change meaning.
- Both complete decks have been rendered after the last source change.
- The `rendered` stage passes.

## Gate 4: paired visual review

Generate the paired sheet:

```bash
python scripts/create_pair_contact_sheet.py \
  --spec dual_spec.json \
  --output review/双版本逐页对照.png
```

Review every row for hierarchy, wrapping, position, color, contrast, crop, and composition. Open suspicious pairs at full resolution. Record accepted differences, font substitutions, and repairs in `review/验收报告.md`.

## Blocking defects

Do not release when any of these remain:

- incorrect or unreadable text in the image version;
- visible residual text or repair artifacts in a clean background;
- missing slide, stale render, mismatched page dimensions, or divergent slide order;
- editable text flattened into the background;
- a claim of full editability when only text is editable;
- invented data, brand assets, citations, or official wording.
