# Chapter 5: Results and Discussion

## 5.1 Overview and Experimental Integrity

This chapter presents the empirical results of Increments 1 through 3 and evaluates them against the five research questions of Section 1.5 and the validation protocol of Section 4.10.2. Section 5.2 examines the metric embedding and its training ablations (Research Questions 1 and 2). Section 5.3 evaluates open-set rejection and mixed-typography detection (Research Question 3). Section 5.4 benchmarks the deployed recognizer against the closed-set baselines, analyzes the family-level error distribution, and tests the conformal and re-render verification metrics (Research Questions 4 and 5). Section 5.5 reports the four-backbone comparison, measures per-crop inference latency against the interactive target of the Software Requirements Specification (Appendix A), and sets out the evaluation framework for the real-generative benchmark.

All synthetic evaluations follow the partition rules of Section 4.3.2. Every design decision, including the choice of DINOv2 encoder blocks, batch composition, distillation weight, outlier-exposure load, and the homogeneity cut grid, was made on the validation partition (6,900 palette crops, 5,750 crops across the 10 validation unknown fonts, and 2,000 mixed-font validation crops). Once those choices were fixed, the final model was evaluated once on the untouched test partition: 6,905 known crops across the 80 palette fonts, 5,750 crops across the 10 held-out test unknown fonts, and 2,000 mixed-font test crops. No parameter was adjusted after the test split was unsealed.

Model training and the Increment 2 ablations ran on an NVIDIA GB10 server (`torch 2.14.0+cu130`). After a hardware storage failure on that server during Increment 3, the rescued checkpoints were moved to the deployment laptop (NVIDIA RTX 3050 Laptop GPU, 14-thread Intel CPU, `torch 2.6.0+cu124`), where features were recomputed and the final test pass was executed. Because floating-point reductions differ slightly across GPU architectures and CUDA releases, the two machines are never mixed inside a single comparison table. A parity check on the full validation split confirmed that the laptop reproduces the server's final model within rounding noise: validation Top-1 accuracy measured 50.14% on the laptop against 50.16% on the server, false-positive rate at 95% recall (FPR@95) measured 74.56% against 74.63%, and open-set AUROC matched to four decimal places at 0.7083.

## 5.2 Metric Embedding and Training Ablations

The first two research questions ask whether the synthetic degradation corpus can train a recognizer that separates typographic identity from generative distortion, and how much of that separation comes from the metric head rather than the frozen Vision Transformer alone.

### 5.2.1 Frozen Backbone Versus the Trained Metric Head

Before training any projection parameters, the frozen DINOv2 ViT-B/14 encoder (`facebook/dinov2-base`) was evaluated directly by taking the concatenated class token and mean patch token of its twelfth block (1,536 dimensions, $L_2$-normalized) and scoring validation crops by nearest-prototype cosine similarity. Across the 80 palette fonts, random guessing yields 1.25% Top-1 accuracy. The raw frozen features reach 12.45% Top-1 accuracy, 26.11% Top-3 accuracy, and 66.01% family-level accuracy. That is ten times chance, which confirms that self-supervised pretraining captures some stroke and proportion cues without font supervision, but it leaves nearly seven in eight crops misclassified.

Adding the two-layer metric head $f_\theta$ of Section 4.3.2 changes the geometry of the space. On the same block-12 features, five-fold stratified cross-validation across the combined training and validation partitions raises Top-1 accuracy to 43.79% $\pm$ 0.33%, Top-3 accuracy to 66.36% $\pm$ 0.29%, and family accuracy to 88.38% $\pm$ 0.50%. Figure 12 shows this shift on 4,000 seeded validation crops projected into two dimensions with cosine t-SNE.

**Figure 12**

*t-SNE Projection of Validation Crops Under Frozen DINOv2 Features and the Trained Metric Head*

![Two-panel scatter plot of 4,000 validation crops projected with cosine t-SNE, colored by the four structural family classes (sans-serif in teal, serif in blue, display in orange, monospace in rose). Left panel, Frozen DINOv2 features: the four color groups overlap across a single central cloud with no clear class boundaries. Right panel, Trained metric head f-theta: the four structural families separate into distinct regional clusters, with serif, sans-serif, display, and monospace occupying well-defined territories](../../assets/figures/embedding_tsne.png)

*Note.* Each point is one validation crop from the synthetic corpus ($n = 4,000$, random seed 2026), colored by true `family_class`. Both panels project the same crops from the deployed multi-layer feature set before and after the metric head $f_\theta$.

In the left panel of Figure 12, frozen DINOv2 features group crops largely by word length, ink density, and distortion level rather than typeface, leaving serif, sans-serif, display, and monospace crops mingled across the plane. In the right panel, the trained head pulls the four structural families into separate regions and tightens individual fonts into local neighborhoods. Even when a deformed crop misses its exact font prototype, almost nine out of ten predictions stay inside the right structural family.

### 5.2.2 Triplet Mining, Batch Composition, and Knowledge Distillation

Reaching a stable embedding on deformed text required changing how triplets are mined. The initial implementation used batch-hard mining (Hermans et al., 2017), which updates each anchor using only its farthest same-font crop and its nearest different-font crop inside the mini-batch. On this corpus, batch-hard training collapsed immediately: the triplet loss locked onto the exact margin value (0.2000) from the first epoch and mapped every crop toward a single point, yielding 23.1% Top-1 accuracy on exploratory laptop runs. The cause lies in the severe degradation tier ($\theta$ up to 0.90). When elastic warp and kerning jitter push a glyph near illegibility, the hardest positive in a batch is practically pure noise, and forcing the network to pull that outlier crop ahead of cleaner crops destabilizes the gradients. Switching to batch-all mining, which averages over every margin-violating triplet in the mini-batch, removed the collapse and lifted the same laptop configuration to 38.9%.

