# Increment 2 findings: metric embedding

What the Increment 2 experiments showed, with the file that holds each number. This is the lab record that Chapter 5 draws from. Chapter 4 states the method; this file states what happened.

## Setup in brief

- **Corpus:** 46,000 crops (80 fonts × 575), split 70/15/15 by `(font_id, tier)`. Tiers: pristine 15%, mild 30%, moderate 30%, severe 25% (θ up to 0.90).
- **Metric:** nearest-prototype accuracy. Each font's prototype is the mean training embedding; a validation crop is correct if its nearest prototype is its own font. Chance is 1.25% Top-1. There is no τ or rejection yet; that is Increment 3.
- **Two numbers per result:** a single run scored on the validation split, and 5-fold cross-validation on train + validation (the test split is never used). The CV spread shows how much is noise: about ±0.35 points.
- **Where it ran:** development on the laptop (RTX 3050, torch 2.6.0+cu124), final results on SVC1 (NVIDIA GB10, torch 2.14.0+cu130). Each machine is deterministic, but they differ by about half a point on the same run (40.50% vs 41.06%), so **numbers from the two are never mixed in one comparison**. Everything below is from SVC1 unless marked "laptop".

## Final result

Frozen DINOv2 + trained head `f_θ`, distilled from the 10-epoch teacher. Settings: 120 epochs, batches of 16 fonts × 8 crops, KD weight 0.5, margin 0.2.

| | Top-1 | Top-3 | Family acc |
|---|---|---|---|
| Frozen DINOv2, no head | 12.45% | 26.11% | 66.01% |
| **Head, 5-fold CV** | **43.79% ± 0.33** | **66.36% ± 0.29** | **88.38% ± 0.50** |

By severity tier (CV): pristine 60.58%, mild 56.09%, moderate 40.40%, severe 23.43%. By family (CV): display 71.53%, serif 47.96%, sans-serif 31.15%, monospace 26.34%.

Files: `dinov2_cv.json`, `dinov2.json` (single run, 43.70%), figure `assets/figures/embedding_tsne.png`.

## Findings

**1. The head does the work, not the backbone alone.** The frozen features alone reach 12.45% Top-1. The trained head brings this to 43.79%. Families go from intermixed to separated (see the figure): 88% of predictions land in the correct family even when the font is wrong, so most errors are within-family.

