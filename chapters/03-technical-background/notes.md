# Chapter 3 — Technical Background

Foundational concepts the reader needs before the methodology (Ch4). **Planning only — prose goes in [`draft.md`](./draft.md).** Grading criteria: [`./CLAUDE.md`](./CLAUDE.md).

> 📄 **The chapter itself is written to [`draft.md`](./draft.md)**, section by section (3.1 … 3.5). This file is the plan only.
> 📚 Source table: [`../../literature/references.md`](../../literature/references.md). Cite each source here, then tag the row's "Cited in" column with `Ch3`.

---

# 📐 MASTER TECHNICAL BACKGROUND PLANNER (Chapter 3 blueprint — NOT the essay)

**Goal:** exactly **15 pp / ~4,500 words**, mathematically rigorous, defense-ready. Built in **4 thematic batches**, written one batch at a time (auto mode) to protect quality and avoid token exhaustion.
**Narrative spine (General → Specific):** T1 → T2 → T3 → T4 — *the field & its concepts → the theory that powers our approach → the tools we build on → the gap we own & the bridge to methodology.*
**Purpose (per `./CLAUDE.md`):** the bridge between general knowledge and the problem statement — not a literature review (Ch2), not the methodology (Ch4).

## Non-negotiable rules (from `./CLAUDE.md`)
1. **General → specific.** Open on the field (AI/ML/CV), narrow to font-style metric learning on hallucinated crops.
2. **Define every term before use.** Every technical term, theory, and model gets a definition (+ equation/diagram where relevant) *before* it is relied upon.
3. **Explain underlying principles.** Cover the math foundations: convolution, distance metrics, optimization/loss, probability/energy scores.
4. **Frameworks with strengths AND limitations.** Every tool (ViT/DINO/SSIM/PyTorch/diffusion) names what it does well *and* where it falls short.
5. **Situate the problem.** State explicitly why current solutions are insufficient (sets up the thesis gap).
6. **End with a transition to Ch4** (methodology) — T4 only.
7. **APA throughout**, anchored to `references.md`; paraphrase mostly, quote sparingly. Tag each used row `Ch3`.
8. **Balance detail** — inform without becoming a textbook.
9. **No fabricated data.** `[X.XX]` only for *this thesis's own* empirical values; literature metrics come from `references.md`.

## APA visual rules (apply to EVERY figure/table)
- **Bold** "Figure N" / "Table N" placed **above** the visual; *italic Title-Case caption* directly **below** the number.
- **In-text introduction before** it appears ("Figure 1 illustrates …") **and a follow-up evaluation sentence after** ("As shown in Figure 1, …").
- If adapted, cite the source in a *Note.* below the caption and ensure the row exists in `references.md`.
- Tables: no vertical lines, minimal horizontals, consistent font, aligned numbers.

## Format
A4, double-spaced, 12 pt body, 1" margins all sides → **~300 words / double-spaced page** → 15 pp ≈ **4,500 words**.

---

## Batch map + allocation matrix (4 batches, 15 pp / ~4,500 w)

| Batch | Prof. §§ | draft.md section(s) | Themes | Refs | Words | Pages |
|---|---|---|---|---|---|---|
| **T1** | §1 + §2 | 3.1 Introduction to the Domain · 3.2 Core Concepts & Definitions | AI→ML→DL→CV→font-recognition funnel; font anatomy (serif/sans/display/mono, x-height, terminals, stroke contrast, counters); typographic-hallucination formal definition; CNN convolution + feature maps + pooling; embedding space | 27, 28, 30, 10, 29, 31, 32 | ~1,350 | ~4.5 |
| **T2** | §3 | 3.3 Theoretical Foundations | supervised vs self-supervised; metric learning (embedding fn, distance metric); contrastive & triplet loss; open-set recognition + open-space risk; logit/energy rejection scores | 34, 3, 23, 24, 1, 2, 4, 5 | ~1,200 | ~4 |
| **T3** | §4 | 3.4 Existing Technologies & Frameworks | ViT (patch embedding, self-attention); DINO/DINOv2 frozen encoders + register tokens; classical SSIM → DeepSSIM/SAMScore; diffusion latent mutation; PyTorch — **each with strengths + limitations** | 33, 21, 6, 7, 25, 35, 16, 17, 29 | ~1,050 | ~3.5 |
| **T4** | §5 (+ chapter intro para, + Ch4 bridge) | 3.5 Problem Context & Transition | closed-set assumption breaks; pristine over-fit of `font-classify` baseline; pixel-SSIM collapse on warped glyphs; VLMs get lost; consolidated thesis gap; transition to Ch4 | 10, 11, 20, 22 (+ synthesis of prior refs) | ~600 | ~2 |

