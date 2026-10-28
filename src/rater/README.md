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
- **Identity and chain of custody** (Ch4 §4.2.3): each rater opens one secret link; the server, not the browser, decides who they are. Raters confirm a consent and attestation, every answer is logged with the time spent on it, and finishing locks the answers and shows a receipt (see below).
- **Output**: answers to the evaluation crops are saved atomically to `data/real/labels.csv` (`crop_id, rater, font, coherence`) for `.venv/bin/python src/model/real.py score`; answers to the hidden controls go to `data/real/labels_controls.csv`, which the scoring never reads.

## Proving whose answers they are

Nobody can prove who is at the keyboard; this makes impersonation and later edits hard, detectable and documented.

1. **Named invitation.** Send each expert their link by email to their own professional address, with the transmittal letter. Keep the list of who got which link (r1, r2, r3) privately, outside the repo.
2. **Link = identity.** `server.py tokens` prints three random links once and stores only their hashes (`data/real/raters.private.json`). The server ignores any `rater` the browser sends, each link reads only its own answers, and crops are served only to the rater they belong to. Reissuing (delete the file, run again) kills the old links.
3. **Consent and attestation** before any item, bound to the exact text (its SHA-256 is logged).
4. **Audit log** `data/real/audit.jsonl`: link opened, consent, every save (answer hash, seconds on the item), finish; each line carries the hash of the previous one, plus salted hashes of network address and browser (no raw address or name). `server.py verify` recomputes the chain, so an edited or deleted line is caught.
5. **Receipt.** Finishing locks the answers and shows the rater the SHA-256 of their answer set. They reply from the mailbox that got the link. Commit the receipts and the final audit-log head to the repo (or the appendix), so a later edit to `labels.csv` shows up.
6. **Hidden controls**, built once by `server.py controls`: 8 repeats of readable crops (test-retest) and 6 clean reference renders with a known font. They are served mixed in, with ids shaped like the others and no marker in the payload; they are kept in `controls.private.json` and `labels_controls.csv`, outside the scoring. `verify` reports, per rater, repeat agreement and how many reference items were put in the right family. Report them as data-quality checks, not as scores.

Limits: outside help cannot be excluded; the log shows timing and devices, not who was in the room. Hashing addresses is a privacy choice: check the Data Privacy Act (RA 10173) requirements for the consent wording with the adviser.

## Commands

```bash
# Run self-tests (palette, PNG crops, blind isolation, real.py score compatibility, and the whole identity path against a live server)
.venv/bin/python src/rater/server.py --check

# One-time setup, before any rater starts (both refuse to overwrite; they change nothing after that)
.venv/bin/python src/rater/server.py tokens --base-url https://<your public address>
.venv/bin/python src/rater/server.py controls

# Start backend server (API, fonts, built frontend at http://127.0.0.1:8000); needs `bun run build` first
.venv/bin/python src/rater/server.py --port 8000

# Audit chain, receipts, repeat and reference-item checks
.venv/bin/python src/rater/server.py verify

# Frontend development server with hot reload (http://127.0.0.1:5173)
cd src/rater && bun run dev

# Format, lint, and build production bundle
cd src/rater && bun run format && bun run lint && bun run build
```
