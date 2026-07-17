# Abstract — Planning Notes

> Planning artifact only. Prose goes in `draft.md`.

## Word budget
~250 words (single paragraph, no citations, no undefined acronyms on first use).

## Structure (funnel)
1. **Problem** — GenAI images (DALL-E, Midjourney) produce typographic hallucinations: glyph deformation, micro-warping, variable kerning.
2. **Gap** — Commercial font identifiers (WhatTheFont) fail on hallucinated text; closed black box, maps to paid licenses.
3. **Approach** — Deep-learning feature-metric pipeline maps hallucinated crops → open-source palette (top 50–100 Google Fonts) for free template reconstruction.
4. **Method** — Synthetic degradation pipeline (elastic warp, blur/noise, tracking) on pristine renders; metric learning + open-set recognition; ViT/DINOv2 embeddings; eval via Top-K, SSIM, confusion matrix, 3-person human proxy.
5. **Expected contribution** — Deformation-robust open-set font recognition; results deferred until runs complete.

## Keywords (target 4–6)
typographic hallucination · font style recognition · metric learning · open-set recognition · generative AI · Google Fonts

## Evidence pointers
- Problem/gap/objectives → `chapters/01-introduction/draft.md` (§1.2)
- Method + metrics → `chapters/04-methodology/notes.md`; root `CLAUDE.md` Data Strategy & Metrics
- Do NOT state result numbers until measured (CLAUDE.md rule #3).

## Timing
Draft prose after Ch1 background (§1.1) lands — abstract mirrors the finished intro funnel.
