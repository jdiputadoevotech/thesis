# Increment 3 findings: open-set rejection

What the Increment 3 experiments have shown so far, with the file that holds each number. Like `reports/incr2/FINDINGS.md`, this is the lab record Chapter 5 draws from.

## Setup in brief

- **Decision rule** (`src/model/open_set.py`, Section 4.4.2 steps 7–8, 11): each palette font's prototype is its mean training embedding. A crop's rejection score is its cosine similarity to the nearest prototype. τ is set so that 95% of known validation crops are accepted. Below τ, the verdict is "unknown font".
- **Unknown fonts** (`data/unknown.csv`): the 20 fonts ranked just below the palette cutoff, split by font into 10 validation and 10 test. **Everything below uses the 10 validation fonts only.** The test fonts are untouched (`--final`).
- **Metrics:** FPR@95 is the share of unknown-font crops wrongly accepted at that τ (lower is better; a closed-set model is at 100% by construction). AUROC is the known-vs-unknown separation over all thresholds (0.5 = chance, 1.0 = perfect).
- **Model:** the multi-layer head (DINOv2 blocks 3, 6, 9, 12) with the Increment 2 settings, all runs on SVC1.

## Findings

**1. The plain head barely rejects unknown fonts.** At 95% recall on known fonts, 87.1% of unknown-font crops are accepted (AUROC 0.654; `open_set_dinov2_mid.json`). The last-layer head is worse: 92.2%, AUROC 0.614 (`open_set_dinov2.json`). So the multi-layer head is better on the open-set measure too, not only on closed-set Top-1.

**2. Deformation is not the main cause.** Even on pristine crops, unknown fonts sit nearly as close to a prototype as known fonts (median similarity 0.836 vs 0.868). The triplet loss only separates the 80 known fonts from each other; nothing in it says a new font should sit far from all of them.

**3. A better score does not fix it.** On the same embeddings: nearest training crop (k-NN, k = 1) reaches AUROC 0.676 and FPR 83.3%; the best-minus-second-best margin and a softmax over prototype similarities do worse than the plain score (AUROC 0.49 and 0.53). The limit is in the embedding, not in how it is read.

**4. Unknown fonts are mistaken for their closest-looking relatives.** Fira Code → IBM Plex Mono and JetBrains Mono; Roboto Serif → Bitter and Source Serif 4; Rowdies → Archivo Black; Fira Sans → Roboto, Ubuntu, Source Sans 3 (`per_unknown_font` in the reports). The embedding places a new font next to the palette font it most resembles; it cannot tell "looks like Roboto" from "is Roboto".

**5. Outlier exposure helps, by about 12 points.** Background fonts (`data/background.csv`: the 40 fonts ranked below the unknown set, never evaluated on) join every training batch as triplet negatives (Hendrycks et al., 2019). Best setting: 128 background crops per batch, margin 0.4. Three seeds each:

| | FPR@95 (3 seeds) | Mean ± sd | AUROC | Known Top-1 |
|---|---|---|---|---|
| No outlier exposure | 87.1, 86.7, 86.8 | 86.9 ± 0.2 | 0.654 | 51.30% |
| **40 background fonts** | 74.6, 73.3, 77.9 | **75.3 ± 2.4** | **0.705** | 50.28% |
| 120 background fonts | 81.3, 79.2, 78.8 | 79.7 ± 1.3 | 0.703 | 50.60% |

The gain costs about 1 point of known-font Top-1. Pushing harder (256 crops per batch, or margin 0.6) does not help further and costs more accuracy (`open_set_oe_bg*.json`, single runs).

**6. More background-font variety does not help.** 120 background fonts at 100 crops each (the same 12,000 crops as 40 × 300) give the same AUROC as 40 fonts and, if anything, a worse FPR. One explanation, untested: the 40 fonts sit just below the unknown set in the ranking, so they are the closest look-alikes and the most useful negatives, which the wider set dilutes.

**7. Outlier exposure teaches rejection of distinctive fonts, not of look-alikes.** Per unknown font, share accepted before → after outlier exposure: Creepster 67 → 32%, Share Tech 79 → 35%, Saira 82 → 38%; but Fira Code 91 → 92%, Fira Sans 88 → 87%, IBM Plex Sans 90 → 88%, Roboto Serif 95 → 95%, Rowdies 99 → 98%, Nanum Myeongjo 97 → 98%. Unknown serif and monospace fonts stay near 92% accepted. What remains are fonts close enough to a palette font that the frozen features may not separate them at all.

**8. FPR is a noisy measure once outlier exposure is on.** Without it, FPR varies by ±0.2 points across seeds; with it, by ±1.3–2.4. It averages over only 10 unknown fonts, each of which swings between ~30% and ~98% acceptance. Single-run FPR differences of a few points are not evidence; Chapter 5 should report the mean over seeds.

## Files

| File | Contents |
|---|---|
| `open_set_dinov2.json`, `open_set_dinov2_mid.json` | Plain heads: last-layer and multi-layer |
| `open_set_dinov2_mid_oe.json` | **The final model** (128 background crops, margin 0.4; identical to `open_set_oe_bg128_m04.json`) |
| `open_set_oe_bg*.json` | Outlier-exposure sweep (40 background fonts); `open_set_oe_bg32.json` is the first, 32-crop run |
| `open_set_oe_x3_*.json` | 120 background fonts |
| `open_set_*_s1.json`, `open_set_*_s2.json` | Extra seeds for the three setups in finding 5 |
