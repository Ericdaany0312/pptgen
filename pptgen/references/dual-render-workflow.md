# Dual-render workflow

## Contract

One canonical source must produce two decks with identical slide order, dimensions, visual composition, and intended wording:

- `图片版.pptx`: approved composite images placed full-bleed;
- `文字可编辑版.pptx`: approved text-free backgrounds plus native text boxes.

The editable deck is text-editable by default, not necessarily fully editable.

## Project lifecycle

### 1. Plan

Create the outline, style guide, confirmation record, and `dual_spec.json`. Keep exact wording in the spec before invoking image generation. Verify with:

```bash
python scripts/validate_dual_spec.py --spec dual_spec.json --stage plan
```

### 2. Generate composite pages

Generate one complete page per call. The prompt must include the page purpose, approved visible wording, composition, visual hierarchy, brand constraints, aspect ratio, and prohibited inventions. Save each raw result immediately to `composite/slide_NN.png`.

Full-size inspection is mandatory. Generated text must be correct in the image deck; the later editable overlay does not repair the baked-in image version.

### 3. Remove editable text

Edit the approved composite as a reference image. Remove the intended words, punctuation, glyph shadows, outlines, and glow while reconstructing the underlying background. Do not remove labels that the user wants to remain embedded in artwork. Save to `backgrounds/slide_NN.png`.

If two removal attempts leave artifacts, regenerate a text-free background using the composite as the composition reference. Do not keep inpainting the same damaged pixels indefinitely.

### 4. Map text boxes

Compare the composite and clean background at full resolution. Record normalized coordinates and native text styling. Keep the boxes slightly larger than the apparent glyph bounds so font substitution does not clip text. Use the original exact text, not OCR output.

### 5. Build two decks

Use the presentation skill's artifact-tool workflow.

- Image version: use identical slide dimensions and a full-bleed composite image per page.
- Editable version: use the matching clean background, then add native text boxes in `text_elements` order.

Convert normalized geometry to presentation units:

```text
left   = x × slide_width
top    = y × slide_height
width  = w × slide_width
height = h × slide_height
```

### 6. Render and compare

Render both decks at the same dimensions. Populate `image_render` and `editable_render`, validate, then create the pair contact sheet. Inspect the contact sheet for global consistency and open every questionable page at full size.

## Change behavior

- Text-only correction in editable deck: update the spec and native text box, then rerender the editable deck.
- Text correction in both decks: update the spec, regenerate that composite, regenerate its clean background, rebuild both affected slides, and rerender both.
- Visual correction: regenerate the composite, derive a new clean background, and rebuild both affected slides.
- Layout correction: update normalized boxes and rebuild the editable slide; update the composite too if the image version must remain matched.

Never mix a new composite with an old clean background.
