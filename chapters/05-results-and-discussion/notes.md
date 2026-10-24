# Chapter 5 — Results and Discussion (Planning Blueprint)

## Purpose and Scope
- Report empirical findings from Increments 1–3 (`reports/incr2/FINDINGS.md`, `reports/incr3/FINDINGS.md`) and map them to the five research questions (Ch1 §1.5) and validation protocol (Ch4 §4.10.2).
- Strictly planning notes only; chapter prose lives in `draft.md`.
- Maintain strict separation of facts (no repetition of Ch3 equations or Ch4 procedures).
- Preserve `[X.X%]` / `[κ = X.XX]` placeholders ONLY for the pending real-generative human-proxy panel (`reports/real/real_eval.json` not yet run). All synthetic test and validation numbers are frozen and final.

## Section Map & Evidence Sources

### 5.1 Experimental Setup and Hardware Verification
- Partition summary: 46,000 palette crops (80 fonts × 575, 70/15/15 stratified split → 6,905 test crops), 11,500 unknown-font crops (20 fonts × 575, split 10 validation / 10 test → 5,750 test crops), 4,000 mixed-font stressor crops (2,000 validation / 2,000 test).
- Hardware parity check (`open_set_laptop_validation.json` vs `open_set_dinov2_mid_oe.json`): SVC1 (NVIDIA GB10, torch 2.14.0+cu130) vs laptop (RTX 3050, torch 2.6.0+cu124) after SVC1 disk failure on 2026-10-02. Validation Top-1: 50.14% vs 50.16%; FPR@95: 74.56% vs 74.63%; AUROC: 0.7083 vs 0.7083.

### 5.2 Metric Embedding and Training Ablations (RQ1, RQ2)
- **Frozen vs. Head (`dinov2.json`, `dinov2_cv.json`, Fig 12 `embedding_tsne.png`):**
  - Frozen DINOv2 block 12: 12.45% Top-1, 26.11% Top-3, 66.01% family.
  - Trained head (block 12, 5-fold CV): 43.79% ± 0.33% Top-1, 66.36% ± 0.29% Top-3, 88.38% ± 0.50% family.
- **Triplet mining & hyperparameter sweep (`sweep.json`, `dinov2_combo.json`, `dinov2_nokd.json`, `teacher10.json`, Table 6):**
  - Batch-hard collapsed to constant 0.2 margin loss from epoch 1 (23.1% vs 38.9% batch-all on laptop) due to severe-tier noise.
  - Sweep from 41.06% baseline: 120 epochs (+1.06 → 42.12%), P=16×K=8 (+0.93 → 41.99%), KD weight 0.5 (+0.59 → 41.65%); combined = 43.41%.
  - Removing KD drops 43.70% → 40.41% (-3.29 pts). Heavy KD (2.0 / 4.0) drops to 39.54% / 38.87%.
  - Teacher 5 epochs (60.2%) → 10 epochs (64.2%) only lifts student +0.29 pts (43.41% → 43.70%). Frozen features are the bottleneck.
- **Multi-layer feature extraction (`dinov2_mid_cv.json`, `dinov2_last4_cv.json`, Table 7):**
  - Blocks 3, 6, 9, 12 (6144-d): 51.27% ± 0.41% Top-1 (+7.48 pts), 73.16% Top-3, 90.54% family. Severe tier jumps from 23.43% to 29.93% (+6.50 pts).
  - Blocks 9, 10, 11, 12: 50.29% ± 0.58% Top-1, 29.03% severe.
  - Raw frozen 3/6/9/12 without head drops to 9.29% (vs 12.45% block 12): intermediate stroke detail requires learned projection.

### 5.3 Open-Set Rejection and Mixed-Typography Detection (RQ3)
- **Outlier exposure (`open_set_dinov2.json`, `open_set_dinov2_mid.json`, `open_set_oe_*.json`, Table 8):**
  - Plain multi-layer head: validation FPR@95 = 86.9% ± 0.2% (3 seeds), AUROC = 0.654 (block 12 head: 92.2%, AUROC 0.614). Pristine median cosine similarity: 0.836 unknown vs 0.868 known. Alternative post-hoc scores (1-NN AUROC 0.676, margin 0.49, softmax 0.53) do not solve representation overlap.
  - Outlier exposure (40 background fonts, 128 crops/batch, margin 0.4): validation FPR@95 = 75.3% ± 2.4% (3 seeds), AUROC = 0.705, known Top-1 = 50.28% (-1.02 pts).
  - 120 background fonts (100 crops each): FPR@95 = 79.7% ± 1.3%, AUROC = 0.703 (dilutes boundary-adjacent look-alikes).
- **Test-set open-set rejection and per-font breakdown (`open_set_dinov2_mid_oe_final.json`, Table 9, Table 10):**
  - Calibrated $\tau = 0.7191$ (95.0% val recall → 95.2% test recall). Test FPR@95 = 75.6%, AUROC = 0.687.
  - Acceptance by unknown family: display 41.5% (Bangers 17.4%, Special Elite 65.6%), sans-serif 71.7% (Smooch Sans 19.3%, Jost 87.5%, Space Grotesk 87.7%, Karla 92.3%), monospace 95.3% (Courier Prime 95.3%), serif 97.0% (Sanchez 94.8%, Frank Ruhl Libre 97.2%, Cormorant 99.1% mistaken for Cormorant Garamond 484/575 times).