**Totals:** prose ~4,200 w + equation/caption exposition ~300 w = **~4,500 w**. ~5–6 figures (§6 Illustrations) ≈ 1.5 pp, absorbed within the batch page counts.
**§6 Illustrations** is not a standalone batch — it is woven across T1–T4 and produced by the `src/visualization/` tooling track (see bottom of this file). Figure ownership: T1 → Figs 1–3, T2 → Fig 4, T3 → Figs 5–6, T4 → Fig 7.

---

## Batch T1 — Introduction to the Domain & Core Concepts
- **draft.md sections:** 3.1, 3.2 · **Refs:** 31, 32, 27, 28, 30, 10, 29 · **Words:** ~1,350 · **Figures owned:** 1, 2, 3
- **Objective:** Lay the General→Specific runway. Open at the field level (AI ⊃ ML ⊃ deep learning ⊃ computer vision) and funnel to visual font-style recognition; then formally define every core object the rest of the thesis manipulates — glyph anatomy, the typographic-hallucination model, the CNN, and the embedding space.
- **Define-before-use list:** artificial intelligence; machine learning; deep learning; computer vision; typography; glyph; typeface vs. font; font family classes (serif, sans-serif, display, monospace); glyph structural traits (x-height, terminal, stroke contrast, counter, ascender/descender); **typographic hallucination** (probabilistic glyph deformation, micro-warping, variable kerning); convolutional neural network; convolution kernel; feature map; receptive field; pooling; embedding / feature vector; embedding space.
- **Sub-section order (3.2):** 3.2.1 typography & font anatomy → 3.2.2 typographic hallucination (formal degradation model) → 3.2.3 CNNs & visual feature extraction → 3.2.4 embedding spaces.
- **Equations (define every symbol immediately after):**
  - Convolution: `(I * K)(i, j) = Σ_m Σ_n I(i+m, j+n) · K(m, n)`
  - Feature-map output dimension: `O = ⌊(W − F + 2P) / S⌋ + 1`
  - Degradation operator (formalizes the hallucination model): `x̃ = D(x; θ_warp, θ_blur, θ_kern)` where `D` composes elastic warp, Gaussian blur/noise, and kerning jitter.
- **Figures:** **Figure 1** font-anatomy panel (`font_anatomy.py`); **Figure 2** CNN conv→pool→FC block (`cnn_block.py`); **Figure 3** degradation pipeline clean→warp→blur→kern (`degradation_pipeline.py`).

```
Write Batch T1 of Chapter 3 (Technical Background) — sections 3.1 "Introduction to the Domain" and
3.2 "Core Concepts & Definitions." Target ~1,350 words (~4.5 double-spaced pp at 300 w/pp). Write the
prose into sections 3.1 and 3.2 of chapters/03-technical-background/draft.md — NEVER into notes.md.

Follow chapters/03-technical-background/CLAUDE.md exactly. Enforce a strict GENERAL → SPECIFIC arc:
open at the field level (AI ⊃ machine learning ⊃ deep learning ⊃ computer vision) and funnel down to
visual font-style recognition, then to the GenAI-hallucinated-crop regime this thesis targets. DEFINE
EVERY TERM BEFORE USE (typography, glyph, typeface vs font, serif/sans/display/monospace, x-height,
terminal, stroke contrast, counter; typographic hallucination; CNN, kernel, feature map, receptive
field, pooling; embedding, embedding space).

Render these equations in LaTeX and define every symbol immediately after each: (1) the convolution
operation (I*K)(i,j)=Σ_m Σ_n I(i+m,j+n)K(m,n); (2) feature-map output dimension O=⌊(W−F+2P)/S⌋+1;
(3) a formal degradation operator x̃ = D(x; θ_warp, θ_blur, θ_kern) that models typographic
hallucination as a composition of elastic warp, Gaussian blur/noise, and kerning jitter.

Use ONLY references [31, 32, 27, 28, 30, 10, 29] from literature/references.md with flawless APA
in-text citations; tag each used row's "Cited in" column with Ch3. Anchor the deep-learning/CNN
definitions on LeCun, Bengio, & Hinton (2015) and Goodfellow, Bengio, & Courville (2016); use Sarker
(2021) and Plastropoulos & Tegos (2024) for the taxonomy/augmentation framing; DeepFont (Wang et al.,
2015) as the domain anchor for font recognition; Li, Song, et al. (2025) to motivate why texture, not
semantics, must be read; Kondo et al. (2024) to ground the hallucination-as-native-diffusion-output
claim.

Include Figure 1 (font anatomy), Figure 2 (CNN conv→pool→FC block), and Figure 3 (degradation
pipeline). For EACH figure apply APA rules: bold "Figure N" above, an *italic Title-Case caption*
below, an explicit in-text introduction BEFORE the figure and an evaluation sentence AFTER; add a
"Note." with an APA citation if the figure is adapted. Do NOT fabricate metrics — use [X.XX] only for
this thesis's own empirical values.
```

