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

**9. The homogeneity check as designed in Section 4.4.2 does not work.** It pools DINOv2 block-12 patch tokens by grid column, splits the column profiles into two clusters, and flags the crop when the clusters are farther apart than a cutoff set at 5% false alarm on single-font validation crops (`src/model/homogeneity.py`, `homogeneity.json`). On the mixed-font stressor set (validation half), it flags only 2.4% of mid-word mixes, 4.5% of whole-word mixes and 2.4% of interleaved crops: no better than its 4.8% false-alarm rate on single-font crops. Finding empty columns by CLS attention instead of ink pixels is no better (1.0–3.2%). Probable cause: a column's tokens mostly encode *which letter* sits there, so letter-to-letter variation inside one font swamps the font-to-font difference the check looks for.

**10. The trained font embedding does separate the halves of a two-font crop.** Probe on 300 single-font and 300 mixed validation crops (whole-word and mid-word mixes): cut each crop in two, embed both halves with the final head, and take their cosine distance. Cutting at the middle gives AUROC 0.811 and detects 48.7% of mixed crops at 5% false alarm; cutting at the true boundary gives AUROC 0.932 and 78.0% (the ceiling for a perfect cut position). A working check can therefore search a few cut positions with the embedding the head was trained for, at the price of extra forward passes per crop, which Section 4.4.2 currently says the check does not need. (Probe only; not yet a script or a report file.)

**11. The first cut-search homogeneity check underperforms the probe.** Taking the largest left/right distance over cuts at 20–80% of the width (`homogeneity_search.json`) gives AUROC 0.669 and detects 24.4% of whole-word mixes, 12.8% of mid-word mixes and 10.7% of interleaved crops at 5.3% false alarm; median boundary error 0.17–0.20 of the crop width. The middle-cut probe of finding 10 did better (AUROC 0.811). The likely cause: cuts near the edges leave a piece one or two letters wide, whose embedding is noisy, and the maximum over cuts picks those noisy distances up even on single-font crops (cutoff 0.93). Not yet tuned.

**12. DeepSSIM is no better than classic SSIM at checking a prediction.** Re-rendering the predicted font in the crop's exact layout (`src/model/rerender.py`, `rerender.json`, 3,000 validation crops): the score separates correct from wrong predictions with AUROC 0.716 (SSIM), 0.689 (MSE), 0.670 (DeepSSIM), 0.669 (DeepSSIM-Lite). Re-rendering the *true* font, by tier (pristine / mild / moderate / severe):

| | Pristine | Mild | Moderate | Severe |
|---|---|---|---|---|
| SSIM | 0.943 | 0.265 | 0.060 | 0.023 |
| DeepSSIM | 0.888 | 0.478 | 0.205 | 0.088 |
| DeepSSIM-Lite | 0.962 | 0.665 | 0.215 | 0.039 |

DeepSSIM holds up better than pixel SSIM under mild deformation but collapses too at moderate and severe. This is our implementation from the arXiv v1 equations; the paper's attention calibration is unspecified there and not implemented (choices listed in the script's docstring), so the result describes this implementation, not necessarily the authors' code.

**13. Both closed-set baselines fall far behind on this corpus, most of all under deformation.** Each run with its own released weights and preprocessing (`src/model/baselines.py`, `baselines.json`), folded to font families, on the same validation crops as our head:

| Same crops | Top-1 | Top-3 | Pristine | Mild | Moderate | Severe |
|---|---|---|---|---|---|---|
| *77 palette fonts Storia knows (6,645 crops)* | | | | | | |
| Storia-AI (Jiang et al., 2025) | 20.9% | 31.6% | 48.1% | 33.6% | 9.6% | 3.1% |
| Our head | 51.4% | 72.8% | 66.5% | 66.2% | 47.6% | 29.9% |
| *17 palette fonts Chen et al. know (1,469 crops)* | | | | | | |
| Chen et al. (2026), v2 weights | 15.2% | 31.7% | 16.1% | 20.0% | 14.9% | 9.8% |
| Storia-AI | 27.3% | 45.0% | 57.8% | 40.6% | 15.4% | 7.9% |
| Our head | 56.2% | 81.3% | 67.3% | 70.8% | 56.2% | 33.2% |

Read with care:
- Both baselines are asked only to choose among the palette fonts they know, the same closed-set question our head answers. On their own full catalogues they score lower still (Storia 6.9% over 1,677 families, Chen 11.2% over 32).
- Storia is competitive on pristine crops (48–58%) and collapses with deformation (3–8% severe), which is the failure mode the thesis targets.
- Chen et al.'s model is weak even on pristine crops (16.1%), although it uses its own deployed preprocessing (`handler.py`) verbatim. A sanity check on clean, full-size renders also gave mixed answers, and was sensitive to text polarity (better white-on-black). Its model card states "~86% on test set". So it does not transfer well to renders that are not its own; this is a statement about these weights on this corpus, not about the paper's benchmark.
- Storia's catalogue lacks three palette fonts (Google Sans, Geist Mono, Ubuntu), which are excluded from its rows.
- Neither baseline can say "unknown": on unknown fonts its FPR is 100% by construction. Storia's catalogue contains all 20 unknown fonts, but it names them correctly only 7.7% of the time.

## Files

| File | Contents |
|---|---|
| `open_set_dinov2.json`, `open_set_dinov2_mid.json` | Plain heads: last-layer and multi-layer |
| `open_set_dinov2_mid_oe.json` | **The final model** (128 background crops, margin 0.4; identical to `open_set_oe_bg128_m04.json`) |
| `open_set_oe_bg*.json` | Outlier-exposure sweep (40 background fonts); `open_set_oe_bg32.json` is the first, 32-crop run |
| `open_set_oe_x3_*.json` | 120 background fonts |
| `open_set_*_s1.json`, `open_set_*_s2.json` | Extra seeds for the three setups in finding 5 |
| `homogeneity.json` | Patch-column homogeneity check, both empty-column masks (finding 9) |
| `homogeneity_search.json` | First cut-search homogeneity check (finding 11) |
| `rerender.json` | Re-render check: SSIM, MSE, DeepSSIM, DeepSSIM-Lite (finding 12) |
| `baselines.json` | Storia-AI and Chen et al. against our head (finding 13) |