**2. Batch-hard triplet mining collapsed; batch-all works.** With batch-hard mining (each anchor's hardest positive and negative only), the loss sat at exactly the margin (0.2) from the first epoch: every crop mapped to the same point. At severe deformation the hardest pairs in a batch are mostly noise. Batch-all (every margin-violating triplet, Hermans et al., 2017) trained normally. Laptop: batch-hard 23.1% vs batch-all 38.9%.

**3. Three training settings matter; the rest do not.** A one-at-a-time sweep from the old defaults (41.06%), in `sweep.json`:

| Change | Top-1 | vs 41.06% |
|---|---|---|
| 120 epochs instead of 60 | 42.12% | +1.06 |
| 16 fonts × 8 crops instead of 32 × 4 | 41.99% | +0.93 |
| KD weight 0.5 instead of 1.0 | 41.65% | +0.59 |
| margin 0.1 or 0.4, lr ×0.5 or ×2, head 128-d or 512-d | 40.4–41.2% | within noise |
| 64 fonts × 2 crops | 40.00% | −1.06 |
| KD temperature 0.05 | 39.74% | −1.32 |
| KD weight 2.0 / 4.0 | 39.54% / 38.87% | −1.52 / −2.19 |

The three gains stack: together they give 43.41% (`dinov2_combo.json`). More crops per font per batch helps because batch-all mining gets more same-font pairs to learn from.

**4. Distillation helps, but only in moderation.** Under the final settings, removing KD drops Top-1 from 43.70% to 40.41% (`dinov2_nokd.json`), a 3.3-point loss. But a heavier KD weight hurts (finding 3): the student pulled too hard toward a teacher that is itself only ~60% accurate inherits its mistakes.

**5. A better teacher barely helps the student.** Training the teacher 10 epochs instead of 5 raised its own accuracy from 60.2% (laptop) to 64.2% (`teacher10.json`, plateaued by epoch 8). The student distilled from it improved by only 0.3 points (43.41% → 43.70%), inside the noise. The teacher is no longer what limits the student; the frozen features are. The teacher can adapt the backbone to fonts through LoRA; the student cannot, because the frozen backbone is what keeps the served model independent of the closed-set teacher (Chapter 4, Section 4.3.2).

**6. Severe deformation is unsolved.** The severe tier stays between 22.6% and 24.7% under every setting tried. From the old defaults to the final head (single runs), pristine rose 8.0 points, mild 4.1 and moderate 1.6, while severe fell 1.0: the gains shrink as deformation grows. Whatever limits the model at severe deformation, training settings do not reach it. Part of this may be irreducible: the severe tier deliberately runs to θ = 0.90, near where glyphs stop being recognizable to a person. The human-proxy panel (Increment 3) is what will show how much of the gap a person could close.

**7. Monospace and sans-serif are the hard families.** Monospace (8 fonts) and sans-serif (32 fonts) score lowest. Both are families designed to look uniform, so their members differ in small details that deformation erases first.

**8. Reading more layers of the frozen encoder is the biggest gain found.** Findings 5 and 6 pointed at the frozen features as the limit. Those features were the class token and mean patch token of DINOv2's *last* block only. Two variants read the same two summaries from four blocks instead (each through DINOv2's final LayerNorm, concatenated to 6144-d). The backbone stays frozen and every other setting is unchanged. 5-fold CV (`dinov2_cv.json`, `dinov2_mid_cv.json`, `dinov2_last4_cv.json`):

| Blocks read | Top-1 | Top-3 | Family acc | Pristine | Severe |
|---|---|---|---|---|---|
| 12 only (current) | 43.79% ± 0.33 | 66.36% | 88.38% | 60.58% | 23.43% ± 0.51 |
| **3, 6, 9, 12** | **51.27% ± 0.41** | **73.16%** | **90.54%** | 65.99% | **29.93% ± 0.41** |
| 9, 10, 11, 12 | 50.29% ± 0.58 | 72.22% | 90.27% | 66.29% | 29.03% ± 0.78 |

- Top-1 rises 7.5 points, and the **severe tier moves for the first time** (+6.5), which no training setting achieved. Its limit was what the features carried, not how the head was trained.
- Every family improves: serif 47.96 → 57.49%, sans-serif 31.15 → 38.62%, monospace 26.34 → 31.53%, display 71.53 → 77.08%.
- Spreading across depth (3, 6, 9, 12) beats the last four by about 1 point, roughly two standard deviations. This is weak support for the idea that letterform style sits in middle layers. Most of the gain comes from reading more than one block at all.
- Without a head, the raw multi-layer features score *worse* than the last layer alone (frozen nearest-prototype Top-1: 9.29% for 3/6/9/12 vs 12.45%). The extra information is there but buried; the trained head is what extracts it.

These runs reuse the 10-epoch teacher and the tuned settings unchanged, so the teacher's similarity structure (from its last-block CLS) was not re-tuned for the new features.

## Files

| File | Contents |
|---|---|
| `dinov2.json` | Final head, single run on validation, plus the frozen-feature baseline |
| `dinov2_cv.json` | Final head, 5-fold CV, per fold and mean ± std |
| `dinov2_nokd.json` | Final settings without distillation |
| `dinov2_combo.json` | Final settings with the 5-epoch teacher |
| `sweep.json` | One-at-a-time sweep from the old defaults |
| `teacher.json`, `teacher10.json` | LoRA teacher, 5 epochs (laptop) and 10 epochs |
| `dinov2_mid.json`, `dinov2_mid_cv.json` | Head on blocks 3, 6, 9, 12: single run and 5-fold CV |
| `dinov2_last4.json`, `dinov2_last4_cv.json` | Head on blocks 9–12: single run and 5-fold CV |
