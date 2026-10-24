# Expert-Panel Typography Rating Form (`src/rater/`)

Interactive web application implementing the blind three-rater evaluation instrument (`Section 4.2.3`, `Appendix B`, `plans/plans.md` Increment 4). Built with React, Tailwind CSS, and **shadcn/ui** components (`Card`, `Badge`, `Button`, `Input`, `Progress`, `Separator`, `TabsList`) designed for direct side-by-side comparison between degraded/AI-generated raster crops and live Google Fonts specimens.

## Dataset Crop Loading Priority (`src/rater/server.py`)

`GET /api/crops` loads raster PNG crops in priority order while keeping all ground-truth font and coherence labels strictly server-side (blind rating protocol):

1. **Real Generative Evaluation Set (`data/real/crops.csv`)** — Serves localized EasyOCR word crops (`data/real/crops/<crop_id>.png`) produced by `.venv/bin/python src/model/real.py localize`.
2. **Pre-built Synthetic Corpus (`data/corpus/metadata.csv`)** — Serves test-split PNGs directly from disk when `data/corpus/` has been generated.
3. **Deterministic Dataset Pipeline Rendering (`src/data/render_corpus.py` + `src/data/render_mixed.py`)** — When `data/real/crops.csv` is not yet populated on disk, `GET /api/crop-image/<crop_id>.png` deterministically renders and caches a stratified 100-crop benchmark (70 known palette fonts from `data/palette.csv`, 15 held-out unknown fonts from `data/unknown.csv`, and 15 mixed two-typeface crops from `render_mixed.py` across `pristine`, `mild`, `moderate`, and `severe` degradation tiers).

## Key UI Features for Raters

- **Raster Crop Inspector**: Zoom (`100%`–`250%`), luminance polarity inversion (`Key: I`), edge contrast boost for blurred crops, pixel-grid toggle, and dark/light checkerboard backdrops.
- **Live Synced Specimen Diff**: Renders the crop's exact OCR text (`ocr_text`) immediately underneath the target PNG using the pinned `@font-face` TTF from `data/fonts/*.ttf`, with adjustable font size (`24px`–`72px`), letter-spacing/tracking (`-6%` to `+16%`), and diagnostic glyph strip (`Aa Bb Gg Qq Rr M y 0123`).
- **Pinned Finalists Tray**: Raters can hover any font in the 80-font browser to preview it in place, or pin up to 4 candidate fonts side-by-side beneath the crop before locking in **Q1**.
- **Blind Rater Isolation & Output**: Saves `(crop_id, rater, font, coherence)` atomically to `data/real/labels.csv` for `.venv/bin/python src/model/real.py score`.

## Commands

```bash
# Run self-tests (verifies 80-font palette, PNG crop rendering, blind rater isolation, and real.py score compatibility)
.venv/bin/python src/rater/server.py --check

# Start backend server (serves API, /fonts/*.ttf, /api/crop-image/*.png, and built frontend at http://127.0.0.1:8000)
.venv/bin/python src/rater/server.py --port 8000

# Frontend development server with hot reload (http://127.0.0.1:5173)
cd src/rater && bun run dev

# Format, lint, and build production bundle
cd src/rater && bun run format && bun run lint && bun run build
```
