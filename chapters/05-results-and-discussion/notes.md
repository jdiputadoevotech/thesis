# Chapter 5 — Results and Discussion

- Presentation of results (tables, figures → `assets/`)
- Interpretation / discussion against the research questions
- Comparison with related studies (Ch2)
- Error analysis / limitations observed

## Notes

## Tables this chapter owes (from the 2026-08-03 defense revisions)
- **Backbone comparison table** — protocol in §4.10.2 (DINOv2 vs CLIP-class vision-language encoder vs supervised ViT vs convolutional baseline). Columns: Top-1, Top-3, FPR@95% recall, parameter count, CPU latency, GPU latency, and whether the backbone exposes patch-level features (the qualifying criterion for the homogeneity check). Ch6 concludes which backbone ships and why.
- **Mixed-font stressor results** — detection rate and false-alarm rate of the patch-token homogeneity check, measured on the synthetic two-font stressor set at controlled mixing ratios (§4.10.2). Report alongside the rate of mixed-typography verdicts on the real-generative set.