---

## Batch T2 — Theoretical Foundations
- **draft.md section:** 3.3 · **Refs:** 34, 3, 23, 24, 1, 2, 4, 5 · **Words:** ~1,200 · **Figures owned:** 4
- **Objective:** Supply the mathematical engine. Define the learning paradigms, then metric learning (the *representation + distance* the thesis reasons over), then open-set recognition (the *reject-the-unknown* machinery) — the two pillars the methodology assembles.
- **Define-before-use list:** supervised vs. unsupervised vs. self-supervised learning; label; loss function; **metric learning**; embedding function `f_θ`; distance metric (Euclidean, cosine); positive/negative/anchor; **contrastive loss**; **triplet loss**; margin; **open-set recognition**; known/unknown class; **open-space risk**; rejection score; logit; softmax; **energy score**; threshold.
- **Sub-section order:** 3.3.1 learning paradigms (supervised → self-supervised) → 3.3.2 metric learning & embedding distance → 3.3.3 open-set recognition & rejection scores.
- **Equations (define every symbol):**
  - Euclidean & cosine distance: `d(a,b) = ‖f(a) − f(b)‖₂`; `cos(a,b) = f(a)·f(b) / (‖f(a)‖‖f(b)‖)`
  - Triplet loss: `L = Σ_i [ ‖f(aᵢ) − f(pᵢ)‖² − ‖f(aᵢ) − f(nᵢ)‖² + α ]₊`
  - Softmax: `σ(z)_i = e^{z_i} / Σ_j e^{z_j}`
  - Energy score: `E(x) = −T · log Σ_i exp(f_i(x) / T)`
  - Open-space risk framing `R_O(f)` — the fraction of "open space" a recognizer labels as known; motivates thresholded rejection.
- **Figure:** **Figure 4** embedding space with known-font clusters + open-set rejection boundary (`embedding_space.py`).

```
Write Batch T2 of Chapter 3 (Technical Background) — section 3.3 "Theoretical Foundations." Target
~1,200 words (~4 double-spaced pp). Write the prose into section 3.3 of
chapters/03-technical-background/draft.md — NEVER into notes.md.

Follow chapters/03-technical-background/CLAUDE.md. Continue the GENERAL → SPECIFIC arc from 3.2:
learning paradigms (supervised → unsupervised → self-supervised) → metric learning → open-set
recognition. DEFINE EVERY TERM BEFORE USE (loss function; metric learning; embedding function f_θ;
Euclidean and cosine distance; anchor/positive/negative; contrastive and triplet loss; margin;
open-set recognition; known/unknown class; open-space risk; rejection score; logit; softmax; energy
score; threshold).

Render these equations in LaTeX and define every symbol immediately after: Euclidean distance
d(a,b)=‖f(a)−f(b)‖₂ and cosine similarity; triplet loss L=Σ[‖f(a)−f(p)‖²−‖f(a)−f(n)‖²+α]₊; softmax;
energy score E(x)=−T·log Σ exp(f_i(x)/T); and a conceptual open-space-risk R_O(f) framing that
motivates thresholded rejection.

Use ONLY references [34, 3, 23, 24, 1, 2, 4, 5] with flawless APA in-text citations; tag each used
row's "Cited in" with Ch3. Anchor metric learning / triplet loss on Schroff, Kalenichenko, & Philbin
(2015); use Wang et al. (2024, NCL) for disentangled embeddings and Huang & Zhou (2022) + Umer et al.
(2022) for the proximity-ranking rationale; ground open-set rejection on Hofmann et al. (2024, energy),
Djurisic et al. (2024, logit scaling), Karunanayake et al. (2025, ExCeL runner-up ranking), and Lu et
al. (2025, survey). Present each theoretical tool with what it establishes AND its limitation
(e.g., none is validated on typographic OOD).

Include Figure 4 (embedding space with an open-set rejection boundary): bold "Figure 4" above, italic
Title-Case caption below, in-text intro before and evaluation sentence after. Do NOT fabricate metrics;
[X.XX] only for this thesis's own values.
```

