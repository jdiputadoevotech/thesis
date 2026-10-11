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

**11b. Tuned, the cut search detects about half of two-font crops.** Distances at every cut from 10% to 90% (5% steps) were cached once for 3,000 single-font and 2,000 mixed validation crops on the laptop (the server's disk had failed; `homogeneity_tune.json`), and 30 variants were compared on them. The decisive change is refusing cuts that leave a piece narrower than 1.25 times the crop height (about two letters): it lifts AUROC from 0.669 to 0.81. Chosen variant: cuts at 35–65% of the width, that minimum piece width, distances standardized per cut position against single-font crops. At 3.8% false alarm it detects 52.0% of whole-word mixes, 35.2% of mid-word mixes and 11.2% of interleaved crops (AUROC 0.814 on contiguous mixes), and places the boundary within 10% of the crop width for 59.5% of detected crops. A middle-only cut detects slightly more (46.4% vs 43.5% of contiguous mixes, at 4.9% false alarm) but places the boundary worse (49.5% within 10%); the split position matters because it decides what each half is recognized as. These are validation numbers used for the choice; the test half of the stressor set is still unscored.

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

## Final test results (for Chapter 5)

Run once, on 2 Oct 2026, after every design choice above was frozen. They cover the test partition of the main corpus, the 10 held-back unknown fonts, and the test half of the mixed-font set, none of which informed any choice. **No tuning follows these numbers.**

**Where they were computed:** the laptop (RTX 3050, torch 2.6.0+cu124), with the model weights trained on SVC1, because SVC1's disk had failed. The features were recomputed on the laptop.

**Sanity check:** the laptop's validation numbers match SVC1's to within 0.07 points (`open_set_laptop_validation.json`: Top-1 50.14% vs 50.16%, FPR@95 74.56% vs 74.63%, AUROC 0.7083 vs 0.7083).

| Measure | Validation | **Test** | File |
|---|---|---|---|
| Top-1 / Top-3, 80 fonts | 50.2% / 71.3% | **50.2% / 72.2%** | `open_set_dinov2_mid_oe_final.json` |
| Family accuracy | 89.7% | **89.7%** | |
| Severity index Π | 0.103 | **0.103** | |
| Unknown fonts accepted at 95% recall (FPR@95) | 74.6% | **75.6%** | |
| AUROC, known vs unknown | 0.708 | **0.687** | |
| Conformal coverage at α = 0.10 (mean set size) | 89.6% (9.6) | **89.9% (9.6)** | |
| Conformal coverage at α = 0.05 (mean set size) | 94.8% (13.7) | **94.9% (13.4)** | |
| Homogeneity: two-font crops detected (contiguous) / false alarm | 43.5% / 3.8% | **45.7% / 5.4%** | `homogeneity_final.json` |
| Homogeneity: AUROC / boundary within 10% | 0.814 / 59.5% | **0.819 / 59.1%** | |
| Re-render verification AUROC: SSIM / DeepSSIM | 0.716 / 0.670 | **0.710 / 0.664** | `rerender_final.json` |
| Storia-AI / ours, 77 shared fonts (Top-1) | 20.9% / 51.4% | **21.2% / 51.4%** | `baselines_final.json` |
| Chen et al. / Storia-AI / ours, 17 shared fonts (Top-1) | 15.2% / 27.3% / 56.2% | **14.9% / 27.9% / 57.8%** | |

**Notes on the test results:**
- Test Top-1 by tier: pristine 65.9%, mild 65.6%, moderate 49.0%, severe 28.9% (77 shared fonts). The baselines collapse with deformation (Storia-AI 46.2% pristine → 2.5% severe).
- Rejection depends heavily on which unknown fonts are held out. Of the 10 test fonts, the display faces Bangers (17% accepted) and Smooch Sans (19%) are mostly rejected. Cormorant (99%), Frank Ruhl Libre (97%), Courier Prime (95%) and Sanchez (95%) are almost always accepted. Unknown serif and monospace fonts are accepted 95–97% of the time, display fonts 41.5%.
- The homogeneity check detects whole-word mixes (52.6%) better than mid-word ones (38.5%), and cross-family pairs (52.0%) better than same-family pairs (30.7%). Detection drops to 29.0% at severe deformation.
- The false-alarm rate on test single-font crops came out at 5.4%, against the 5% the validation cutoff targeted.

## Backbone comparison (Table 5)

All four candidates use the final recipe: outlier exposure, distillation, and the tuned head settings. To keep "only the backbone changes", every backbone is read the same way: the last layer's summary (class or pooled token plus mean patch token; ConvNeXt's pooled map). The multi-layer reading exists only for DINOv2, so the final model is listed separately. Run on the laptop on 4 Oct 2026, with no tuning per backbone. Files: `open_set_bb_*.json` (validation), `open_set_bb_*_final.json` (test), `latency.json`.

| Backbone | Val Top-1 | **Test Top-1** | Test Top-3 | Test family | Test FPR@95 | Test AUROC | Backbone params | GPU ms / crop | CPU ms / crop |
|---|---|---|---|---|---|---|---|---|---|
| DINOv2 ViT-B/14 | 42.5% | **41.0%** | 65.1% | 87.3% | 80.3% | 0.661 | 86.6 M | 28.7 | 300 |
| Supervised ViT-B/16 | 33.2% | 32.7% | 54.4% | 83.3% | 86.3% | 0.627 | 86.4 M | 18.7 | 238 |
| ConvNeXt-T | 34.2% | 33.8% | 55.3% | 84.1% | 88.8% | 0.620 | 27.8 M | 13.8 | 98 |
| SigLIP ViT-B/16 (vision tower) | 27.2% | 26.0% | 46.6% | 81.0% | 91.7% | 0.605 | 92.9 M | 19.5 | 269 |
| *DINOv2, blocks 3/6/9/12 (final model)* | *50.2%* | *50.2%* | *72.2%* | *89.7%* | *75.6%* | *0.687* | *86.6 M* | *26.3* | *332* |

Latency is the median per crop over 50 crops (GPU) and 20 crops (CPU), one crop at a time, after warm-up. Machine: RTX 3050 Laptop GPU, Intel CPU with 14 threads, torch 2.6.0.

- **DINOv2 is best on every accuracy and rejection measure.** That confirms the choice on measured evidence, as Section 4.10.2 promised.
- **Self-supervised pretraining helps.** DINOv2 and the supervised ViT share one architecture, and DINOv2 leads by 8.3 points of test Top-1 and 6 points of FPR. Table 5's note anticipated this pairing as the test of self-supervised pretraining.
- **SigLIP, the vision-language encoder, is last.** Its image-text pretraining carries less letterform detail.
- **ConvNeXt is the speed floor.** It is about 2x faster on GPU and 3x faster on CPU, at a 7-point Top-1 cost. The new homogeneity check no longer needs patch tokens, so ConvNeXt was a full candidate here.
- **Against the speed target** (SRS REQ-5.1-1: ≤ 5 regions in ~10 s on the demo laptop, CPU acceptable):
  - One embedding of the final model costs 26 ms on GPU and 332 ms on CPU.
  - The homogeneity check adds 14 more passes per crop, so a crop needs 15 passes: about 0.4 s on GPU, but about **5 s on CPU**.
  - Five regions then take about 2 s on GPU and about **25 s on CPU**, which misses the target before text localization is even counted.
  - **The demo needs the GPU, or the check needs fewer cuts on CPU.** That is a decision for Increment 4.

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
