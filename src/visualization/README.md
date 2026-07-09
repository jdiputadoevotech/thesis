# src/visualization/

Executable diagram scripts for the thesis figures. Each script programmatically renders one figure to
`assets/figures/` as **PNG @ 300 dpi**. One script per figure; figure numbers follow in-text appearance
order. Figures 1–7 serve **Chapter 3 (Technical Background)**; Figure 8 serves **Chapter 4 (Methodology)
§4.4**.

## Planned scripts

| Script | Figure | Batch | Renders | Tool |
|---|---|---|---|---|
| `_style.py` | — | shared | 300 dpi, fonts, palette, `savefig(name)` → `assets/figures/<name>.png` | — |
| `font_anatomy.py` | Figure 1 | T1 | serif/sans/display/mono + x-height, terminal, stroke-contrast callouts | Matplotlib |
| `cnn_block.py` | Figure 2 | T1 | conv → pool → FC block diagram | Matplotlib patches |
| `degradation_pipeline.py` | Figure 3 | T1 | clean glyph → elastic warp → blur/noise → kerning jitter | Matplotlib |
| `embedding_space.py` | Figure 4 | T2 | 2D scatter — known-font clusters + open-set rejection boundary | Seaborn |
| `vit_attention.py` | Figure 5 | T3 | patch embedding + self-attention heads schematic | Matplotlib |
| `ssim_pipeline.py` | Figure 6 | T3 | re-render predicted font → structural compare vs. crop | Matplotlib |
| `system_pipeline.py` | Figure 7 | T4 | end-to-end framework flowchart | Matplotlib |
| `conceptual_framework.py` | Figure 8 | Ch4 | IPO framework — user/frontend/backend/ML engine + offline training subsystem | Matplotlib |

## Conventions
- Every script imports `_style.py` and writes `assets/figures/<name>.png` at 300 dpi with consistent styling.
- Output goes to `assets/` (per repo schema), **not** into this folder.
- Figure → batch → script mapping is 1:1; numbering matches appearance order in `draft.md`.

## Dependencies (install into the root `.venv`)
```
matplotlib
seaborn
graphviz          # Python package; also needs the graphviz SYSTEM binary on PATH for system_pipeline.py
```