---

## Batch T3 — Existing Technologies & Frameworks
- **draft.md section:** 3.4 · **Refs:** 33, 21, 6, 7, 25, 35, 16, 17, 29 · **Words:** ~1,050 · **Figures owned:** 5, 6
- **Objective:** Present the concrete tooling the methodology builds on — **each with strengths AND limitations** (professor rule 4). Two arcs: (a) the representation stack (ViT → DINO/DINOv2 → registers, on PyTorch), (b) the measurement stack (classical SSIM → DeepSSIM/SAMScore), plus diffusion as the generative source.
- **Define-before-use list:** framework/library; PyTorch (dynamic computation graph, autograd); **Vision Transformer (ViT)**; patch embedding; **self-attention** (query/key/value); class token; **DINO/DINOv2** self-supervised distillation; frozen encoder; **register tokens** (high-norm artifact tokens); **SSIM** (luminance/contrast/structure); DeepSSIM (deep-feature SSIM); SAMScore (segmentation-embedding structural score); latent diffusion; latent interpolation.
- **Sub-section order:** 3.4.1 PyTorch & the representation backbone (ViT, self-attention) → 3.4.2 self-supervised frozen encoders (DINOv2 + registers) → 3.4.3 structural-similarity metrics (SSIM → DeepSSIM/SAMScore) → 3.4.4 diffusion as the generative source.
- **Strengths ↔ limitations pairing (mandatory per tool):** PyTorch (flexible dynamic graphs ↔ no built-in typographic priors); ViT (long-range layout attention ↔ data-hungry, quadratic cost); DINOv2 (frozen all-purpose features, no fine-tuning ↔ high-norm artifact tokens); registers (clean feature maps ↔ still validated only on natural images); classical SSIM (interpretable structural distance ↔ collapses under geometric misalignment/warping); DeepSSIM/SAMScore (deformation-robust ↔ validated on natural-image translation, never re-rendered glyphs); diffusion (natively emits novel glyph geometries ↔ unclassified, uncontrolled — the disease, not the cure).
- **Equations (define every symbol):**
  - Scaled dot-product attention: `Attention(Q,K,V) = softmax(QKᵀ / √d_k) V`
  - SSIM: `SSIM(x,y) = [(2μ_x μ_y + C₁)(2σ_xy + C₂)] / [(μ_x² + μ_y² + C₁)(σ_x² + σ_y² + C₂)]`
- **Figures:** **Figure 5** ViT patch-embedding + self-attention schematic (`vit_attention.py`); **Figure 6** SSIM re-render-and-compare pipeline (`ssim_pipeline.py`).

