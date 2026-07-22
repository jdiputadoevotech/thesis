## 4.3 Research Procedure

This section specifies how the data are gathered and treated. Section 4.3.1 defines the dataset schema, the variables, and the properties of the image and text data. Section 4.3.2 describes the preprocessing, augmentation, and adaptation applied before training, and closes with the validation strategy that guards against overfitting.

### 4.3.1 Gathering of Data

**Data schema.** The corpus is a table of image instances, one row per rendered crop, with the fields listed in Table 1. Each row pairs an image file with the metadata needed to train, stratify, and audit it.

**Table 1**

*Schema of the Synthetic Text-Crop Dataset*

| Field | Type | Description |
|-------|------|-------------|
| `image_id` | string | Unique identifier for the crop |
| `image_path` | string | Path to the rendered PNG |
| `font_id` | categorical | Google Fonts family and weight (the class label) |
| `family_class` | categorical | Serif, Sans-serif, Display, or Monospace |
| `word_text` | string | The rendered English word(s) |
| `warp_level` | float | Elastic-warp intensity $\theta_{\text{warp}}$ |
| `blur_level` | float | Gaussian blur/noise intensity $\theta_{\text{blur}}$ |
| `kern_level` | float | Kerning-jitter intensity $\theta_{\text{kern}}$ |
| `split` | categorical | train, validation, or test |
| `seed` | integer | Random seed for exact regeneration |

*Note.* The three degradation-level fields record the parameters of the operator $D$ from Section 3.2.3, so each crop's deformation is reproducible and can be analyzed after the fact.

**Variables.** The independent variables (inputs) are the pixels of the rendered text-crop image and, at a controlled level above them, the three degradation parameters ($\theta_{\text{warp}}$, $\theta_{\text{blur}}$, $\theta_{\text{kern}}$) that the pipeline manipulates systematically, together with the categorical `family_class` factor used to analyze errors. The dependent variable (target) is the font class label, one of the 50 to 100 palette fonts, plus the open-set "unknown" outcome for crops belonging to no palette font. Secondary outcomes measured from the model are the Top-K rank of the true font, the structural-distance score between the input and the re-rendered prediction, and the open-set rejection score.

**Image properties.** Crops are rendered at 1024 px and downsampled to a fixed 224 × 224 input, which matches the DINOv2 ViT-B/14 backbone and the resolution used by Chen et al. (2026). To keep the model from learning a color shortcut, and to mirror the varied coloring of real generative text, foreground and background colors are randomized during rendering with a minimum luminance contrast of 80 (the Chen et al. precedent). Each crop is then reduced to single-channel luminance and replicated across three channels for ImageNet-normalized input, so the encoder reads grayscale structure while training on color-varied renders. Text alignment is jittered (left, center, or right) and lines wrap with roughly 20% probability, and about 575 images are rendered per font variant as the per-class volume baseline.

**Text properties.** The rendered strings are English (Latin script), drawn from a fixed word list of common words so that lexical content is decorrelated from font identity across the corpus. Each crop carries one to three words, so the visual field is dominated by letterform structure rather than long-line layout.

**Extension beyond the precedent.** Chen et al.'s (2026) augmentation is pristine-noise only (Gaussian $\sigma = 25.5$). This study's data contribution is to add the hallucination-specific degradation operator $D$, covering elastic warp, kerning jitter, and cross-character smear, that their closed-set pipeline lacks. As a result the corpus covers the probabilistic glyph deformation that defines the target regime, which clean renders under noise never reach.

**The real-generative evaluation set.** A second, smaller body of data is *collected rather than rendered*, to test the trained model on genuine in-the-wild deformation instead of the study's own synthetic operator. It consists of [N = 100] text crops isolated from real images produced by current text-to-image generators such as DALL·E, Midjourney, and Stable Diffusion, the tools whose typographic hallucination motivates the study. Each source image is passed through the same off-the-shelf localizer used at deployment (Section 4.1), and every text box it emits becomes one evaluation crop, so the unit of analysis is identical to the synthetic corpus. Because these crops carry no embedded font metadata, their ground-truth labels are fixed by the human-proxy panel (Section 4.2.3), and the set is held out from training entirely (Section 4.3.2).

**Selecting the crops.** The [N = 100] crops are sampled *purposively rather than at random*, under a quota that spans the two factors that drive recognition difficulty: the four structural family classes (serif, sans-serif, display, monospace) and a graded range of hallucination severity from mild to severe, gathered across more than one generator so the benchmark is not dominated by a single tool's failure signature. This mirrors the family-and-degradation stratification of the synthetic split (Section 4.3.2) and ensures the human-proxy accuracy floor is estimated over the full difficulty range, not only easy cases.

**Why one hundred.** The set is deliberately small because every crop must be labeled independently by all three expert raters, roughly 300 judgments in total, so its size is bounded by expert effort rather than by data availability. One hundred is adequate for its role as a benchmark and accuracy floor rather than a training set: at $n = 100$ a measured accuracy carries a worst-case 95% confidence half-width of about $\pm 10$ percentage points, and the comparison it supports (the open-set model against closed-set baselines that collapse on deformed input, Section 4.10) targets gaps far larger than that margin, while finer-grained effects are left to the much larger synthetic test partition. The count is a planned target and may be revised upward if rater capacity allows.

### 4.3.2 Treatment of Data

Before training, each crop passes through a preprocessing chain embedded in the model's forward pass (square-pad, resize to 224 × 224, and ImageNet normalization) rather than applied as a separate offline step. Folding preprocessing into the forward method, following Chen et al. (2026), guarantees that the same transforms run at training and at inference, which eliminates train-serve skew when the model is later called from the web application. Degradation via the operator $D$ is applied online as a stochastic augmentation, so a given font is seen across a distribution of deformation amplitudes within and across epochs. Following the augmentation-as-coverage argument of Plastropoulos and Tegos (2024), this pushes the decision boundary into regions that stay stable under distortion.

**Adaptation strategy.** The default configuration keeps the DINOv2 backbone frozen and trains only a lightweight metric-embedding head (Section 2.5), because in-the-wild generative crops arrive without font labels and the open-set inference path must not depend on a closed-set classifier. Parameter-efficient fine-tuning (LoRA; $r = 8$, $\alpha = 16$, about 0.2% of parameters) as used by Chen et al. (2026) is reserved for the supervised teacher that supplies reference distributions to the label-free prompt-distillation step. It is kept off the open-set inference path, whose closed-set assumptions it would otherwise reintroduce.

**Validation strategy.** The synthetic corpus is partitioned 70% / 15% / 15% into training, validation, and test sets, split by `font_id` and stratified so that every font class and every degradation level appears in each partition in proportion to its overall frequency. Stratification prevents a rare display or monospace face from landing entirely in one partition, which would otherwise inflate or deflate its apparent accuracy. Because per-class counts for the rarest faces are modest, stratified k-fold cross-validation ($k = 5$) is used on the combined train-plus-validation data to stabilize the reported metrics, with the 15% test partition held out untouched until final evaluation. Separate from this synthetic split is the real-generative test set of [N = 100] in-the-wild crops (sourced, sampled, and sized in Section 4.3.1; labeled by the human-proxy panel, Section 4.2.3). It never enters training in any form, and it functions as the out-of-distribution generalization benchmark against which the synthetic-trained model is finally judged.