- **Homogeneity check (`homogeneity.json`, `homogeneity_search.json`, `homogeneity_tune.json`, `homogeneity_final.json`, Table 11):**
  - Patch-column clustering failed: 4.5% whole-word, 2.4% mid-word, 2.4% interleaved at 4.8% false alarm (column tokens encode character identity).
  - Untuned 20–80% cut search: AUROC 0.669 (edge cuts leave noisy 1-letter fragments).
  - Tuned 35–65% cut search (min aspect 1.25× height, per-cut z-score, cutoff 2.2905): Test contiguous AUROC = 0.819, detects 45.7% contiguous mixes (52.6% whole-word, 38.5% mid-word; 52.0% cross-family vs 30.7% same-family) at 5.4% false alarm; 59.1% of boundaries within 10% crop width (median error 7.9%).

### 5.4 Comparative Baselines, Error Structure, and Verification Metrics (RQ4, RQ5)
- **Closed-set baselines (`baselines_final.json`, Table 12):**
  - 77 shared fonts with Storia-AI ($n = 6,645$ test crops): Ours 51.4% Top-1 / 73.5% Top-3 vs Storia-AI 21.2% Top-1 / 31.6% Top-3 (7.1% unmasked over 1,677 families). By tier (Storia vs Ours): pristine 46.2% vs 65.9%, mild 35.7% vs 65.6%, moderate 9.9% vs 49.0%, severe 2.5% vs 28.9%.
  - 17 shared families with Chen et al. ($n = 1,466$ test crops): Ours 57.8% Top-1 / 82.6% Top-3 vs Storia-AI 27.9% / 46.5% vs Chen et al. 14.9% / 34.2% (11.1% unmasked over 32 families).
- **Family confusion matrix and severity index (`open_set_dinov2_mid_oe_final.json`, Table 13):**
  - Test family accuracy: 89.7% (6,196 / 6,905). Diagonal retention: serif 96.9% (2,003/2,068), display 89.9% (1,242/1,382), sans-serif 89.2% (2,463/2,762), monospace 70.4% (488/693; 178 or 25.7% confused with sans-serif).
  - Severity index: $\Pi = 0.103$ ($\text{SWER} = 0.0559$, $\text{SWER}_{\text{random}} = 0.5415$).
- **Conformal prediction and re-render verification (`open_set_dinov2_mid_oe_final.json`, `rerender_final.json`, Table 14):**
  - Conformal test coverage: $\alpha = 0.10 \rightarrow 89.9\%$ (mean set size 9.6, median 8.0); $\alpha = 0.05 \rightarrow 94.9\%$ (mean set size 13.4, median 12.0).
  - Re-render verification ($n = 3,000$ test crops): AUROC separating correct vs wrong predictions is 0.710 (SSIM), 0.691 (MSE), 0.664 (DeepSSIM), 0.660 (DeepSSIM-Lite). True-font similarity by tier shows DeepSSIM holds up better on mild (0.485 vs 0.267 SSIM) but collapses on moderate (0.205) and severe (0.087).

### 5.5 Backbone Comparison, Runtime Latency, and Real-Generative Evaluation
- **Backbone comparison and latency (`open_set_bb_*_final.json`, `latency.json`, Table 15):**
  - Single-layer test Top-1 / FPR@95 / AUROC / GPU ms / CPU ms:
    - DINOv2 ViT-B/14: 41.0% / 80.3% / 0.661 / 28.7 ms / 300 ms
    - ConvNeXt-T: 33.8% / 88.8% / 0.620 / 13.8 ms / 98 ms
    - Supervised ViT-B/16: 32.7% / 86.3% / 0.627 / 18.7 ms / 238 ms
    - SigLIP ViT-B/16: 26.0% / 91.7% / 0.605 / 19.5 ms / 269 ms
    - Deployed DINOv2 (blocks 3/6/9/12): 50.2% / 75.6% / 0.687 / 26.3 ms / 332 ms
  - Latency implication for SRS REQ-5.1-1 (5 regions in ≤ 10 s): 15 forward passes per crop (1 crop + 14 homogeneity cuts) = 0.39 s/crop on GPU (~2.0 s for 5 regions, passes) vs 4.98 s/crop on CPU (~24.9 s for 5 regions, exceeds CPU target).
- **Real-generative evaluation (`real.py`, Table 16 with placeholders):**
  - `[N = 100]` crops, 3 expert raters, Fleiss' $\kappa$ for font (`[κ = X.XX]`) and coherence (`[κ = X.XX]`), Top-1/Top-3 on consensus-known crops, rejection rate on consensus-unknown crops, homogeneity agreement on consensus-coherence crops.
