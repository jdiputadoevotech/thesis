# Font recognizer web application (`src/app/`)

Increment 4 (Sections 4.5, 4.6.3): upload an AI-generated image, get every text region boxed with the closest palette fonts or an honest "unknown" / "two typefaces" verdict. Single user, no accounts, nothing stored.

- `server.py`: FastAPI. `POST /predict` (multipart `file`; query `check_mixed`, `k`, `max_regions`) runs the same pipeline as `src/model/real.py predict`: EasyOCR word boxes → grayscale crop → `bundle.Recognizer` (`models/font_recognizer.pt`; DINOv2 itself downloads from the Hugging Face Hub on first run). Weights and localizer load once at startup. Typed response (`/docs` shows the schema). Bad inputs: 415 wrong type, 400 unreadable, 413 over 10 MB, 200 with no regions when no text is found. Images over 2048 px on a side are scaled down first; at most 12 regions are analysed (largest first, the rest are counted in `skipped`).
- `src/`: React + Vite + Tailwind. Boxes over the image, a card per region with the crop, the read text, the verdict and, per candidate, the text set live in that Google Font (loaded from `/fonts/`), the similarity and a link to Google Fonts. Unknown regions show the closest fonts folded away, below the threshold.

```bash
.venv/bin/python src/app/server.py --check            # contract, bad inputs, determinism (loads the model, ~1.5 min on CPU)
cd src/app && bun run build                           # then:
.venv/bin/python src/app/server.py                    # http://127.0.0.1:8001
cd src/app && bun run dev                             # hot reload on :5174, proxies to :8001
cd src/app && bun run format && bun run lint
```

Measured on the M2 CPU (10 regions, a 1024 px SDXL image): 30 s with the two-typeface check, 10 s without (`check_mixed=false`). That misses the few-seconds target of Section 4.5.1 on a CPU; the homogeneity probe gate in `plans/plans.md` (Increment 4 detail) is the planned fix, and a GPU host is fast.