With batch-all mining fixed, a one-factor-at-a-time sweep on the server tested which hyperparameters move validation accuracy away from the initial baseline of 41.06% (60 epochs, batches of $P = 32$ fonts $\times K = 4$ crops, margin $\alpha = 0.2$, distillation weight $\lambda_{\text{KD}} = 1.0$, temperature $\tau_{\text{KD}} = 0.1$, and the five-epoch LoRA teacher). Table 6 reports the sweep.

**Table 6**

*Validation Sweep of Metric Head Training Settings on Block-12 DINOv2 Features*

| Configuration change from baseline | Validation Top-1 (%) | Validation Top-3 (%) | Change vs. 41.06% (pp) |
| :--- | :---: | :---: | :---: |
| Baseline ($60\text{ epochs}, P=32 \times K=4, \lambda_{\text{KD}}=1.0$) | 41.06 | 63.84 | 0.00 |
| Training length doubled to 120 epochs | 42.12 | 64.91 | +1.06 |
| Batch composition shifted to $P=16 \times K=8$ | 41.99 | 64.68 | +0.93 |
| Distillation weight reduced to $\lambda_{\text{KD}}=0.5$ | 41.65 | 64.30 | +0.59 |
| Margin $\alpha \in \{0.1, 0.4\}$, learning rate $\times 0.5$ or $\times 2$, head dim 128 or 512 | 40.40 to 41.20 | 63.10 to 64.05 | $-0.66$ to $+0.14$ |
| Batch composition shifted to $P=64 \times K=2$ | 40.00 | 62.71 | $-1.06$ |
| Distillation temperature lowered to $\tau_{\text{KD}}=0.05$ | 39.74 | 62.45 | $-1.32$ |
| Distillation weight raised to $\lambda_{\text{KD}}=2.0$ | 39.54 | 62.19 | $-1.52$ |
| Distillation weight raised to $\lambda_{\text{KD}}=4.0$ | 38.87 | 61.50 | $-2.19$ |
| Combined gains ($120\text{ epochs}, P=16 \times K=8, \lambda_{\text{KD}}=0.5$, 5-epoch teacher) | 43.41 | 65.42 | +2.35 |
| Combined gains + 10-epoch LoRA teacher | 43.70 | 65.61 | +2.64 |
| Combined gains without distillation ($\lambda_{\text{KD}}=0.0$) | 40.41 | 63.07 | $-0.65$ |

*Note.* All runs were executed on the server validation split ($n = 6,900$ crops) using frozen block-12 DINOv2 features. Because five-fold cross-validation shows a fold-to-fold standard deviation of $\pm 0.33$ percentage points, single-run shifts smaller than roughly $0.7$ points lie within sampling noise.

Three results stand out in Table 6. First, giving each batch more crops per font ($P = 16 \times K = 8$, yielding 28 positive pairs per font per batch instead of 6 at $P = 32 \times K = 4$) helps batch-all mining much more than packing more distinct fonts into the batch ($P = 64 \times K = 2$, which drops 1.06 points). Second, knowledge distillation from the LoRA teacher contributes a genuine 3.29-point gain under the tuned schedule (43.70% with $\lambda_{\text{KD}} = 0.5$ versus 40.41% without distillation), but only when kept subordinate to the triplet loss. Pushing $\lambda_{\text{KD}}$ up to 2.0 or 4.0 degrades accuracy below the un-tuned baseline, because the teacher itself is imperfect and pulling the student too tightly toward the teacher's similarity matrix forces the student to copy its errors.

Third, improving the teacher further brings almost no return to the student. Extending LoRA teacher training from 5 epochs to 10 epochs raised the teacher's own closed-set validation accuracy from 60.2% to 64.2% (where it plateaued by epoch 8), yet the student distilled from that stronger teacher improved by only 0.29 percentage points, from 43.41% to 43.70%. Across every hyperparameter combination in Table 6, accuracy on the severe deformation tier stayed locked between 22.6% and 24.7%. The bottleneck was no longer how the head was trained or how well the teacher supervised it. The bottleneck was what survived inside the last block of the frozen backbone.

### 5.2.3 Multi-Layer Feature Extraction

In a Vision Transformer pretrained with self-supervised objectives, later blocks specialize toward global semantic abstraction while intermediate blocks retain finer spatial and edge structure (Oquab et al., 2024). Because font recognition depends on terminal shape, stroke contrast, and aperture geometry rather than word meaning, reading only the twelfth block discards detail that earlier layers still carry.

To test this without unfreezing the encoder, two multi-layer variants were evaluated under five-fold cross-validation with every training setting from Section 5.2.2 held constant. Each variant reads the class token and mean patch token from four blocks, passes each block's tokens through DINOv2's final layer normalization, and concatenates them into a 6,144-dimensional vector. The first variant samples evenly across network depth (blocks 3, 6, 9, and 12); the second reads the final four blocks (blocks 9, 10, 11, and 12). Table 7 compares both against the single-block head.

**Table 7**

*Five-Fold Cross-Validation Accuracy by DINOv2 Block Selection*

