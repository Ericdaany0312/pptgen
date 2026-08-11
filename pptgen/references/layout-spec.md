# `dual_spec.json` reference

Copy `assets/templates/dual_spec.json` into the presentation project. Paths are resolved relative to the spec file.

## Root fields

- `version`: currently `1`.
- `title`: project title.
- `slide_size.width`, `slide_size.height`: reference pixel dimensions and aspect ratio. Default `1920 × 1080`.
- `slides`: ordered non-empty array.

## Slide fields

- `slide`: continuous one-based page number.
- `page_type`: semantic type such as `cover`, `agenda`, `content`, `section`, or `closing`.
- `composite_image`: complete page image including text.
- `clean_background`: matched visual image with intended editable text removed.
- `image_render`: rendered image-deck page.
- `editable_render`: rendered editable-deck page.
- `text_elements`: native text boxes to restore on the clean background.

All paths must be non-empty, relative, and contained within the project directory.

## Text element fields

- `id`: unique stable name within the slide.
- `text`: exact canonical wording.
- `role`: semantic role such as `title`, `subtitle`, `body`, `caption`, `label`, or `footer`.
- `x`, `y`, `w`, `h`: normalized geometry in the range 0–1. Width and height must be positive; the box must remain inside the slide.
- `font_family`: preferred PowerPoint font.
- `font_size_pt`: positive point size.
- `bold`: Boolean.
- `color`: `#RRGGBB`.
- `align`: `left`, `center`, `right`, or `justify`.
- `valign`: `top`, `middle`, or `bottom`.

The validator checks the required interoperable subset. The builder may add optional presentation fields such as `italic`, `line_spacing`, `letter_spacing`, `rotation`, `opacity`, or `shadow`; document those additions in the project if used.

## Text fidelity

Copy exact text from user-approved sources. Preserve line breaks only when they are semantically or visually required. Never trust image-generation output or OCR for names, dates, numbers, policy wording, quotations, or punctuation.

## Geometry guidance

- Estimate boxes against the composite image at full resolution.
- Prefer padding inside a slightly generous box over tight glyph tracing.
- Use explicit line breaks only when needed to reproduce the design.
- Confirm the selected font exists in the build/render environment.
- Rerender after every box, font, size, or wording change.
