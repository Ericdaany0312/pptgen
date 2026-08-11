# Text separation

## Source-of-truth rule

Canonical text comes from source material and `dual_spec.json`. OCR and visual models may estimate text regions, but their recognized strings are advisory only. Never replace canonical text with OCR output.

## Image-editing sequence

Before editing, inspect the local composite at original resolution as required by the image generation workflow. Then make one image-editing call for that page with instructions equivalent to:

```text
Using the attached slide as the exact visual reference, remove only these editable text regions: [describe regions and strings]. Remove glyphs, punctuation, outlines, shadows, glow, and antialiasing residue. Reconstruct the background naturally under those regions. Preserve every other element, including illustration, photos, icons, charts, decorations, colors, texture, geometry, spacing, crop, and 16:9 canvas. Add no new text or symbols. Return one clean text-free slide background at the same aspect ratio.
```

Be explicit about text that must remain embedded, such as words inside a logo, photographed signage, or decorative lettering the user does not intend to edit.

## Inspection checklist

At full size, verify:

- no surviving strokes, punctuation, shadows, halos, or blur where text was removed;
- no obvious flat patches, repeated texture, broken lines, or missing decorations;
- unchanged illustration geometry, crop, colors, spacing, and slide dimensions;
- enough visual contrast remains for the restored native text;
- no new text-like artifacts were introduced.

## Coordinate mapping

Use visual inspection to place text boxes. OCR bounding boxes can be used as an initial guess only. Expand the box slightly to accommodate native font metrics, then compare the editable render against the composite.

When the original image typography uses effects that native PowerPoint text cannot reproduce reliably, prioritize hierarchy, wrapping, alignment, color, and perceived size. Record unavoidable differences in the review report.

## Retry rule

Allow at most two text-removal edits on a page. On a third attempt, change strategy: generate a fresh text-free background using the approved composite as a strict composition reference. Repeated inpainting often compounds artifacts.