```
Write Batch T3 of Chapter 3 (Technical Background) — section 3.4 "Existing Technologies & Frameworks."
Target ~1,050 words (~3.5 double-spaced pp). Write the prose into section 3.4 of
chapters/03-technical-background/draft.md — NEVER into notes.md.

Follow chapters/03-technical-background/CLAUDE.md. CRITICAL: present EVERY framework with BOTH its
strengths AND its limitations (professor rule 4). Cover, in order: PyTorch (dynamic graphs/autograd ↔
no typographic priors); Vision Transformers and self-attention (long-range layout ↔ data-hungry,
quadratic cost); DINO/DINOv2 frozen self-supervised encoders (all-purpose frozen features ↔ high-norm
artifact tokens) and register tokens as the fix (clean maps ↔ natural-image-only validation);
structural-similarity metrics SSIM → DeepSSIM → SAMScore (interpretable/deformation-robust ↔ classical
pixel-SSIM collapses under geometric misalignment; deep variants validated on natural images, never
re-rendered glyphs); and latent diffusion as the generative SOURCE of hallucination (emits novel glyph
geometries ↔ unclassified/uncontrolled). DEFINE every term before use.

Render these equations in LaTeX with every symbol defined: scaled dot-product attention
Attention(Q,K,V)=softmax(QKᵀ/√d_k)V; and the SSIM index
SSIM(x,y)=[(2μ_xμ_y+C₁)(2σ_xy+C₂)]/[(μ_x²+μ_y²+C₁)(σ_x²+σ_y²+C₂)].

Use ONLY references [33, 21, 6, 7, 25, 35, 16, 17, 29] with flawless APA in-text citations; tag each
used row's "Cited in" with Ch3. Anchor self-attention on Vaswani et al. (2017); ViT layout on Wang,
Lv, et al. (2025, TransTab); frozen encoders on Oquab et al. (2024, DINOv2), Darcet et al. (2024,
registers), and Sheikh et al. (2024, UnSupDLA); SSIM lineage on Wang et al. (2004) → Zhang et al.
(2024, DeepSSIM) → Li et al. (2025, SAMScore); diffusion mutation on Kondo et al. (2024).

Include Figure 5 (ViT patch-embedding + self-attention) and Figure 6 (SSIM re-render-and-compare
pipeline), each with bold "Figure N" above, italic Title-Case caption below, in-text intro before and
evaluation after; cite in a Note if adapted. Do NOT fabricate metrics; [X.XX] only for this thesis's
own values.
```

---

## Batch T4 — Problem Context & Transition to Methodology
- **draft.md section:** 3.5 (+ the ~0.5 pp chapter intro paragraph for 3.1, + the Ch4 bridge) · **Refs:** 10, 11, 20, 22 (+ synthesis of already-cited refs) · **Words:** ~600 · **Figures owned:** 7
- **Objective:** Converge everything into the technical gap that motivates the thesis, then hand off to Ch4. State plainly why current solutions are insufficient *on this input distribution*, and close with the mandatory transition.
- **Define-before-use list:** closed-set vs. open-set assumption; pristine over-fitting; pixel registration; in-the-wild GenAI crop; localized open-set palette (top 50–100 Google Fonts).
- **Problem points (each = "current tool → why it fails here"):** classical OCR/closed-boundary layout (Ponnuru et al., 2024, 98% baseline) excels on anatomically-correct text but presupposes rigid glyph geometry; DeepFont/`font-classify` baseline is pristine-over-fit and closed-set; pixel-SSIM needs registration warped glyphs break; general VLMs get lost in font recognition (Li, Song, et al., 2025); open-set/OOD scores are untested on typographic deformation; ControlText's L2@k/cos@k (Jiang et al., 2025) assume an undeformed input glyph. Glyph-ByT5's <20% figure (Liu et al., 2024) sizes the disease.
- **Consolidated gap:** none couples an attention-isolated crop → deformation-robust frozen-ViT metric embedding → open-set font-identity ranking + calibrated Top-K over a localized Google-Fonts palette on the GenAI-deformed input distribution.
- **Figure:** **Figure 7** end-to-end proposed-framework flowchart (`system_pipeline.py`) — the capstone visual that previews the methodology.
- **Mandatory closer:** a seamless transition sentence into Ch4, e.g. *"Having established the typographic, deep-learning, metric-learning, and open-set foundations — and the specific technical gap they leave open — the next chapter details the synthetic-degradation pipeline, model architecture, and evaluation protocol employed to address it."*

