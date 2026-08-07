# Chapter 5 — Summary, Conclusions, and Recommendations

- Summary of findings (answer each research question)
- Conclusions
- Recommendations (future work, deployment, dataset/model improvements)

## Notes
-

## Post-defense items to carry into recommendations (2026-08-03 defense, passed w/ minor revisions)
- Panel question: regions with multiple font families. Resolution now in Ch4: word-level localization (§4.4.2 assumption: one word = one typeface), patch-token homogeneity check + one split, third verdict "mixed typography". Recommendation hook: per-glyph attribution inside an unsplittable mixed word stays out of scope (char segmentation unreliable on hallucinated glyphs; no single reconstructable font) — name it as future work.
- Panel mandate: backbone comparison beyond DINOv2 (protocol in §4.10.2: DINOv2 vs CLIP-class vs supervised ViT vs conv baseline; Top-1/3, FPR@95, params, CPU/GPU latency; patch-token capability as qualifying criterion). Ch5 reports the table; Ch6 concludes which backbone ships and why.
