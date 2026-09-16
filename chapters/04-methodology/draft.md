# Chapter 4: Methodology

## 4.1 Research Environment and Respondents

This study is conducted entirely in a computational environment. It does not survey a human population. Instead, it studies typographic artifacts: the units of analysis are *fonts* and the *rendered text-crop images* derived from them. The study addresses typographic hallucination in generative AI images, and no clean, labeled corpus of such hallucinated text exists at the scale a metric-learning model needs. The researchers therefore generate the primary dataset themselves, from a curated open-source font palette, instead of downloading one ready-made. This follows the precedent of DeepFont, which also built a targeted synthetic dataset of rendered glyphs to train a deep visual font recognizer (Wang et al., 2015).

### Digital Source and Trusted Environment

The font palette comes from Google Fonts (https://fonts.google.com; source repository https://github.com/google/fonts), the open-source typeface library maintained by Google LLC. Google Fonts is a trusted environment for three reasons. First, its typefaces are released under permissive open licenses, predominantly the SIL Open Font License. Every typeface can therefore be freely rendered, degraded, and redistributed, without the licensing restrictions that commercial font catalogues carry. Second, the collection is curated and version-controlled. Each typeface has a stable identity and a traceable history, which a reproducible dataset requires. Third, these typefaces are among the most widely used on the web. A model trained on them therefore maps hallucinated text back onto a palette that designers can actually reuse for free. From this library the study selects the top 50 to 100 fonts, following the platform's own popularity ranking and chosen to span the four structural family classes established in Section 3.2.1: serif, sans-serif, display, and monospace.

The palette is deliberately small, and the decision rests on both the design of the framework and the published evidence on large catalogues. On the design side: the system performs open-set recognition, in which the set of known fonts is intentionally finite and every input outside that set is routed to an "unknown" verdict. The space of possible fonts is effectively unbounded and cannot be enumerated (Lu et al., 2025). A small, well-chosen known set is therefore the premise of the design, not a limitation of it. On the evidence side: enlarging a font catalogue buys coverage, but not robustness. The Storia-AI classifier covers 3,474 fonts, the largest reference embedding in the field, yet it still overfits to pristine glyphs and breaks down under generative deformation (Jiang et al., 2025). Chen et al. (2026) observed the same pattern at a smaller scale: expanding their model to 394 font variants dropped family-level accuracy to 40.2%, because most of the added fonts were near-identical weight variants that the model constantly confused with one another. A curated palette that leaves out such near-duplicates avoids this failure directly. Trimming the palette also excludes the typographic long tail of rare and ornamental faces. Those faces are the hardest to recognize and the ones diffusion models hallucinate most severely (Zhuang et al., 2025). A smaller palette additionally keeps the number of training images per font high, because a fixed rendering budget spread over fewer classes yields more examples of each. Finally, the study's reconstruction goal only requires the fonts designers actually reuse, and the popularity ranking surfaces exactly those.

A second, external repository defines the study's comparative baseline: Storia-AI's Google Font Classifier (the `font-classify/` sandbox), a pre-trained classifier over 3,474 Google Fonts. It was chosen because it is the field's reference embedding for font identity, adopted as the fidelity backbone in recent typographic work (Jiang et al., 2025). Benchmarking against it lets the study show, on a recognized standard, how weights fitted to pristine glyphs degrade when the input is deformed by generative AI.

### Respondents: The Entities Being Studied

Because the data concern non-human objects, there are no human respondents in the primary sense. The entities being studied are of two linked kinds:

1. **Fonts (typefaces).** The 50 to 100 selected Google Fonts are the population of typographic identities the system must recognize. Each font is one class label in the recognition problem. Each is characterized by the measurable structural traits defined in Chapter 3: x-height, terminal form, stroke contrast, and counter shape.

2. **Rendered text-crop images.** From each font, the pipeline renders clean word crops and then applies the degradation operator of Section 3.2.3 to produce hallucinated variants. These grayscale image crops, standardized to a fixed input resolution (Section 4.3.1), are the individual "profiles" the model actually consumes. Each degraded crop is one instance, and its ground-truth label is the font it was rendered from.

The **unit of analysis is the isolated text crop**, not the full image. A real deployment receives a whole generative-AI image, which may contain several pieces of text in different fonts. An upstream step must therefore locate and cut out each piece before recognition can begin. That localization is handled by a standard off-the-shelf text detector, and it is treated as a boundary of the study rather than a contribution: this study does not train, tune, or evaluate the localizer, and it reports no detection metrics. Every crop the localizer emits is classified independently by the recognition engine, and that engine is where the thesis's contribution lies. Fixing the crop as the unit of analysis keeps the dataset, the metrics of Section 4.2, and the human-proxy baseline all defined at the same level.

A small human element enters only at the evaluation stage, and strictly as a benchmark rather than a study population. A three-person consensus panel establishes a human-proxy ground truth over a held-out set of 100 real generative-AI text boxes. This panel provides the accuracy floor against which the automated system is compared (Section 4.10); its composition and screening criteria are specified there. The raters are practicing typography and design professionals, and gathering them for a supervised, face-to-face labeling session would be impractical. The panel therefore works in a **remote, asynchronous online environment**: each rater completes the rating exercise independently through a web-based form, at their own pace, with no shared session and no contact between raters. This distributed setup protects rater independence by construction, because no rater can see another's judgments before submitting. It also keeps the environment reproducible, because every rater receives the identical instrument over the identical set of crops. The administration of the form is detailed in Section 4.2.3. Apart from this panel, the study's respondents are entirely typographic artifacts.

## 4.2 Research Instrument or Sources of Data

This study works on typographic artifacts rather than human respondents, so its "instruments" are not questionnaires or surveys. They are the software apparatus that manufactures, measures, and adjudicates the data. Four instruments are used:

1. **Synthetic-data generation pipeline** (researcher-made): produces the training and validation corpus (Section 4.2.1).
2. **Standardized evaluation metrics**: score the model's output against published protocols (Section 4.2.2).
3. **Human-proxy consensus rubric** (researcher-made): the rating instrument through which a three-person expert panel fixes ground truth on real generative crops (Section 4.2.3).
4. **Web application**: exercises the trained model interactively, in real time (Section 4.2.4).

The first three supply and assess data; the fourth is the interactive artifact through which the system is demonstrated and stress-tested.

### 4.2.1 Synthetic-Data Generation Pipeline (Researcher-Made)

The primary instrument is a rendering-and-degradation pipeline built by the researchers. Its purpose is to generate a large, fully labeled corpus of text-crop images, a corpus with no in-the-wild equivalent at the scale metric learning requires. It follows the synthetic-corpus precedent of DeepFont (Wang et al., 2015) and the more recent DINOv2-based font pipeline of Chen et al. (2026). The pipeline has two stages. The rendering stage draws clean word crops from the selected Google Fonts palette. The degradation stage applies the operator $D$ defined in Section 3.2.3 (elastic warp, Gaussian blur and noise, and kerning jitter) to turn each clean crop into a hallucinated look-alike.

The pipeline is valid to the extent that its manufactured deformations resemble the deformations found in real text-to-image output. This is its **construct validity**, and it rests on the correspondence between the degradation parameters and the failure mechanisms the generative literature documents: cross-character attention smearing (Gillani et al., 2025), multi-instance entanglement (Du et al., 2025), and continuous latent-manifold mutation (Kondo et al., 2024). Its **reliability** is procedural. Rendering and degradation are deterministic once the random seed is fixed, so any crop in the dataset can be regenerated bit-for-bit, and the degradation intensity of every image is logged alongside it. The pipeline is researcher-made rather than a standardized dataset, but its determinism means any third party who runs the same code with the same seed obtains the same data.

### 4.2.2 Standardized Evaluation Metrics

The model is scored with four metrics, all taken from the published literature rather than invented for this study, so their validity is already established. The first measures recognition accuracy: how often the true font appears in the model's top one and top three guesses, the **Top-1 and Top-3 (Top-K) protocol** that DeepFont made the field standard (Wang et al., 2015). The second measures visual closeness. The predicted font is re-rendered with the same text, and the re-rendering is compared against the input crop using **structural similarity**: the classical SSIM of Wang et al. (2004), plus its modern successors DeepSSIM (Zhang et al., 2024) and SAMScore (Li, Chen, et al., 2025), which stay reliable when the two images are warped out of alignment. That is exactly the condition hallucinated text creates. The third quantifies confidence: **rank-calibrated conformal prediction** (Shi et al., 2024; Ding et al., 2025) turns the shortlist into a prediction set with a formal statistical guarantee of containing the true font. The fourth weighs how bad each error is. The **embedding-centroid cosine severity index** of Chen et al. (2026) measures how far, in style terms, a wrong answer lands from the right one, so that a near-miss within the same typographic family is distinguished from a cross-family blunder. Because all four instruments come from peer-reviewed sources, their validity and reliability are inherited from the literature rather than re-established here.

### 4.2.3 Human-Proxy Consensus Rubric (Researcher-Made)

Real generative crops carry no font metadata, so something must fix their ground truth. That something is a researcher-made rating instrument, administered to a three-person expert panel.

**How the instrument is delivered.** The rating exercise runs asynchronously as a web-based form rather than in a supervised session (the remote environment justified in Section 4.1). Each crop is shown individually, beside a reference sheet of the entire palette rendered as labeled specimens. Raters therefore match each crop against a fixed, visible option set instead of recalling fonts from memory. Each rater works at their own pace, blind to the other raters and blind to the model's predictions, which guards against anchoring. The form's two screens (an instructions page and the per-crop rating item) are reproduced in the appendices. The layout is deliberately platform-neutral, so any standard web-form service can deliver it without altering the instrument.

**What each rater judges.** For each of the [N = 100] real generative-AI text boxes, the rater makes two required judgments. The first is the font label: the closest palette font, or an "unknown / hallucinated" verdict when no palette font matches. A label becomes ground truth only when at least two of the three raters agree. The second is a coherence judgment: does the crop appear to be set in one typeface throughout, or in more than one? A "cannot tell" option is available, and the same blind protocol and two-of-three consensus rule apply. This second question serves a specific purpose. It turns the single-typeface assumption of Section 4.4.2 from a premise into a measured quantity, the actual prevalence of font-incoherent text in real generative output, and its consensus answers double as the ground truth against which the pipeline's homogeneity check is validated (Section 4.10.2).

**Validity and reliability.** The instrument's **content validity** comes from the panel's expertise: raters are screened for typographic training, under criteria specified in Section 4.10. Its **reliability** is quantified by inter-rater agreement, reported as a Fleiss' $\kappa$ of [κ = X.XX] once the rating exercise has run. The two-of-three consensus rule is the instrument's built-in safeguard against any single rater's idiosyncrasy.

### 4.2.4 Web Application (Interactive Testing Instrument)

The fourth instrument is a web application built on top of the trained model, so that the system can be exercised in real time rather than only in batch evaluation. A user uploads a generative-AI image through the browser, the backend runs the inference engine, and the interface returns the Top-K Google Fonts shortlist or an "unknown" verdict. The application accepts raster images in PNG (.png), JPEG (.jpg, .jpeg), or WebP (.webp) format, up to 10 MB. These are the formats current text-to-image generators export, and the forms in which their output circulates as screenshots and web re-shares. Vector formats such as SVG are refused, because typographic hallucination is a raster artifact with no vector equivalent. Animated and photographic formats (GIF, HEIC) fall outside the study's scope of directly generated still images. The instrument serves two methodological purposes. It is the demonstration artifact that the build-method evaluation of Section 4.10 requires. It is also a qualitative probe: it surfaces failure cases on ad hoc, in-the-wild inputs that the fixed test set may not contain. Its design, framework choices, and development process are detailed in Sections 4.5 through 4.8.

## 4.3 Research Procedure

This section specifies how the data are gathered and treated. Section 4.3.1 defines the dataset schema, the variables, and the properties of the image and text data. Section 4.3.2 describes the preprocessing, augmentation, and adaptation applied before training, and closes with the validation strategy that guards against overfitting.

### 4.3.1 Gathering of Data

**Data schema.** The corpus is a table of image instances, one row per rendered crop, with the fields listed in Table 1. Each row pairs an image file with the metadata needed to train on it, stratify it, and audit it afterward.

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

**Variables.** The independent variables are the pixels of the rendered crop and, at a controlled level above them, the three degradation parameters ($\theta_{\text{warp}}$, $\theta_{\text{blur}}$, $\theta_{\text{kern}}$) that the pipeline manipulates systematically, together with the categorical `family_class` factor used to analyze errors. The dependent variable is the font class label: one of the 50 to 100 palette fonts, plus the open-set "unknown" outcome for crops that belong to no palette font. Three secondary outcomes are measured from the model: the Top-K rank of the true font, the structural-distance score between the input and the re-rendered prediction, and the open-set rejection score.

**Image properties.** Crops are rendered at 1024 px and downsampled to a fixed 224 × 224 input. This matches the DINOv2 ViT-B/14 backbone and the resolution used by Chen et al. (2026). Foreground and background colors are randomized during rendering, with a minimum luminance contrast of 80 (the Chen et al. precedent). The randomization serves two purposes: it prevents the model from learning color as a shortcut, and it mirrors the varied coloring of real generative text. Each crop is then reduced to single-channel luminance and replicated across three channels for ImageNet-normalized input. The encoder therefore reads grayscale structure, even though the renders it trains on vary in color. Text alignment is jittered between left, center, and right; lines wrap with roughly 20% probability; and about 575 images are rendered per font variant as the per-class volume baseline.

**Text properties.** The rendered strings are English (Latin script), drawn from a fixed list of common words. Using a fixed shared word list means the words themselves carry no information about the font, so the model cannot learn to associate vocabulary with typeface. Each crop carries one to three words, which keeps the visual field dominated by letterform structure rather than long-line layout.

**Extension beyond the precedent.** Chen et al.'s (2026) augmentation is pristine-noise only: clean renders plus Gaussian noise ($\sigma = 25.5$). This study's data contribution is to add the hallucination-specific degradation operator $D$ (elastic warp, kerning jitter, and cross-character smear) that their closed-set pipeline lacks. The corpus therefore covers the probabilistic glyph deformation that defines the target regime, which clean renders under noise never reach.

**The real-generative evaluation set.** A second, smaller body of data is *collected rather than rendered*. Its purpose is to test the trained model on genuine in-the-wild deformation, not on the study's own synthetic operator. It consists of [N = 100] text crops isolated from real images produced by current text-to-image generators such as DALL·E, Midjourney, and Stable Diffusion, the tools whose typographic hallucination motivates the study. Each source image passes through the same off-the-shelf localizer used at deployment (Section 4.1), and every text box the localizer emits becomes one evaluation crop. The unit of analysis is therefore identical to the synthetic corpus. These crops carry no embedded font metadata, so their ground-truth labels are fixed by the human-proxy panel (Section 4.2.3). The set is held out from training entirely (Section 4.3.2).

**Selecting the crops.** The [N = 100] crops are sampled *purposively rather than at random*. A quota spans the two factors that drive recognition difficulty: the four structural family classes (serif, sans-serif, display, monospace) and a graded range of hallucination severity from mild to severe. The crops are gathered from more than one generator, so the benchmark is not dominated by a single tool's failure signature. This mirrors the family-and-degradation stratification of the synthetic split (Section 4.3.2), and it ensures the human-proxy accuracy floor is estimated over the full difficulty range rather than only the easy cases.

**Why the set is limited to one hundred crops.** The choice of one hundred balances statistical adequacy against expert labeling effort. The set is deliberately small, because every crop must be labeled independently by all three expert raters (roughly 300 judgments in total). Its size is bounded by expert effort, not by data availability. One hundred is adequate for the set's actual role, which is benchmark and accuracy floor rather than training data. At $n = 100$, a measured accuracy carries a worst-case 95% confidence half-width of about $\pm 10$ percentage points. The comparison this set supports, the open-set model against closed-set baselines that collapse on deformed input (Section 4.10), targets gaps far larger than that margin. Finer-grained effects are left to the much larger synthetic test partition. The count is a planned target and may be revised upward if rater capacity allows.

### 4.3.2 Treatment of Data

Before training, each crop passes through a preprocessing chain: square-pad, resize to 224 × 224, and ImageNet normalization. This chain is embedded in the model's forward pass instead of being applied as a separate offline step. Folding preprocessing into the forward method, following Chen et al. (2026), guarantees that exactly the same transforms run at training time and at inference time. That eliminates train-serve skew (the class of bug in which a model is trained on inputs prepared one way and served inputs prepared another) when the model is later called from the web application. Degradation via the operator $D$ is applied online, as a stochastic augmentation, so the model sees each font across a whole distribution of deformation strengths within and across epochs. Following the augmentation-as-coverage argument of Plastropoulos and Tegos (2024), this pushes the model's decision boundaries into regions that stay stable under distortion.

**Adaptation strategy.** The default configuration keeps the DINOv2 backbone frozen and trains only a lightweight metric-embedding head (Section 2.5). The reason is the deployment condition: in-the-wild generative crops arrive without font labels, so the open-set inference path must not depend on a closed-set classifier. Parameter-efficient fine-tuning (LoRA with rank $r = 8$, scaling $\alpha = 16$, about 0.2% of parameters, as used by Chen et al., 2026) is reserved for the supervised teacher model. The teacher supplies reference distributions to the label-free distillation step and nothing more. Keeping it off the inference path matters, because the teacher is a closed-set model, and placing it in the serving pipeline would reintroduce exactly the closed-set assumptions the design exists to avoid.

**Validation strategy.** The synthetic corpus is partitioned 70% / 15% / 15% into training, validation, and test sets. The split is made by `font_id` and stratified, so that every font class and every degradation level appears in each partition in proportion to its overall frequency. Stratification prevents a rare display or monospace face from landing entirely in one partition, which would otherwise inflate or deflate its apparent accuracy. Per-class counts for the rarest faces are modest, so stratified k-fold cross-validation ($k = 5$) is used on the combined train-plus-validation data to stabilize the reported metrics. The 15% test partition stays untouched until final evaluation. Separate from this synthetic split is the real-generative test set of [N = 100] in-the-wild crops (sourced, sampled, and sized in Section 4.3.1; labeled by the human-proxy panel, Section 4.2.3). It never enters training in any form. It serves as the out-of-distribution benchmark: the final judge of whether a model trained on synthetic deformation generalizes to the real thing.

## 4.4 Concept

### 4.4.1 Core Concept and Vision

The system is a font-identification service for hallucinated type. Given a fragment of text lifted from a generative-AI image, it returns a ranked shortlist of the closest open-source Google Fonts, or an explicit "unknown" verdict when the glyph belongs to no font in its palette. Its purpose is practical reconstruction. A designer should be able to rebuild a generative image's typography from a free, license-clear palette, instead of paying a commercial identifier to name a font that may not even be reusable. The framework is deliberately scoped: rather than matching against the entire commercial typeface universe, it trades exhaustive coverage for a tractable, localized palette of the top 50 to 100 Google Fonts. That trade is what makes free reconstruction possible. A web application built on top of the model exposes this capability interactively, so the system can be tested in real time on uploaded images.

### 4.4.2 Conceptual Framework

Figure 8 organizes the framework into three enclosed bands. The bands are ordered by *when* each one happens, rather than by an input-process-output grid.

The first band, *before deployment*, is the work the researchers perform once. The Google Fonts palette is rendered into clean word crops whose font is known by construction. Those crops pass through the degradation operator $D$ of Section 3.2.3, which produces hallucinated look-alikes. The resulting corpus, the clean renders together with their degraded variants, trains two models. The first is a teacher: DINOv2 with the LoRA adaptation of Section 4.3.2, fitted to the font labels. The second is the student metric head $f_\theta$, which learns from two signals at once: the font labels, through the triplet objective of Chapter 3, and the teacher's judgments, through distillation. The band closes on the trained model, meaning the learned weights $f_\theta$ together with the calibrated match threshold $\tau$. Only the student ships. The teacher exists to supervise the student and is never executed on a user's image, which is why it is drawn in the offline band and appears nowhere in the band below.

The second band, *at use*, is what runs for every uploaded image. The input is a raster image produced by a text-to-image generator such as DALL·E, Midjourney, or Stable Diffusion, containing rendered text whose glyphs are warped and whose spacing is uneven. An off-the-shelf text detector locates each piece of text and cuts it out. The detector is a standard component, not a contribution of this work, and the unit of analysis is the isolated crop, as stated in Section 4.1. How many text regions an image contains is a question the localizer answers; from that point on, every crop is handled independently. Each crop then passes through a fixed preparation sequence before the model reads it:

1. **Square-pad.** The rectangular crop is padded to a square, so the next step cannot stretch or squash the glyphs.
2. **Resize to 224 × 224 pixels.** This is the fixed input size the encoder expects.
3. **Convert to grayscale.** The crop is reduced to luminance, so letterform structure rather than color drives recognition; the single channel is replicated across three channels to match the encoder's input format.
4. **Normalize brightness.** Pixel values are rescaled to the ImageNet statistics the encoder was pretrained on.

This sequence runs inside the model's forward pass, for the train-serve reasons given in Section 4.3.2. The prepared crop is then encoded by the frozen DINOv2 Vision Transformer and projected by the metric head into a font-style fingerprint. The final stage is a match test: the fingerprint is compared against the palette, and the outcome depends on whether the closest font falls within the threshold $\tau$.

Three properties of the match test are worth stating plainly. First, the threshold is not chosen by hand. It is fixed during offline calibration, at the operating point of Section 4.10.2: the cutoff at which 95% of validation crops whose font truly is in the palette are accepted. Second, the test considers only the best match. A crop whose closest font clears $\tau$ is accepted, and its Top-K shortlist then lists the nearest palette fonts in order, regardless of whether the lower ranks clear $\tau$ individually, because those ranks serve as next-closest alternatives, not as independent match claims. Third, rejection is total. A crop whose closest font falls short of $\tau$ receives an explicit "unknown font" verdict, in which the system names no font at all. No partial shortlist exists for such a crop, because every other font is farther away still.

**Word-level granularity and mixed typography.** The text regions of Figure 8 are delimited at word granularity: the localizer emits one bounding box per word. Behind this sits an assumption, that each word is set in a single typeface. The assumption holds for the overwhelming majority of designed text, where font changes fall *between* words (a heading face against an accent face), not inside them. Word crops therefore make the one-font-per-crop premise of the match test approximately true by construction. The assumption operates at the level of design intent. Generators learn from designed text, so the *intended* style of a word is single; style that drifts within a word is the hallucination this thesis studies, degradation around one intent rather than a deliberate second typeface. How often real output violates even this intent-level reading is measured rather than presumed, through the panel's coherence judgment (Section 4.2.3). In the interface, adjacent words that receive the same verdict are merged back into a single region, so a five-word headline still reads as one result.

The assumption is checked rather than trusted. The ViT encoder's forward pass already produces one token per image patch. When a crop's patch tokens disagree about style, the signature of two typefaces sharing one box or of a localizer box that swallowed two words, the crop is flagged as inhomogeneous at no additional inference cost. A flagged crop is split at the boundary between the two token groups, and each half is matched on its own. A half that remains incoherent after one split receives a third verdict: **"mixed typography."** This verdict is distinct from "unknown." It reports that the crop violates the single-font premise and that no one font can honestly be assigned, instead of confidently naming the majority typeface and silently discarding the other. Attribution finer than one split, such as per-glyph styling inside an unsplittable word, is out of scope. It would require character segmentation on precisely the malformed glyphs that defeat segmenters, and a word deliberately set in two typefaces has no single reconstructable font for the template goal in any case.

**How a flagged crop is split.** The check and the split both read the encoder's patch grid. A 224 × 224 input reaches the ViT as a 16 × 16 grid of patches, one token each. Patches that carry no ink (padding margins, gaps between letters) are excluded by their attention weight. The remaining tokens are pooled by grid column, which yields a left-to-right style profile of the word. Homogeneity is then a question of how tightly those column vectors group. When a two-group clustering separates them more widely than a dispersion cutoff, the crop is flagged; the cutoff is calibrated, like $\tau$, at an operating point on labeled data (Section 4.10.2). The split itself demands spatial contiguity. A real boundary exists only when the two groups occupy a contiguous left run and a contiguous right run of columns. In that case the boundary column is mapped back to a pixel coordinate in the original crop, undoing the padding offset, and the cut is made with a margin of roughly half a character, so that no glyph is bisected. If the two groups are interleaved instead, the disagreement is per-letter drift, not composed typography. No boundary exists, and the crop takes the mixed-typography verdict directly. That refusal is what prevents the system from imposing structure on noise. Each half re-enters the pipeline as an ordinary crop. The split is attempted only once: a word still incoherent after one cut is not a composition of typefaces but deformation past recovery, and "mixed typography" is already the honest answer for it. The added cost is negligible. The tokens exist from the original forward pass, the clustering runs over at most sixteen column vectors, and extra encoder passes arise only for the two halves of crops that were actually flagged.

The unknown verdict needs a precise reading, because it carries a genuine ambiguity. "Unknown" means the crop resembled no palette font closely enough to justify a name. Two different situations produce that outcome, and the system cannot tell them apart: the text may be set in a real typeface outside the 50-to-100-font palette, or it may be hallucinated past the point where any typeface is recoverable. Both surface identically. What the verdict does guarantee is the behavior that motivates the open-set design of Section 4.2.1: no font is ever invented to fill the gap, which is precisely what a closed-set classifier is forced to do.

The third band, *how we measure it*, holds the researcher instruments of Section 4.2 rather than any part of the served system. Top-K accuracy records how often the true font appears in the shortlist. The re-render check scores the structural distance between a re-rendering of the predicted font and the original crop. The model comparison benchmarks the recognizer against the closed-set baselines and the alternative backbones, under the protocol of Section 4.10.2. The human-proxy panel supplies the accuracy floor. These run offline, over held-out evaluation sets, and produce no output the designer ever sees.

**Figure 8**

*Conceptual Framework of the Proposed Font-Identification System*

![Diagram with three enclosed horizontal bands. Top band, before deployment: the Google Fonts palette is rendered into pristine word crops, expanded by the operator D with degraded look-alikes, and the combined pristine-plus-degraded corpus trains a teacher model (DINOv2 with LoRA, offline only) and a student metric head f-theta, which learns from font labels through triplet loss and from the teacher through distillation; the band ends in the trained model, meaning the weights f-theta and the match threshold tau. A dashed arrow carries that model into the middle band, loaded once at startup. Middle band, at use: an AI-generated image from DALL-E, Midjourney, or Stable Diffusion passes through off-the-shelf text localization, which emits one bounding box per word; each word crop is then resized to 224 by 224 pixels, converted to grayscale and rescaled in brightness, encoded by the frozen DINOv2 Vision Transformer, passed through a same-font check that asks whether the crop's patches agree on one style (splitting the crop once if not), projected by the metric head into a font-style fingerprint, and put to a match test against the threshold tau. Three verdicts follow: passing crops yield a Top-K Google Fonts shortlist, one per crop; crops whose closest font falls short of tau yield an unknown-font verdict in which no font is guessed; and crops that remain style-incoherent after one split yield a mixed-typography verdict in which no single font is assigned. Bottom band, how we measure it: Top-K accuracy, the re-render check, the model comparison against closed-set baselines and alternative backbones, and the human-proxy panel, marked as researcher instruments never shown to the user. An in-figure legend defines solid arrows as the per-image path and dashed arrows as researcher-side work outside it](../../assets/figures/conceptual_framework.png)

The figure is read through the line convention stated in its legend. Solid arrows mark the per-image path: every step that executes when a designer submits an image. Dashed arrows mark researcher-side work outside that path, which covers both the preparation band above and the measurement band below. The two kinds of flow meet at exactly one point, where the trained model is loaded into the running system at startup. That hand-off is drawn dashed because it happens before the per-image path, not during it. The localization step stays solid because it does run live on every request, even though it is off-the-shelf and replaceable; keeping it solid keeps the thesis focused on the recognition that follows it. Two absences from the figure are deliberate. The web application does not appear, because it is a delivery surface rather than a conceptual stage; it is specified in the system architecture of Section 4.5.2 instead. The measurement band is drawn outside the per-image path for the same reason the re-render check is not a runtime step: the structural comparison of Section 4.2.2 is a validation instrument, applied by the researchers to held-out data. It neither re-ranks the shortlist nor reaches the designer. This separation is what lets the same model serve live requests while remaining fully reproducible from the researcher-controlled data pipeline.

**The framework as a step-by-step process.** For an outside researcher, the three bands of Figure 8 unfold into the following ordered procedure. Each step names its input, its operation, and its output. The section that owns a step's parameters is cited in place, so the full detail of any step is one reference away.

*Before deployment, executed once by the researchers:*

1. **Select the palette.** The top 50 to 100 Google Fonts are curated across the four structural family classes, under the bounding rationale of Section 4.1. Output: a fixed set of font files, each a named class.
2. **Render pristine crops.** Every palette font is rendered into word crops under the image and text properties of Section 4.3.1. Output: labeled clean images, the font of each known by construction.
3. **Degrade.** Each pristine crop passes through the operator $D$ of Section 3.2.3 at logged intensities. Output: hallucinated look-alikes carrying the same label. The corpus holds both the pristine crops and the degraded copies, one metadata row each (Table 1).
4. **Partition.** The corpus splits 70/15/15 into training, validation, and test sets, stratified as in Section 4.3.2. The validation and test slices are not touched again until steps 8 and 11.
5. **Train the teacher.** DINOv2 with the LoRA adaptation of Section 4.3.2 is fitted to the font labels on the training slice. Output: a supervising model that never leaves this band.
6. **Train the student.** The metric head $f_\theta$ trains on the same slice under two simultaneous signals: the triplet objective on the labels (Chapter 3), and distillation toward the teacher's similarity judgments, which consults no labels. Output: an embedding function that maps any crop to a font-style fingerprint.
7. **Build the palette map.** Every training crop of each font is embedded by the finished student and averaged into that font's prototype. Output: one reference fingerprint per palette font.
8. **Calibrate.** Validation crops are embedded and scored against their nearest prototypes. $\tau$ is fixed at the cutoff that accepts 95% of the crops whose font truly is in the palette, the operating point of Section 4.10.2. Output: the trained model, meaning $f_\theta$, the prototypes, and $\tau$. The teacher is discarded.

*At use, executed for every uploaded image:*

9. **Ingest.** The user submits a raster image in an accepted format (Section 4.2.4). The off-the-shelf localizer emits one bounding box per word, and each word crop proceeds independently.
10. **Embed and check.** Inside the model's forward pass, each crop is prepared (square-pad, 224², grayscale, normalize; Section 4.3.2), encoded by the frozen backbone, and projected by $f_\theta$ into a fingerprint. The same pass yields the patch tokens for the homogeneity check described above. A flagged crop is split once, and each half re-enters this step; a half that stays incoherent exits with the mixed-typography verdict.
11. **Decide.** The fingerprint's similarity to its nearest prototype meets the match test. At or above $\tau$, the crop returns its Top-3 shortlist with similarity scores and live font previews. Below $\tau$, it returns the unknown-font verdict. Adjacent words with the same verdict merge into one region card in the interface (Section 4.5).

*How we measure it, executed offline on held-out data:*

12. **Score recognition.** Top-1/Top-3 accuracy is computed on the untouched synthetic test slice and on the real-generative set, whose ground truth is the human-proxy panel consensus of Section 4.2.3.
13. **Verify predictions structurally.** The re-render check of Section 4.2.2 scores each accepted prediction against its input crop.
14. **Compare.** The closed-set baselines and the backbone comparison run under the protocol of Section 4.10.2, on the same data and the same calibration recipe.

Any researcher holding the released code, the pinned seeds and versions (Section 4.7.3), and this sequence can regenerate the corpus bit-for-bit, retrain both models, arrive at the same $\tau$, and reproduce the reported tables. That is the standard the framework is built to meet.

### 4.4.3 Value Proposition

The design suits its problem for three reasons. First, it is open-set. A closed-set classifier must name some font for every input; this system can refuse, which matters because many generative crops correspond to no real typeface at all. Second, it is trained on the hallucination distribution itself rather than on pristine glyphs, so it does not collapse on the warped, re-kerned input that defeats commercial identifiers and clean-glyph baselines. Third, it targets a localized open-source palette, so every match it returns is immediately reusable at no cost. Recognition ends in a template the designer can rebuild from, not in a paywalled lookup.

### 4.4.4 High-Level Operational Logic

From the user's side, the interaction is simple. A designer opens the web application, uploads a generative-AI image containing text, and waits a moment while the system localizes the text, crops it, and runs each crop through the inference engine. For every detected region, the application displays a short ranked list of candidate Google Fonts, each shown as a rendered preview, or an "unknown" message when the system judges the glyph to fall outside its palette. The designer picks the closest match and reuses it directly in their own document. The user needs no knowledge of embeddings, thresholds, or the training pipeline. The technical machinery of Sections 4.2 and 4.3 stays hidden behind a single upload-and-review interaction.

## 4.5 Analysis and Design

This section turns the concept of Section 4.4 into a specification. Section 4.5.1 states what the system must do and the qualities it must have, scoped to a local testing deployment rather than a public service. Section 4.5.2 describes the architecture that satisfies those requirements and how its parts communicate.

### 4.5.1 Requirements Analysis

**Functional requirements.** The system must:

1. Accept an uploaded generative-AI image in common raster formats (PNG, JPEG) through the browser.
2. Localize and crop each text region in the image using an off-the-shelf text detector.
3. Preprocess each crop and embed it with the frozen DINOv2 encoder and the trained metric head.
4. Apply the open-set decision to each crop, either rejecting it as "unknown" or ranking the localized palette.
5. Return, for every detected region, a Top-K shortlist of candidate Google Fonts or an "unknown" verdict.
6. Render a preview of each candidate font so the user can compare it against the source text.
7. Expose the recognition pipeline through a REST endpoint (`/predict`) that the frontend calls.
8. Load the trained model weights once at startup and reuse them across requests.

**Non-functional requirements.** The system should also:

1. Be usable through a single upload-and-review interaction that hides the underlying model (usability).
2. Return results at interactive latency on a single machine, targeting a response within a few seconds per image (responsiveness).
3. Produce the same output for the same input, through deterministic preprocessing and pinned model weights and seeds (reproducibility).
4. Run from a single Docker image on one host, with no external service dependencies at inference time beyond the bundled weights and font files (portability).
5. Keep the localizer, encoder, metric head, and open-set decision as separable components, so any one can be replaced without rewriting the others (maintainability).
6. Operate as a single-user local demo, with no authentication, accounts, or multi-user scaling in scope (a deliberate delimitation, consistent with Section 4.1).
7. Report an honest "unknown" rather than a forced guess when the open-set score falls below threshold (transparency).

### 4.5.2 System Architecture

The architecture is a layered client-server design, shown in Figure 9. It separates a thin presentation layer from a Python inference backend, and separates both from the model and font resources they depend on.

**Figure 9**

*System Architecture of the Font-Identification Web Application*

![Layered architecture diagram with a user tier (graphic designer), a client tier (React frontend), an API tier (FastAPI backend in Docker), an inference tier (PyTorch service running text localization, preprocessing, the frozen DINOv2 encoder, the metric head, and the open-set decision), and a resources tier (HuggingFace model store, offline-trained metric-head weights, and Google Fonts assets), with a request path down and a results path back up to the client](../../assets/figures/system_architecture.png)

As shown in Figure 9, a request flows from top to bottom, and the result returns to the client. The **client tier** is a React single-page application in the browser. It handles the image upload and renders the Top-K results gallery with font previews. It calls the **API tier**: a FastAPI backend packaged in a Docker image, which exposes the `/predict` endpoint, orchestrates the inference call, and loads the model weights when it starts. The API hands each request to the **inference tier**, a PyTorch service that runs the pipeline of Section 4.4: off-the-shelf text localization, preprocessing, the frozen DINOv2 encoder, the metric head $f_\theta$, and the open-set decision that produces a Top-K shortlist or an "unknown" verdict per crop. The **resources tier** holds what the inference tier reads but does not compute at request time: the DINOv2 backbone and baseline weights pulled from the HuggingFace Hub, the metric-head weights trained offline, and the Google Fonts files used both as the recognition palette and to render the candidate previews.

Two design choices in this layout matter for the rest of the chapter. First, the inference tier is the only component with startup state, and the only one specific to this thesis; the localizer above it and the font assets beside it are replaceable off-the-shelf parts. Second, the offline training that produces the metric-head weights is not part of the request path at all. It runs separately and deposits weights into the resource tier. This keeps the served system reproducible from the researcher-controlled pipeline, and it lets the model be retrained or swapped without touching the API or the frontend.

## 4.6 Development Model

### 4.6.1 Identification of the Model

This study follows an **iterative-incremental** development model. The system is built as a sequence of increments. Each increment runs a full Analyze, Design, Build, and Evaluate cycle, and each delivers a working slice that integrates into the growing whole. The model is shown in Figure 10.

### 4.6.2 Justification

The iterative-incremental model fits this project better than a single-pass model such as Waterfall, for two reasons. First, the work is part research. The behavior of the metric embedding and the open-set threshold cannot be fully specified in advance; each increment's evaluation (Top-K accuracy, or the rejection rate on held-out crops) feeds back into the design of the next. A model that froze the design before any results existed would not survive contact with the data. Second, the components have a natural build order. The recognizer cannot be trained without the synthetic dataset; the open-set decision cannot be tuned without a trained embedding; the web application only has something to serve once the recognizer works. Delivering these as increments keeps a working, testable artifact in hand at every stage, and it isolates risk to one increment at a time, which suits a two-person team without a dedicated QA role.

### 4.6.3 Phases of the Model

The project is organized into four increments, each producing a deliverable that the next increment consumes.

1. **Increment 1: Synthetic data pipeline.** Analyze the documented deformation modes, design the rendering and degradation operator $D$, build the pipeline, and evaluate the crops against the target hallucination distribution. Deliverable: a labeled corpus of pristine and degraded crops (Section 4.3.1).
2. **Increment 2: Metric embedding.** Design and build the frozen DINOv2 encoder with the trained metric head, and evaluate embedding separability across fonts and families. Deliverable: the frozen encoder plus the trained head $f_\theta$ (Section 4.3.2).
3. **Increment 3: Open-set decision and evaluation.** Add the rejection score, the calibrated Top-K, and the structural-distance verification, then evaluate against the baselines and the human-proxy panel. Deliverable: the full recognizer with its Top-K, rejection, and metric outputs (Sections 4.2 and 4.10).
4. **Increment 4: Web application.** Wrap the recognizer in the FastAPI backend and React frontend, then evaluate it interactively on real uploaded images. Deliverable: the running demo application (Section 4.5).

### 4.6.4 SDLC Diagram

**Figure 10**

*Iterative-Incremental Development Model*

![Diagram of four increments (synthetic data pipeline, metric embedding, open-set and evaluation, web application) arranged left to right, each running an Analyze, Design, Build, and Evaluate cycle with a refine loop and producing a deliverable, and each deliverable integrating into a cumulative working system band beneath them](../../assets/figures/sdlc_model.png)

As shown in Figure 10, the four increments proceed left to right. The arrows within each increment show that development is not linear inside it: the Analyze, Design, Build, and Evaluate phases repeat, and each evaluation refines the same increment before the next one begins. The deliverables accumulate into a single working system rather than being integrated only at the end. A failure surfaced late, for example an open-set threshold that rejects too many valid crops, can therefore be traced to the increment that introduced it.

## 4.7 Development Approach

### 4.7.1 Bottom-Up Construction

The system is built **bottom-up**. Construction starts at the data and model layers and works upward to the interface, in the increment order of Section 4.6: the synthetic data pipeline first, then the metric embedding, then the open-set decision and evaluation, and only last the web application that presents them. This direction follows the dependency structure of the problem: each layer is useless to test until the one beneath it works. It also matches the runtime-versus-offline split of Figure 8, in which the offline pipeline produces trained weights that the served system later loads. The alternative, a top-down approach that starts from the user interface and stubs out the model, would have deferred the project's central research risk (whether a deformation-robust open-set recognizer is achievable at all) until after the surface was built. That is the opposite of what the schedule can afford.

### 4.7.2 Architectural Patterns

The build organizes around a few standard patterns. The application is a **layered client-server** system with a clear separation of concerns: presentation in the React client, request handling in the FastAPI service, and recognition in the PyTorch inference tier (Section 4.5.2). The client and server communicate over a **REST** interface, which keeps the frontend independent of the model internals and lets either side be developed against a fixed contract. The recognizer itself is a **modular pipeline**: text localization, preprocessing, encoding, the metric head, and the open-set decision are separate stages with defined inputs and outputs. Any stage can be replaced (swapping the off-the-shelf localizer, for instance) without disturbing the others. Inference is **stateless** across requests: the model weights load once at startup, and each request is handled independently, which keeps the served component simple and reproducible.

### 4.7.3 Coding Philosophy

Three principles guide how the code is written. The first is **reproducibility**. Random seeds, pinned dependency versions, and fixed model weights are all recorded, so any run can be regenerated. The preprocessing transforms are embedded in the model's forward pass, so training and serving apply identical steps and no train-serve skew can creep in (Section 4.3.2). The second is **reuse over reinvention**. The backbone (DINOv2), the baseline classifiers, and the text localizer are taken off the shelf rather than rebuilt. Effort concentrates on the thesis's actual contribution: the deformation-robust open-set recognizer. The third is **configuration over hard-coding**. The palette size, degradation parameters, Top-K value, and rejection threshold are configurable settings, not constants buried in the code. This is what makes the iterative evaluation of Section 4.6 practical, since each increment can re-tune these values without a rewrite.

## 4.8 Software Development and Tools

The stack is chosen against a few criteria. Every tool is free and open-source, so the system can be replicated at no licensing cost, consistent with the free-reconstruction goal of the study. Each is mature and widely supported, so documentation and community help are available. And each is the standard choice in its layer, which keeps the learning curve low for a two-person team. Because the served system is stateless and persists nothing between requests (Section 4.7.2), no database is used, and the database-connectivity criterion does not apply. Table 2 lists the tools by function, with the version used and an access link; the role each tool plays is discussed below the table.

**Table 2**

*Software and Tools Used in the Development of the System*

| Function | Tool | Version | Access link |
|----------|------|---------|-------------|
| Language and model | Python | 3.13 | https://www.python.org |
| Language and model | PyTorch | 2.6 | https://pytorch.org |
| Language and model | Hugging Face Transformers | 4.49 | https://github.com/huggingface/transformers |
| Language and model | Hugging Face Hub | 0.28 | https://huggingface.co |
| Language and model | NumPy | 2.2 | https://numpy.org |
| Language and model | scikit-learn | 1.6 | https://scikit-learn.org |
| Data and rendering | Pillow (PIL) | 11.1 | https://python-pillow.org |
| Data and rendering | OpenCV | 4.11 | https://opencv.org |
| Data and rendering | EasyOCR | 1.7 | https://github.com/JaidedAI/EasyOCR |
| Backend | FastAPI | 0.115 | https://fastapi.tiangolo.com |
| Backend | Uvicorn | 0.34 | https://www.uvicorn.org |
| Backend | Pydantic | 2.10 | https://docs.pydantic.dev |
| Frontend | React | 19 | https://react.dev |
| Frontend | Vite | 6 | https://vite.dev |
| Frontend | Node.js | 22 LTS | https://nodejs.org |
| Deployment | Docker | 27 | https://www.docker.com |
| Version control | Git | 2.47 | https://git-scm.com |
| Version control | GitHub | (web service) | https://github.com |
| Documentation | Matplotlib | 3.10 | https://matplotlib.org |
| Documentation | Pandoc | 3.10 | https://pandoc.org |
| Documentation | Visual Studio Code | 1.98 | https://code.visualstudio.com |

*Note.* Versions are current as of July 2026 and are pinned in the project's dependency lockfiles; a replicator should confirm the latest compatible releases at the time of setup. All tools are open-source and free to use; the hosted collaboration service (GitHub) offers a no-cost tier sufficient for this project.

In the language-and-model layer, Python is the primary language for the data pipeline, the model, and the backend, with PyTorch as the deep-learning framework for the encoder, the metric head, and training. Hugging Face Transformers loads the DINOv2 backbone and the baseline classifiers. The Hugging Face Hub pulls pre-trained weights and stores the trained metric head. NumPy carries the array and numerical operations, and scikit-learn supplies the evaluation metrics, the stratified k-fold split, and the confusion matrix. In data and rendering, Pillow renders font specimens into word-crop images, OpenCV applies the elastic warp and the other degradation operations, and EasyOCR performs the off-the-shelf text localization and cropping. The backend exposes inference through FastAPI's `/predict` REST endpoint, served by the Uvicorn ASGI server, with Pydantic validating request and response schemas. The frontend is a React interface for image upload and the results gallery, built by Vite on the Node.js runtime. Docker containerizes the backend for reproducible deployment, and Git and GitHub provide version control and repository hosting. The documentation toolchain uses Matplotlib to generate the thesis figures, Pandoc to export the Markdown chapters to DOCX, and Visual Studio Code as the primary editor.

## 4.9 Project Management

### 4.9.1 Schedule and Timeline

The project runs from June to December 2026. The schedule follows the increment order of Section 4.6, with the written chapters interleaved so that each empirical chapter is drafted as its results become available. Figure 11 shows the plan as a Gantt chart. As of the reporting date (July 10, 2026), Chapters 2 and 3 are complete and Chapter 4 is in progress; the four development increments, the results and conclusion chapters, and the final revisions follow through December.

**Figure 11**

*Project Schedule and Timeline (June to December 2026)*

![Weekly-cell Gantt grid spanning June to December 2026 with four week columns per month, tasks grouped into Writing, Development, and Closeout. Writing shows Chapter 2 and Chapter 3 completed, Chapter 4 in progress at the July 10 marker, and Chapters 5 and 6 planned. Development breaks the four increments into subtasks (palette and rendering, degradation operator, encoder and metric head, training and distillation, open-set and Top-K, evaluation and human panel, backend API, frontend and Docker). Closeout covers revisions and final defense in December](../../assets/figures/gantt_timeline.png)

As shown in Figure 11, the early months cover the written groundwork (Chapters 2 and 3). The middle months carry the build increments, from the synthetic data pipeline through the web application. The final months are reserved for the results and conclusion chapters and for revision ahead of the defense. The development increments deliberately overlap the empirical chapters, because Chapter 5 reports the evaluation that increment 3 produces.

### 4.9.2 Responsibilities

The study is carried out by two researchers, both of whom act as researcher and developer. Table 3 divides the work. The split follows the two sides of the system: one member owns the Python model and data side, the other owns the service and interface side, and the writing is shared with cross-review.

**Table 3**

*Division of Responsibilities*

| Member | Responsibilities |
|--------|------------------|
| Janritch Diputado | Python scripting: synthetic data pipeline, model training, and the inference engine. Lead author of Chapter 2 (Review of Related Literature) and Chapter 3 (Technical Background). |
| Matt Cabarrubias | Backend REST API (FastAPI) and the React frontend web application. Lead author of Chapter 4 (Methodology); contributor and reviewer for Chapters 2 and 3. |
| Both (shared) | System design, integration, evaluation and human-proxy panel coordination, and preparation for the final defense. |

*Note.* Authorship is stated by lead contributor; both members reviewed and contributed to all chapters.

### 4.9.3 Budget and Cost Management

The budget below estimates what it would cost another researcher or organization to replicate this study, not only the out-of-pocket cost to the current team. It therefore includes labor, since replication effort is the largest real cost, alongside compute, utilities, documentation, and contingency. Because the entire software stack is open-source (Section 4.8), the study carries no mandatory license or subscription cost. That is a deliberate outcome of the free-reconstruction design. Table 4 lists the estimate.

**Table 4**

*Estimated Replication Budget*

| Category | Item | Basis / assumption | Amount (PHP) |
|----------|------|--------------------|-------------:|
| Labor | 2 researcher-developers | ~30 weeks × ~15 hr/week each ≈ 900 hours total, at an illustrative ₱250/hr | 225,000 |
| Compute | Cloud GPU for training and experiments | ~100 to 150 GPU-hours; the backbone is frozen and only the metric head trains, so free Colab/Kaggle tiers can bring this near ₱0 | 5,000 |
| Subscriptions | Software stack | Fully open-source; none required | 0 |
| Data storage | Synthetic dataset | Generated locally (a few GB); no paid storage | 0 |
| Utilities | Internet and electricity | ~₱1,500/month × 7 months, shared | 10,500 |
| Documentation | Hard-bound thesis copies | ~₱1,500 × 3 copies | 4,500 |
| Contingency | Overhead on non-labor items | ~10% | 2,000 |
| **Total (with labor)** | | Full replication cost | **~247,000** |
| **Total (materials only)** | | If replicated by unpaid students | **~22,000** |

*Note.* Figures are planning estimates, not incurred expenses. The labor line dominates and is the most adjustable: it scales with the hourly rate and with how much of the pipeline a replicator reuses from the released code. The materials-only total reflects the near-zero software cost that the open-source stack makes possible.

## 4.10 Verification, Validation and Testing

This section describes how the study checks its own work, along three axes. Verification asks whether the system is built correctly. Validation asks whether the correct system was built, in the sense of meeting the objectives of Section 1.2. Testing asks whether the software runs without errors. The study uses a combined **build method** and **model method**. The build method delivers the working artifacts (the recognizer and the web application) as evidence that the approach is realizable. The model method evaluates an abstract model of the system through quantitative metrics on held-out data, which allows controlled measurement that the deployed application alone could not provide.

### 4.10.1 Verification: Building the System Right

Verification targets the internal correctness of each component. The pipeline stages of Section 4.4 (localization wrapper, preprocessing, encoder, metric head, and open-set decision) are checked with unit and integration tests. These confirm that each stage produces output of the expected shape and range, and that the stages compose end to end. Reproducibility is verified directly. Random seeds, dependency versions, and model weights are pinned (Section 4.7.3), so a fixed input must regenerate a bit-identical dataset and the same prediction on every re-run. The preprocessing-in-forward design is verified by confirming that the training-time and inference-time transforms produce identical tensors for the same crop, which proves no train-serve skew is present. The team has no separate QA role, so the two members cross-review each other's code; that review is the verification pass on the parts each did not write.

### 4.10.2 Validation: Building the Right System

Validation asks whether the system meets the specific objectives of Section 1.2.3. This is where the study's quantitative and qualitative measures are applied, and each objective maps to a measure.

For the recognition objective, the system is scored under the **Top-1 and Top-3 accuracy** protocol that DeepFont established as the field standard (Wang et al., 2015), on both the held-out synthetic test partition and the separate real-generative test set. For the open-set objective, rejection quality is measured by the true-positive and false-positive rates at the operating threshold. The result is reported as the false-positive rate at 95% recall, so the fraction of out-of-palette crops wrongly accepted is stated explicitly. For the verification-of-prediction objective, each predicted font is re-rendered and scored against the input crop with a deformation-robust structural distance (Zhang et al., 2024). The error distribution is then analyzed by typographic family through a confusion matrix, and weighted by the embedding-centroid severity index, so that within-family errors are distinguished from more damaging cross-family ones (Chen et al., 2026). Finally, the calibrated Top-K shortlist is validated by its empirical coverage: whether the prediction sets contain the true font as often as the conformal guarantee claims (Ding et al., 2025; Shi et al., 2024).

Validation is also comparative and human-anchored. The system is benchmarked against two closed-set baselines, the Storia-AI Google Font Classifier (Jiang et al., 2025) and the DINOv2-LoRA model of Chen et al. (2026), both run on the same real-generative crops. The comparison quantifies how much the open-set, deformation-trained approach recovers where pristine-trained baselines collapse. The ground truth for those crops is set by the three-person expert **human-proxy panel** (Section 4.2.3). Each rater independently assigns a palette font or an "unknown" verdict to each of the [N = 100] real generative text boxes; a label is fixed by agreement of at least two of three; and rater agreement is reported as a Fleiss' $\kappa$ of [κ = X.XX]. The panel provides the accuracy floor for the comparison, and it independently estimates how often genuine typographic ambiguity occurs in uncorrected generative output.

Two further validation instruments follow from the word-level design of Section 4.4.2. The first validates the mixed-typography verdict. The synthetic pipeline renders a **mixed-font stressor set** on demand: lines and words deliberately set in two palette fonts at controlled mixing ratios, then degraded by the operator $D$ like every other crop. On this labeled data, which no in-the-wild collection could supply, the detection rate and false-alarm rate of the homogeneity check are measured directly. The check's dispersion cutoff is calibrated on the same stressor set, using the operating-point recipe used for $\tau$. Its real-world validity is then reported as the agreement between the check's flag and the panel's coherence judgment (Section 4.2.3) on the real-generative crops. Because the served unit is the word crop, the threshold calibration of this section is likewise performed on word-granularity validation crops.

The second instrument validates the choice of encoder, by a **backbone comparison** rather than by assumption. The same frozen-encoder-plus-metric-head recipe, the same corpus, and the same calibration procedure are re-run with only the backbone swapped: the incumbent DINOv2 (Oquab et al., 2024) against a contrastively pretrained vision-language encoder (SigLIP; Zhai et al., 2023), a supervised ViT (Dosovitskiy et al., 2021), and a convolutional baseline (ConvNeXt; Liu et al., 2022). Each candidate is reported with its Top-1/Top-3 accuracy, false-positive rate at 95% recall, parameter count, and CPU and GPU inference latency. One capability requirement narrows the field before speed and accuracy decide it: the homogeneity check reads per-patch tokens, so a qualifying backbone must expose patch-level features. That is a property of the ViT family which a pooled convolutional embedding does not natively provide. The comparison therefore selects the deployed model on measured evidence, with the architecture class justified by the capability the pipeline requires of it. Table 5 profiles the four candidates: what the literature already establishes about each, and which columns only this study's runs can fill.

**Table 5**

*Candidate Backbones for the Encoder Comparison*

| Backbone (checkpoint) | Pretraining signal | Size and compute (224² input) | Patch-level features | Reported ImageNet-1k accuracy |
|-------|------|------|------|------|
| DINOv2 ViT-B/14 (`facebook/dinov2-base`) | Self-supervised (Oquab et al., 2024) | 86.6M params · ≈23 GFLOPs | Yes: native patch tokens | 84.5% (linear probe on frozen features) |
| SigLIP ViT-B/16 (`google/siglip-base-patch16-224`) | Contrastive image-text (Zhai et al., 2023) | 203M with the text tower; only the ViT-B vision tower (≈17.6 GFLOPs) runs here | Yes: native patch tokens | Published evaluations use a zero-shot protocol not comparable to the other rows (Zhai et al., 2023) |
| Supervised ViT-B/16 (`google/vit-base-patch16-224`) | Supervised classification on ImageNet-21k (Dosovitskiy et al., 2021) | 86.6M params · 17.6 GFLOPs | Yes: native patch tokens | 84.0% (fine-tuned) |
| ConvNeXt-T (`facebook/convnext-tiny-224`) | Supervised classification (Liu et al., 2022) | 28.6M params · 4.5 GFLOPs | No: pooled feature maps, so it does not qualify for the same-font check | 82.1% (supervised training) |

*Note.* The accuracy column is a general-capability proxy taken from each model's own literature; the evaluation protocols differ (linear probe, fine-tune, supervised training) and the figures are not directly comparable with one another. The compute column is the hardware-independent cost of one forward pass: ConvNeXt-T from Liu et al. (2022); ViT-B/16 from the torchvision reference implementation (17.56 GFLOPs, rounded); DINOv2's patch-14 variant derived from its token count (256 patch tokens against 196, roughly 1.3 times the B/16 rows). Published *latency* figures are not quoted, because the literature reports batch-mode throughput on datacenter accelerators, a regime that does not transfer to this study's deployment condition of one crop at a time on a demo laptop; batching and hardware can even reorder the candidates. The FLOPs column therefore gives the defensible prior (ConvNeXt-T is roughly four times cheaper per crop; the three ViT-B rows sit in one compute class), and the decisive numbers, per-crop CPU and GPU latency measured on the deployment machine against the interactive target of Section 4.5.1, are produced by the comparison runs and reported in Chapter 5. Task accuracy likewise cannot be quoted, because no published work evaluates these backbones on degraded font recognition. The DINOv2-vs-supervised-ViT pair shares one architecture class, so their difference isolates the effect of self-supervised pretraining; ConvNeXt-T anchors the speed floor and the capability contrast.

### 4.10.3 Testing: Confirming the System Works

Testing confirms that the delivered software behaves correctly under normal and abnormal use. The web application is exercised end to end: an uploaded image must return a per-region Top-K shortlist or an "unknown" verdict with font previews, and the `/predict` endpoint is checked against its request and response contract. The responsiveness requirement of Section 4.5.1 is tested by measuring per-image latency against the interactive target. Error handling is tested with abnormal inputs (unsupported file types, images with no detectable text, and crops the recognizer rejects as unknown) to confirm the system fails gracefully rather than crashing. Passing these tests, together with the verification and validation results above, is the evidence that the artifact both works and answers the research questions of Section 1.2.