| DINOv2 blocks read (input dim) | Top-1 (%) | Top-3 (%) | Family (%) | Pristine (%) | Mild (%) | Moderate (%) | Severe (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Block 12 only (1,536-d) | $43.79 \pm 0.33$ | $66.36 \pm 0.29$ | $88.38 \pm 0.50$ | $60.58 \pm 0.91$ | $56.09 \pm 0.84$ | $40.40 \pm 0.52$ | $23.43 \pm 0.51$ |
| Blocks 9, 10, 11, 12 (6,144-d) | $50.29 \pm 0.58$ | $72.22 \pm 0.34$ | $90.27 \pm 0.31$ | $66.29 \pm 0.88$ | $63.24 \pm 1.12$ | $47.81 \pm 0.67$ | $29.03 \pm 0.78$ |
| Blocks 3, 6, 9, 12 (6,144-d) | $51.27 \pm 0.41$ | $73.16 \pm 0.13$ | $90.54 \pm 0.25$ | $65.99 \pm 0.94$ | $64.40 \pm 1.41$ | $48.92 \pm 0.46$ | $29.93 \pm 0.41$ |

*Note.* Values report mean $\pm$ standard deviation across 5 stratified folds on the combined training and validation partitions ($n = 39,095$ crops).

Reading four blocks across depth (blocks 3, 6, 9, and 12) produced the largest single gain in the study: Top-1 accuracy jumped 7.48 percentage points to 51.27%, Top-3 rose 6.80 points to 73.16%, and family accuracy crossed 90.5%. More importantly, the severe deformation tier moved for the first time, climbing 6.50 points from 23.43% to 29.93%. Every structural family shared in the gain: serif accuracy rose from 47.96% to 57.49%, sans-serif from 31.15% to 38.62%, monospace from 26.34% to 31.53%, and display from 71.53% to 77.08%.

Spreading the readout across blocks 3, 6, 9, and 12 beat stacking the last four blocks (9 through 12) by 0.98 percentage points, roughly two cross-validation standard deviations, with most of the edge appearing on mild and moderate distortion. At the same time, evaluating the raw 6,144-dimensional features *without* the trained head actually scored worse than block 12 alone (nearest-prototype Top-1 dropped from 12.45% to 9.29%). Earlier transformer blocks preserve fine letterform traits, but those traits sit mixed with spatial and background variance that only a learned projection can untangle.

## 5.3 Open-Set Rejection and Mixed-Typography Detection

Research Question 3 asks whether an open-set rejection mechanism can route out-of-palette or incoherent crops away from false palette matches. Increment 3 tested two defenses: prototype-similarity thresholding with outlier exposure for unseen fonts, and the width cut-search for crops containing more than one typeface.

### 5.3.1 Outlier Exposure and the Open-Set Decision

When the multi-layer head of Section 5.2.3 was evaluated without background negatives on the 10 validation unknown fonts (5,750 crops), setting $\tau$ at 95% recall on known validation crops accepted 87.1% of unknown-font crops as false positives (AUROC 0.654; the single-layer block-12 head was worse still at 92.2% FPR@95 and 0.614 AUROC). Deformation was not the primary culprit. Even on pristine renders, unknown fonts sat almost as close to their nearest palette prototype as known fonts did (median cosine similarity 0.836 versus 0.868). Changing how the frozen embedding was scored did not rescue rejection: on the same embeddings, 1-nearest-neighbor distance over all 32,195 training crops reached 83.3% FPR@95 (AUROC 0.676), while top-two prototype margin and prototype softmax scored worse than raw cosine similarity (AUROC 0.49 and 0.53). Because standard triplet training only pushes the 80 known fonts apart from one another, an unseen font lands beside whichever palette font shares its general proportions.

To give the embedding an explicit reason to push non-palette faces away from the prototypes, background fonts were introduced into every training batch as negative-only anchors following Hendrycks et al. (2019), as specified in Section 4.3.2. Table 8 summarizes the validation runs across three random seeds per configuration.

**Table 8**

*Open-Set Rejection on Validation Unknown Fonts Across Outlier-Exposure Configurations*

| Outlier-exposure configuration | FPR@95 by seed (%) | FPR@95 mean $\pm$ SD (%) | Open-set AUROC | Known val Top-1 (%) |
| :--- | :---: | :---: | :---: | :---: |
| No outlier exposure (0 background fonts) | 87.1, 86.7, 86.8 | $86.9 \pm 0.2$ | 0.654 | 51.30 |
| 40 background fonts (128 crops/batch, $\alpha = 0.4$) | 74.6, 73.3, 77.9 | $75.3 \pm 2.4$ | 0.705 | 50.28 |
| 120 background fonts (128 crops/batch, $\alpha = 0.4$) | 81.3, 79.2, 78.8 | $79.7 \pm 1.3$ | 0.703 | 50.60 |
| 40 background fonts (32 crops/batch, $\alpha = 0.2$, 1 seed) | 82.4 | 82.4 | 0.679 | 50.91 |
| 40 background fonts (256 crops/batch, $\alpha = 0.4$, 1 seed) | 76.1 | 76.1 | 0.701 | 49.42 |
| 40 background fonts (128 crops/batch, $\alpha = 0.6$, 1 seed) | 77.8 | 77.8 | 0.696 | 49.15 |

*Note.* Evaluated on the 10 validation unknown fonts ($n = 5,750$ crops) with $\tau$ calibrated at 95.0% recall on known validation crops ($n = 6,900$). All models use DINOv2 blocks 3, 6, 9, and 12.

Adding 128 background crops per batch from the 40 typefaces ranked immediately below the unknown set cut FPR@95 by 11.6 percentage points (from 86.9% to 75.3%) and raised AUROC from 0.654 to 0.705, at the cost of roughly one percentage point of closed-set Top-1 accuracy (51.30% to 50.28%). Tripling the auxiliary pool to 120 background fonts (`data/background_x3.csv`, keeping the total rendering budget fixed at 12,000 crops) did not improve rejection; it worsened mean FPR@95 to 79.7%. Because the first 40 background fonts sit closest to the popularity cutoff, they supply harder, more palette-like negatives than the rarer ornamental faces further down the list, which dilute the repulsive gradient.

### 5.3.2 Final Test-Set Rejection and the Look-Alike Ceiling

With the 40-font outlier-exposure head frozen and $\tau$ calibrated on validation at $\tau = 0.7191$, the model was evaluated once on the test partition and the 10 held-out test unknown fonts. Table 9 summarizes the primary test-set metrics of the deployed recognizer, and Table 10 breaks down rejection across the 10 unseen test fonts.

**Table 9**

*Final Test-Set Performance of the Deployed Font Recognizer*

| Evaluation measure | Validation split | Test split |
| :--- | :---: | :---: |
| Closed-set Top-1 accuracy (80 palette fonts) | 50.2% | 50.2% |
| Closed-set Top-3 accuracy (80 palette fonts) | 71.3% | 72.2% |
| Structural family accuracy (4 classes) | 89.7% | 89.7% |
| Embedding-centroid severity index $\Pi$ | 0.103 | 0.103 |
| Known-font recall at $\tau = 0.7191$ | 95.0% | 95.2% |
| Known-font Top-1 accuracy among accepted crops | 51.3% | 51.4% |
| Unknown-font false-positive rate (FPR@95) | 74.6% | 75.6% |
| Known-versus-unknown AUROC | 0.708 | 0.687 |
| Conformal coverage at $\alpha = 0.10$ (mean / median set size) | 89.6% (9.6 / 8.0) | 89.9% (9.6 / 8.0) |
| Conformal coverage at $\alpha = 0.05$ (mean / median set size) | 94.8% (13.7 / 12.0) | 94.9% (13.4 / 12.0) |

*Note.* Test partition comprises $n = 6,905$ known crops and $n = 5,750$ unknown crops across the 10 held-out test fonts.

**Table 10**

*Test-Set Acceptance Rate and Top Confusions for Held-Out Unknown Fonts*

| Unknown test font | Family class | Wrongly accepted at $\tau = 0.7191$ (%) | Rejected as unknown (%) | Most frequent palette match ($n / 575$) |
| :--- | :---: | :---: | :---: | :--- |
| Bangers | Display | 17.4 | 82.6 | Bebas Neue (49), Lilita One (17), Oleo Script (14) |
| Smooch Sans | Sans-serif | 19.3 | 80.7 | Instrument Serif (37), Inconsolata (19), Barlow (18) |
| Special Elite | Display | 65.6 | 34.4 | Arvo (138), Zilla Slab (121), Slabo 27px (33) |
| Jost | Sans-serif | 87.5 | 12.5 | Google Sans (81), Outfit (73), Figtree (45) |
| Space Grotesk | Sans-serif | 87.7 | 12.3 | Work Sans (73), Figtree (40), Plus Jakarta Sans (35) |
| Karla | Sans-serif | 92.3 | 7.7 | Work Sans (62), Lato (52), Source Sans 3 (46) |
| Sanchez | Serif | 94.8 | 5.2 | Zilla Slab (187), Arvo (158), Roboto Slab (84) |
| Courier Prime | Monospace | 95.3 | 4.7 | Arvo (172), Zilla Slab (123), Space Mono (87) |
| Frank Ruhl Libre | Serif | 97.2 | 2.8 | Lora (180), Playfair Display (117), Fraunces (106) |
| Cormorant | Serif | 99.1 | 0.9 | Cormorant Garamond (484), Cinzel (42), EB Garamond (17) |

*Note.* Each unknown test font is evaluated across $n = 575$ crops spanning all four deformation tiers.

Table 10 explains why overall FPR@95 settles at 75.6% despite outlier exposure. Rejection is bimodal across font families. Unseen display and ultra-condensed faces whose silhouettes sit outside the palette's core geometry are rejected reliably: 82.6% of Bangers crops and 80.7% of Smooch Sans crops receive the "unknown" verdict, and the same pattern held on validation unknown fonts after outlier exposure (Creepster acceptance dropped from 67% to 32%, Share Tech from 79% to 35%, and Saira from 82% to 38%).

By contrast, unseen serif, neo-grotesque sans-serif, and slab-monospace faces that have a near-twin inside the 80-font palette are almost always accepted and mapped to that twin. Cormorant is accepted 99.1% of the time and matched to Cormorant Garamond, its sister revival from the same type family, on 484 of 575 crops. Sanchez, a slab serif, maps to Zilla Slab and Arvo; Jost, a geometric sans, maps to Google Sans and Outfit. Because the unknown set was constructed from the next 20 most popular Google Fonts rather than arbitrary decorative faces, many of its members are structural cousins of palette fonts. Under a frozen backbone, the metric head can reject genuinely novel display geometry, but it cannot tell "looks like Zilla Slab" apart from "is Zilla Slab." Whether this failure mode is harmless for template reconstruction depends on how close the returned font is to the true one, and this study collected no human judgment of that. A structural proxy is available. Of the 2,710 wrongly accepted crops covered by the three most frequent matches per font in Table 10, 74.5% (2,018) were assigned to a palette font of the unknown font's own structural family (`family_match.json`). The pattern is uneven. Cormorant, Frank Ruhl Libre, Sanchez, Jost, Karla, and Space Grotesk stayed within their family on every listed match (Cormorant maps to its sister revival Cormorant Garamond on 484 of 575 crops), which suggests a usable look-alike. Courier Prime, a monospace face, was matched mostly to proportional slab serifs (23% in family), Special Elite only to slab serifs, and Smooch Sans partly to a serif face, so for monospace and display faces a wrong acceptance can hand the designer a visibly different font. A same-family match is necessary but not sufficient for a usable substitute, and rating the returned font against the true one is left to future work.

### 5.3.3 Homogeneity Check for Mixed Typography

Section 4.4.2 requires the recognizer to check whether a word crop contains more than one typeface before trusting a single prototype match. The original design pooled block-12 patch tokens by image column (ignoring empty background columns either by ink mask or by class-token attention) and split the column vectors into two clusters. When tested on the validation half of the mixed-font stressor set ($n = 2,000$ two-font crops against $n = 3,000$ single-font crops, with the cutoff calibrated at a 5% single-font false-alarm rate), that column-pooling design failed completely. It flagged only 4.5% of whole-word mixes, 2.4% of mid-word mixes, and 2.4% of character-interleaved crops, indistinguishable from its 4.8% false-alarm rate on single-font crops. Inspecting the column features showed why: a vertical strip of patch tokens is dominated by *which letter* occupies those columns (for instance, a round `O` versus a vertical `I`), and that letter-to-letter variance inside one font is much larger than the stylistic difference between two fonts.

Replacing raw patch columns with the trained metric embedding solved the problem, because $f_\theta$ is explicitly trained to discard letter identity and keep font style. An initial probe that simply cut each crop at its horizontal midpoint and measured the cosine distance between the left and right embeddings achieved an AUROC of 0.811 on contiguous mixes (and 0.932 when cut at the exact ground-truth boundary). However, a naive search across all cut positions from 20% to 80% of the crop width dropped validation AUROC back to 0.669 (`homogeneity_search.json`), because cuts near the left or right edge leave a narrow sliver containing a single character whose embedding is noisy, inflating the maximum distance even on single-font crops.

Offline tuning across 30 cut-search variants (`homogeneity_tune.json`) identified two constraints that eliminate edge noise: restricting candidate cuts to the central band from 35% to 65% of crop width (seven positions in 5% steps), and refusing any cut that leaves either piece narrower than 1.25 times the crop height (roughly two characters). Standardizing each cut position's cosine distance by the mean and standard deviation of single-font crops at that same position equalizes the remaining variance across cuts. Table 11 compares the failed column-pooling check, the untuned width search, and the final calibrated check on the untouched test half of the stressor set.

**Table 11**

*Homogeneity Check Performance Across Methods and Mixing Conditions*

| Method and evaluation split | Single-font false alarm (%) | Contiguous AUROC | Whole-word mix detected (%) | Mid-word mix detected (%) | Interleaved detected (%) | Boundary within $\pm 10\%$ width (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Patch-column clustering (ink mask, val) | 4.8 | 0.512 | 4.5 | 2.4 | 2.4 | N/A |
| Patch-column clustering (CLS attention, val) | 4.9 | 0.504 | 3.2 | 1.8 | 1.0 | N/A |
| Untuned cut search (20% to 80% width, val) | 5.3 | 0.669 | 24.4 | 12.8 | 10.7 | 31.2 |
| Tuned cut search (35% to 65% width, val) | 3.8 | 0.814 | 52.0 | 35.2 | 11.2 | 59.5 |
| Tuned cut search (35% to 65% width, test) | 5.4 | 0.819 | 52.6 | 38.5 | 12.7 | 59.1 |

*Note.* Test evaluation covers $n = 3,000$ single-font test crops and $n = 2,000$ mixed-font test crops (40% whole-word, 40% mid-word at 25/50/75%, 20% per-character interleaved), using the validation-calibrated cutoff of $z = 2.2905$.

On the held-out test split, the tuned cut search reaches an AUROC of 0.819 on contiguous two-font crops at a 5.4% false-alarm rate (against the 5.0% calibration target). It flags 45.7% of all contiguous mixes, detecting whole-word font changes (52.6%) more often than mid-word switches (38.5%), and cross-family pairs (52.0%) much more reliably than pairs drawn from the same structural family (30.7%). Across deformation tiers, contiguous detection holds at 49.0% on pristine crops, 59.6% on mild, and 44.9% on moderate, before dropping to 29.0% under severe distortion. When the check flags a crop, its chosen cut lands within 10% of the true A-to-B font transition on 59.1% of cases (median boundary error 7.9% of crop width). That is accurate enough to split the two halves and match each one on its own. Character-interleaved crops are rarely caught (12.7%), because every horizontal cut leaves both fonts mixed on both sides of the boundary.

## 5.4 Comparative Baselines, Error Structure, and Verification Metrics

Research Questions 4 and 5 ask how the recognizer's Top-K accuracy compares against published closed-set baselines and whether its remaining errors stay inside the true font's structural family.

### 5.4.1 Comparison Against Closed-Set Baselines

The deployed model was benchmarked on the synthetic test partition against the two reference classifiers of Section 4.10.2: Storia-AI's Google Font Classifier (ResNet-50 over 1,677 Google Font families; Jiang et al., 2025) and the DINOv2-LoRA classifier of Chen et al. (2026; released `font_classifier_v4` weights covering 394 variants across 32 families). Each baseline was run with its own published preprocessing and checkpoint weights, and variant predictions were folded to font family level so neither baseline was penalized for weight-variant mismatches.

To keep the comparison fair, each baseline was scored both over its full native output space and under a restricted mask containing only the palette fonts that exist in its training catalogue (77 shared fonts for Storia-AI, which lacks Google Sans, Geist Mono, and Ubuntu; 17 shared fonts for Chen et al.). Under the restricted mask, the baseline answers the exact same closed-set multiple-choice question over the exact same test crops as our model. Table 12 presents the results.

**Table 12**

*Closed-Set Accuracy by Deformation Tier Against Published Baselines on Shared Test Fonts*

| Evaluation subset and model | Overall Top-1 (%) | Overall Top-3 (%) | Pristine Top-1 (%) | Mild Top-1 (%) | Moderate Top-1 (%) | Severe Top-1 (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| *77 shared fonts ($n = 6,645$ test crops)* | | | | | | |
| Storia-AI (unmasked, 1,677 families) | 7.1 | 12.9 | 21.8 | 11.7 | 1.0 | 0.1 |
| Storia-AI (restricted to 77 shared fonts) | 21.2 | 31.6 | 46.2 | 35.7 | 9.9 | 2.5 |
| Proposed metric recognizer (same 77 fonts) | 51.4 | 73.5 | 65.9 | 65.6 | 49.0 | 28.9 |
| *17 shared fonts ($n = 1,466$ test crops)* | | | | | | |
| Chen et al. (2026) v2 (unmasked, 32 families) | 11.1 | 22.8 | 9.7 | 13.4 | 12.7 | 7.3 |
| Chen et al. (2026) v2 (restricted to 17 shared fonts) | 14.9 | 34.2 | 15.9 | 17.7 | 16.1 | 9.7 |
| Storia-AI (restricted to 17 shared fonts) | 27.9 | 46.5 | 56.6 | 42.6 | 15.9 | 7.3 |
| Proposed metric recognizer (same 17 fonts) | 57.8 | 82.6 | 72.1 | 69.1 | 56.5 | 37.4 |

*Note.* Chance Top-1 accuracy is 1.30% on the 77-font subset and 5.88% on the 17-font subset. Neither baseline includes an open-set rejection mechanism, yielding 100% FPR on unknown fonts by construction.

Table 12 confirms the central hypothesis of Chapter 1. On the 77 shared fonts, Storia-AI is competitive when glyphs arrive undeformed (46.2% Top-1 on pristine crops, and 56.6% on the 17-font subset), but its accuracy collapses as soon as generative-style distortion enters the image: it drops to 35.7% under mild distortion, 9.9% under moderate distortion, and 2.5% under severe distortion, barely above the 1.3% random floor. By training across the degradation distribution $D$ and projecting multi-layer DINOv2 features, our recognizer holds 65.6% on mild distortion, 49.0% on moderate distortion, and 28.9% on severe distortion. Across all 77 fonts, it leads Storia-AI by 30.2 percentage points in Top-1 accuracy (51.4% versus 21.2%) and more than doubles its Top-3 recall (73.5% versus 31.6%). Even on the 10 unknown test fonts, all of which exist inside Storia-AI's 1,677-family catalogue, Storia-AI names the right family on only 8.5% of crops overall and 0.0% at severe distortion.

On the 17-font subset shared with Chen et al. (2026), our recognizer reaches 57.8% Top-1 and 82.6% Top-3. That is 29.9 points ahead of Storia-AI and 42.9 points ahead of Chen et al.'s released checkpoint. Chen et al.'s model underperforms even on pristine crops (15.9% restricted Top-1), despite using its exact deployed preprocessing (`handler.py`) and despite its model card reporting 99.0% accuracy on its own synthetic test split. Diagnostic checks on clean, full-size renders showed that the released checkpoint is highly sensitive to foreground-background polarity and tight ink-box cropping, so it does not transfer well outside its own rendering script. That sensitivity is a property of the released weights on external crops rather than a verdict on LoRA fine-tuning itself, since our own LoRA teacher trained on the present corpus reached 64.2% validation Top-1 (Section 5.2.2).

### 5.4.2 Family Confusion and Error Severity

Research Question 5 asks whether the recognizer's mistakes stay visually close to the ground-truth font when it misses the exact Top-1 match. Table 13 gives the confusion matrix across the four structural family classes on the 6,905 known test crops.

**Table 13**

*Test-Set Confusion Matrix Across Structural Font Families*

| True family class | Predicted sans-serif | Predicted serif | Predicted display | Predicted monospace | Row total | Within-family recall (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Sans-serif (32 fonts) | 2,463 | 45 | 111 | 143 | 2,762 | 89.2 |
| Serif (24 fonts) | 35 | 2,003 | 9 | 21 | 2,068 | 96.9 |
| Display (16 fonts) | 121 | 14 | 1,242 | 5 | 1,382 | 89.9 |
| Monospace (8 fonts) | 178 | 19 | 8 | 488 | 693 | 70.4 |
| Column total | 2,797 | 2,081 | 1,370 | 657 | 6,905 | 89.7 (overall) |

*Note.* Evaluated on all $n = 6,905$ known test crops across the 80 palette fonts.

Across the test split, 6,196 of the 6,905 crops (89.7%) are assigned to a font in their own structural family. Given that Top-1 exact-font accuracy is 50.2%, roughly four out of every five font-level errors (39.5% out of the 49.8% error mass) still land inside the right typographic category.

Errors are not symmetric across categories. Serif faces are the most insulated, with 96.9% within-family recall; their bracketed and slab terminals remain distinct from sans-serif strokes even under moderate blurring and warping. Display faces retain 89.9% within-family recall, leaking mainly into heavy sans-serifs (121 crops, such as condensed display faces mistaken for Bebas Neue or Archivo Black). The primary cross-family confusion runs between monospace and sans-serif: 25.7% of monospace test crops (178 of 693) are predicted as sans-serif, and 5.2% of sans-serif crops (143 of 2,762) are predicted as monospace. Sans-serif and monospace are also the two lowest-scoring families at the individual font level (5-fold CV Top-1 of 38.62% and 31.53%, against 57.49% for serif and 77.08% for display). Both classes are engineered for low stroke contrast and simple, open counters, and once kerning jitter disrupts the fixed character advance of a monospace word, little separates a neo-grotesque sans-serif from a sans-serif code font beyond tiny terminal details that elastic warping erases first.

Weighting every test error by the cosine distance between the predicted and true font prototypes yields a Severity-Weighted Error Rate of $\text{SWER} = 0.0559$, compared with $\text{SWER}_{\text{random}} = 0.5415$ for uniform random guessing across the 80 prototypes. Their ratio, the severity index of Chen et al. (2026), is $\Pi = 0.103$. On average, a mistake made by the recognizer sits at roughly one-tenth the stylistic distance of a random palette font. When the model misses the exact typeface, its prediction lands on a close relative inside the same family.

### 5.4.3 Conformal Prediction Sets and Re-Render Verification

Beyond fixed Top-3 shortlists, rank-calibrated split conformal prediction (Shi et al., 2024; Ding et al., 2025) was evaluated at nominal miscoverage rates of $\alpha = 0.10$ and $\alpha = 0.05$ (Table 9). On the test partition, empirical coverage reached 89.9% at $\alpha = 0.10$ (calibrated cosine threshold 0.3085, mean prediction set size 9.6 fonts, median 8.0) and 94.9% at $\alpha = 0.05$ (threshold 0.3671, mean set size 13.4, median 12.0), matching the nominal 90% and 95% guarantees within 0.1 percentage points. Set sizes adapt to distortion: at $\alpha = 0.10$, mild crops require a mean of 8.5 fonts (96.1% coverage), whereas severe crops widen to 10.2 fonts (74.4% marginal coverage, because extreme distortion pushes some true prototypes below the global quantile).

For the post-hoc verification metric of Objective 4, each test crop ($n = 3,000$ subsampled across tiers) was compared against a clean re-rendering of its predicted font in the crop's exact string and bounding geometry using classical pixel SSIM (Wang et al., 2004), pixel MSE, and two variants of DeepSSIM (Zhang et al., 2024) computed over VGG-16 feature maps. Table 14 reports how well each score separates correct Top-1 predictions from wrong ones, alongside the mean similarity obtained when re-rendering the *true* font across the four deformation tiers.

**Table 14**

*Re-Render Verification AUROC and True-Font Similarity Across Deformation Tiers*

| Structural similarity metric | Correct vs. wrong AUROC | Mean on correct / wrong | True font: Pristine | True font: Mild | True font: Moderate | True font: Severe |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Classical pixel SSIM | 0.710 | 0.311 / 0.130 | 0.986 | 0.267 | 0.059 | 0.023 |
| Pixel MSE (inverted for AUROC) | 0.691 | 0.089 / 0.124 | 0.003 | 0.076 | 0.129 | 0.147 |
| DeepSSIM (VGG-16 stages 1 to 5) | 0.664 | 0.425 / 0.278 | 0.899 | 0.485 | 0.205 | 0.087 |
| DeepSSIM-Lite (VGG-16 stages 1 to 3) | 0.660 | 0.507 / 0.322 | 0.964 | 0.671 | 0.215 | 0.038 |

*Note.* Evaluated on $n = 3,000$ synthetic test crops (Top-1 accuracy on this subsample is 48.9%). For MSE, lower values indicate closer agreement; for SSIM, DeepSSIM, and DeepSSIM-Lite, higher values indicate closer agreement.

The re-render experiment yielded an instructive negative finding. DeepSSIM was included on the expectation that computing structural similarity over pooled VGG feature maps would tolerate geometric misalignment better than pixel-aligned SSIM (Zhang et al., 2024). Under mild distortion, that expectation holds: when the true font is re-rendered against a mildly warped crop, pixel SSIM drops from 0.986 to 0.267, whereas DeepSSIM retains 0.485 and DeepSSIM-Lite retains 0.671. Under moderate and severe distortion, however, both deep metrics collapse alongside pixel SSIM (to 0.205 and 0.087 for DeepSSIM), and across the full test set classical pixel SSIM actually separates right predictions from wrong ones slightly better than DeepSSIM (AUROC 0.710 versus 0.664). Two factors explain this result. First, kerning jitter shifts characters horizontally by whole stroke widths, which exceeds the spatial pooling tolerance of early VGG layers while deeper VGG layers blur away the fine serif and terminal differences that distinguish one font from another. Second, the attention-calibration step in Zhang et al. (2024) leaves several implementation choices unspecified in its published equations, so our uncalibrated VGG implementation does not realign displaced glyphs before comparing them. Consequently, re-render similarity is kept strictly as an offline diagnostic rather than a runtime re-ranker, as designed in Section 4.4.2.

## 5.5 Backbone Comparison, Runtime Latency, and Real-Generative Evaluation

### 5.5.1 Backbone Comparison and Inference Latency

To verify that DINOv2 earns its place in the pipeline on measured evidence rather than assumption (Section 4.10.2), the complete training and open-set recipe (120 epochs, $P = 16 \times K = 8$, batch-all triplet loss with 128 background crops at margin $\alpha = 0.4$, and LoRA teacher distillation at $\lambda_{\text{KD}} = 0.5$) was re-run across the four candidate backbones of Table 5: DINOv2 ViT-B/14 (`facebook/dinov2-base`), Supervised ViT-B/16 (`google/vit-base-patch16-224`), ConvNeXt-T (`facebook/convnext-tiny-224`), and the vision tower of SigLIP ViT-B/16 (`google/siglip-base-patch16-224`). To isolate the backbone itself, all four models in the controlled comparison read only their final layer's summary (class plus mean patch token for the three Vision Transformers; global pooled map for ConvNeXt-T). Because the revised cut-search homogeneity check embeds sub-crops through the full model rather than reading patch columns, ConvNeXt-T was able to participate as a full candidate. Table 15 reports test-split accuracy, open-set rejection, parameter count, and single-crop inference latency on the deployment laptop alongside the deployed multi-layer DINOv2 model.

**Table 15**

*Backbone Comparison on the Synthetic Test Partition and Single-Crop Latency on the Deployment Laptop*

| Encoder backbone | Val Top-1 (%) | Test Top-1 (%) | Test Top-3 (%) | Test family (%) | Test FPR@95 (%) | Test AUROC | Params (M) | GPU latency (ms/crop) | CPU latency (ms/crop) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| *Single-layer readout (controlled comparison)* | | | | | | | | | |
| DINOv2 ViT-B/14 (block 12) | 42.5 | 41.0 | 65.1 | 87.3 | 80.3 | 0.661 | 86.6 | 28.7 | 300 |
| ConvNeXt-T (final stage) | 34.2 | 33.8 | 55.3 | 84.1 | 88.8 | 0.620 | 27.8 | 13.8 | 98 |
| Supervised ViT-B/16 (block 12) | 33.2 | 32.7 | 54.4 | 83.3 | 86.3 | 0.627 | 86.4 | 18.7 | 238 |
| SigLIP ViT-B/16 (vision tower, block 12) | 27.2 | 26.0 | 46.6 | 81.0 | 91.7 | 0.605 | 92.9 | 19.5 | 269 |
| *Multi-layer readout (deployed model)* | | | | | | | | | |
| DINOv2 ViT-B/14 (blocks 3, 6, 9, 12) | 50.2 | 50.2 | 72.2 | 89.7 | 75.6 | 0.687 | 86.6 | 26.3 | 332 |

*Note.* All runs were trained and evaluated on the deployment laptop (`torch 2.6.0+cu124`, NVIDIA RTX 3050 Laptop GPU, 14-thread Intel CPU). Latency is the median single-crop forward-pass time over 50 crops on GPU and 20 crops on CPU (batch size 1) after warm-up.

Three findings emerge from Table 15. First, DINOv2 leads every candidate on every accuracy and open-set rejection metric, even before multi-layer readout is turned on. Comparing single-layer DINOv2 against Supervised ViT-B/16 isolates the pretraining objective on the same 86-million-parameter Vision Transformer class: self-supervised discriminative pretraining outperforms ImageNet-21k category supervision by 8.3 percentage points of test Top-1 accuracy (41.0% versus 32.7%) and reduces unknown-font false alarms by 6.0 percentage points (80.3% versus 86.3% FPR@95). Reading intermediate blocks widens DINOv2's lead to 16.4 percentage points over the next best backbone (ConvNeXt-T at 33.8%).

Second, SigLIP finishes last across the board (26.0% Top-1, 91.7% FPR@95). Image-text contrastive pretraining aligns patches with caption semantics, which encourages the vision tower to care about what word or object is present rather than the fine geometry of how its strokes are drawn. This matches the semantic interference that Li, Song, et al. (2025) found in vision-language models.

Third, the latency measurements expose a concrete deployment trade-off against the responsiveness target of the Software Requirements Specification (Appendix A, `REQ-5.1-1`: an image with up to five text regions shall complete within roughly 10 seconds on the presenter's laptop). A single embedding of the deployed multi-layer DINOv2 model takes 26.3 ms on the laptop GPU and 332 ms on the laptop CPU. However, the cut-search homogeneity check of Section 5.3.3 embeds two sub-crops at each of seven cut positions, adding 14 encoder passes per crop (for a total of 15 passes when all seven cuts are allowed). On the laptop GPU, 15 passes cost roughly 0.40 seconds per crop, or 2.0 seconds for a five-region image, comfortably inside the 10-second interactive budget even after EasyOCR localization is added. On CPU alone, 15 passes cost roughly 5.0 seconds per crop, or 25.0 seconds for five regions, exceeding the CPU target before localization runs (and even if the 14 cut passes are batched into a single tensor call, CPU compute scales nearly linearly with token volume). Consequently, interactive demonstration in Increment 4 either uses the laptop GPU (where the full 7-cut search runs in 2 seconds) or, when running on a CPU-only host, gates the full cut search behind a single midpoint probe so that unflagged single-font words require three passes instead of fifteen.

### 5.5.2 Real-Generative Evaluation and Human-Proxy Panel Consensus

While the synthetic test partition provides controlled, bit-reproducible measurement across 80 fonts and four distortion tiers, the out-of-distribution test of the thesis is the real-generative benchmark of Section 4.3.1: `[N = 100]` word crops localized by EasyOCR from images generated by DALL-E 3 (Bing Image Creator), Google Gemini, and OpenAI GPT Image across a purposive quota of font families and hallucination severities. Ground truth on this set is fixed by three practicing typography and design raters using the blind web-based rating instrument of Section 4.2.3 (Appendix B), scored by `src/model/real.py`. Table 16 sets out the evaluation record to be populated once all three raters submit their response sets.

**Table 16**

*Real-Generative Evaluation Set Performance Against the Three-Rater Expert Panel Consensus*

| Evaluation measure | Measured value |
| :--- | :---: |
| Total localized real-generative crops rated by all 3 panelists ($N$) | `[N = 100]` |
| Inter-rater agreement on palette font / unknown label (Fleiss' $\kappa$) | `[κ = X.XX]` |
| Inter-rater agreement on single-versus-mixed typeface coherence (Fleiss' $\kappa$) | `[κ = X.XX]` |
| Crops reaching 2-of-3 panel consensus on a known palette font ($n_{\text{known}}$) | `[n = XX]` |
| Crops reaching 2-of-3 panel consensus on the "unknown / hallucinated" verdict ($n_{\text{unknown}}$) | `[n = XX]` |
| Proposed recognizer Top-1 / Top-3 accuracy on consensus-known crops | `[XX.X% / XX.X%]` |
| Proposed recognizer Top-1 accuracy on accepted consensus-known crops | `[XX.X%]` |
| Storia-AI Top-1 accuracy on consensus-known crops | `[XX.X%]` |
| Chen et al. (2026) Top-1 accuracy on consensus-known crops | `[XX.X%]` |
| Proposed recognizer rejection rate (true unknown recall) on consensus-unknown crops | `[XX.X%]` |
| Panel prevalence of multi-typeface crops (2-of-3 consensus "more than one") | `[XX.X%]` |
| Agreement between the cut-search homogeneity flag and panel coherence consensus | `[XX.X%]` |

*Note.* Bracketed placeholders mark empirically unmeasured values awaiting completion of the asynchronous three-rater labeling exercise (`data/real/labels.csv` $\rightarrow$ `reports/real/real_eval.json`), in accordance with the study's data-integrity rules.