```
Write Batch T4 of Chapter 3 (Technical Background) — section 3.5 "Problem Context," PLUS a ~0.5-page
chapter-introduction paragraph for section 3.1 that frames the General→Specific arc (T1→T4), AND the
closing transition into Chapter 4. Target ~600 words total. Write the prose into
chapters/03-technical-background/draft.md — NEVER into notes.md.

Follow chapters/03-technical-background/CLAUDE.md. Situate the problem: for each current tool, state
what it does well and WHY it fails on this thesis's input distribution — classical OCR/closed-boundary
layout (Ponnuru et al., 2024) presupposes rigid glyph geometry; the DeepFont-style / font-classify
baseline is pristine-over-fit and closed-set; pixel-SSIM requires registration that warped glyphs
break; general VLMs get lost in font recognition (Li, Song, et al., 2025); and ControlText's L2@k/cos@k
(Jiang et al., 2025) assume an undeformed input glyph. Use Liu et al. (2024, Glyph-ByT5) <20% figure to
size the problem. Consolidate into ONE explicit gap: no framework couples attention-isolated crops →
deformation-robust frozen-ViT metric embedding → open-set font-identity ranking + calibrated Top-K over
a localized Google-Fonts palette on the GenAI-deformed distribution.

Use ONLY references [10, 11, 20, 22] plus brief back-references to concepts already established in
3.1–3.4 (no new sources beyond these). Flawless APA; tag each used row's "Cited in" with Ch3.

Include Figure 7 (end-to-end proposed-framework flowchart) with bold "Figure 7" above, italic
Title-Case caption below, in-text intro before and evaluation after. END the chapter with the mandatory
seamless transition sentence pointing directly into Chapter 4 (Methodology): name the synthetic-
degradation pipeline, model architecture, and evaluation protocol. Do NOT fabricate metrics; [X.XX]
only for this thesis's own values.
```

---

## Verification (after each batch + at end)
```powershell
$f="chapters/03-technical-background/draft.md"
$wc=((Get-Content $f -Raw) -split '\s+' | ? {$_ -ne ''}).Count
"words=$wc  ~pp=$([math]::Round($wc/300,1))"
```
**Final gate:** ~4,300–4,700 w (≈14–15.5 pp). Checks:
- [ ] Flows general → specific across 3.1 → 3.5.
- [ ] Every technical term defined before use; every equation defines its symbols.
- [ ] Every framework in 3.4 names **both** a strength and a limitation.
- [ ] 3.5 makes clear why current solutions are insufficient and states the consolidated gap.
- [ ] Chapter ends with a transition into Ch4.
- [ ] Every Figure N has an in-text intro + a post-visual evaluation sentence; bold number above, italic caption below; Note+citation if adapted.
- [ ] Every in-text citation exists in `references.md` and its row is tagged `Ch3`.

---

# 🎨 §6 ILLUSTRATIONS — `src/visualization/` tooling track

Scripts (Matplotlib / Seaborn / Graphviz) that programmatically render the chapter's diagrams to `assets/figures/` as **PNG @ 300 dpi**. One script per figure; figure numbers follow appearance order. **Code is written in a later execution pass — this file specifies the architecture only.** Scaffold marker: [`../../src/visualization/README.md`](../../src/visualization/README.md).

```
src/visualization/
  _style.py                # shared: 300 dpi, font sizes, palette, savefig(name) → assets/figures/<name>.png
  font_anatomy.py          # Figure 1  (T1): serif/sans/display/mono + x-height, terminal, stroke-contrast callouts
  cnn_block.py             # Figure 2  (T1): conv → pool → FC block diagram (matplotlib patches)
  degradation_pipeline.py  # Figure 3  (T1): clean glyph → elastic warp → blur/noise → kerning jitter
  embedding_space.py       # Figure 4  (T2): 2D scatter — known-font clusters + open-set rejection boundary (seaborn)
  vit_attention.py         # Figure 5  (T3): patch embedding + self-attention heads schematic
  ssim_pipeline.py         # Figure 6  (T3): re-render predicted font → structural compare vs. crop
  system_pipeline.py       # Figure 7  (T4): end-to-end framework flowchart (graphviz)
```
- Every script imports `_style.py` and writes `assets/figures/<name>.png` at 300 dpi with consistent styling.
- Dependencies (`matplotlib`, `seaborn`, `graphviz`) install into the **root `.venv`** (already created). Note: the graphviz *Python* package needs the graphviz *system* binary on PATH for `system_pipeline.py`.
- Figure → batch → script mapping is 1:1; numbering matches in-text appearance order (Figures 1–7).

## Notes
-
