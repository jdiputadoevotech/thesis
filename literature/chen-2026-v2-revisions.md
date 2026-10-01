# Chen et al. (2026) was revised: sentences to re-check

**Status:** flagged 2026-10-01, not yet revised. For Janritch and Matt to decide how to re-argue; no chapter text has been changed.

Chen, D., Lowe, M., & Zinn, Z. (2026). *Parameter-Efficient Fine-Tuning of DINOv2 for Large-Scale Font Classification.* arXiv:2602.13889.

- **v1:** 14 Feb 2026. `references.md` row 36 was written from this version.
- **v2:** 3 Apr 2026. The current version, and what a reader following the citation will see.

## What changed

| Figure | v1 | v2 |
|---|---|---|
| Top-1 accuracy | ~86% | 99.0% |
| Family-level accuracy | 40.2% | 99.4% |
| Trainable parameters | ~150K LoRA (~0.2%) | ~295K LoRA + 606K classification head ≈ 900K (~1%) |
| Relative severity index Π | 0.5532 | 0.0069 |
| Families | 31 | 32 (394 variants) |
| Released model | — | `dchen0/font_classifier_v4` |

**Unchanged:** the synthetic pipeline this thesis adopts (575 images per variant, 1024 px renders, luminance contrast ≥ 80, Gaussian noise σ = 25.5), the r = 8 / α = 16 LoRA on query and value, and the stated limitation that the model "may not generalize perfectly to photographs of printed text, handwritten annotations overlaid on typed text, or heavily stylized graphics."

## Affected sentences

**1. Chapter 1, `chapters/01-introduction/draft.md` line 13.** It argues the current baseline fails on real input:
> "even a modern frozen Vision Transformer baseline collapses to 40.2% family-level accuracy on non-synthetic input by its authors' own report (Chen et al., 2026)"

- v2 reports 99.4% family-level accuracy.
- Even in v1, the 40.2% was about weight variants within the synthetic benchmark, not non-synthetic input.
- The motivation still has support: the authors' own stated limitation on photographs and stylized graphics, which v2 keeps.

**2. Chapter 2, `chapters/02-review-of-related-literature/draft.md` line 11.** Two places:
> "training only about 0.2% of the backbone's parameters, and reach roughly 86% Top-1 accuracy across 394 Google Font variants"

> "its family-level accuracy collapsing to 40.2% between near-identical weight variants"

v2: ~1% trainable, 99.0% Top-1, 99.4% family-level.

**3. Chapter 3, `chapters/03-technical-background/draft.md` line 149.** It explains LoRA with Chen et al. as the example:
> "training roughly 150,000 parameters — about 0.2% of the backbone — and reach approximately 86% Top-1 accuracy"

> "(family-level accuracy falls to 40.2%), which the authors attribute to detail lost at the 224×224 input resolution"

- v2: ~295K LoRA parameters.
- Our own run of the same configuration counts 294,912, which agrees with v2.

**4. Chapter 4, `chapters/04-methodology/draft.md` line 11 (Section 4.1).** It justifies the one-weight-per-family palette:
> "expanding their model to 394 font variants dropped family-level accuracy to 40.2%, because most of the added fonts were near-identical weight variants that the model constantly confused"

- With 99.4% in v2, this no longer supports the palette decision as stated.
- v2 does still report that "performance degrades on near-identical weight variants at low resolution." That may carry the argument without the number.

**5. Defense script, `proposal-presentation/script.md` line 70:**
> "by their own report family accuracy collapses to 40.2% on non-synthetic input"

Same issue as Chapter 1.

**6. Section 4.10.2 adopts their severity index Π.** No v1 value is quoted there, so nothing to fix. Our implementation follows the definition, which is unchanged (`src/model/open_set.py`, `severity_index`).

## Note for Chapter 5

Our own Chen et al. baseline numbers will come from running the released v2 model (`src/model/baselines.py`), not from either version of the paper.
