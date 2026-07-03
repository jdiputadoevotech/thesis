# Chapter 2 — Review of Related Literature (RRL)

- Related literature (foreign + local)
- Related studies / systems (font recognition, OCR, synthetic data, CNNs/ViTs)
- Synthesis / research gap
- Conceptual / theoretical framework

> Source table lives in [`../../literature/references.md`](../../literature/references.md).
> Cite each source here and tag the row's "Cited in" column with `Ch2`.

---

# 📐 MASTER RRL PLANNER (Chapter 2 blueprint — NOT the essay)

> 📄 **The essay itself is written to [`draft.md`](./draft.md)**, section by section. This file is the plan only.

**Goal:** 15–20 pp, publication-grade, defense-ready. Built in 5 thematic batches, written one batch at a time to protect quality.
**Narrative order (problem-first):** A → C → B₁ → B₂ → D — *legacy fails → the GenAI disease → our recognizer (reject + embed) → our validation.*
**Rule:** No fabricated metrics. Any empirical value not in a source row → bracket placeholder `[X.XX]`. Tag each used row's "Cited in" column with `Ch2`.

> ⚠️ The "Batch 1–5" labels in [`references.md`](../../literature/references.md) are *acquisition* clusters (how papers were gathered) — a **different** grouping from the A–D/B₁/B₂ *writing* batches below. Kept for traceability only.

## Batch map (all 30 rows, no overlap — 7+7+4+6+6 = 30)

| Batch | Theme | Rows | # | Pages |
|---|---|---|---|---|
| **A** | Legacy Font Recognition, OCR/Layout & Closed-Set Vector Assumptions | 21, 22, 25, 26, 27, 28, 30 | 7 | 3.5–4 |
| **C** | Generative AI Typographic Hallucinations & Diffusion Latent Mutations | 10, 11, 12, 13, 14, 15, 29 | 7 | 3.5–4 |
| **B₁** | Logit-Space Thresholds & Open-Set Rejection Scores | 1, 2, 4, 5 | 4 | 2.5–3 |
| **B₂** | Feature Disentanglement & Frozen-ViT Metric Embedding | 3, 6, 7, 8, 9, 23 | 6 | 3.5–4 |
| **D** | Advanced Visual Distance Metrics (SSIM) & Human-Proxy Ground-Truth Alignment | 16, 17, 18, 19, 20, 24 | 6 | 3.5–4 |

Batch bodies ≈ 16–19 pp; + chapter intro (~0.5) + cross-batch synthesis/gap (~1) + conceptual framework (~1) → **~18–21 pp total**.

---

## Batch A — Legacy baselines the thesis is defined against
- **Rows:** 30, 22, 26, 21, 25, 27, 28 · **Pages:** 3.5–4
- **Objective (gap defense):** Establish the closed-set, geometrically-rigid status quo so the gap is visible *by contrast*. Anchor on DeepFont (30) as the domain-defining font recognizer built on **clean** synthetic glyphs + Top-1/Top-3 — the exact protocol this thesis adopts but re-targets from pristine vectors to hallucinated crops. Classical OCR/layout excel on anatomically-correct text yet presuppose rigid glyph geometry (22 Tesseract [98%], 26 IEEE closed-boundary). The field's own migration off fixed CNN receptive fields toward attention-based localization (21 TransTab, 25 UnSupDLA) sets up the modern turn. Taxonomy + augmentation scaffolding (27 Sarker, 28 Plastropoulos) licenses the synthetic-degradation methodology.
- **Sub-clusters:** A.1 domain anchor — DeepFont (30) · A.2 classical OCR / geometric layout on clean text (22, 26) · A.3 attention-based localization bridge (21, 25) · A.4 taxonomy & augmentation rationale (27, 28)

```
/academic-research-skills:ars-lit-review Write Batch A of Chapter 2 (Review of Related Literature) — "Legacy Font
Recognition, OCR/Layout & Closed-Set Vector Assumptions." Use ONLY references [30,22,26,21,25,27,28]
from literature/references.md. Target 3.5–4 pages of dense, defense-grade synthesis in APA 7.0,
following sub-clusters A.1–A.4 in chapters/02-review-of-related-literature/notes.md. Frame every
source as the closed-set/rigid-glyph status quo the thesis inverts; open on DeepFont as the anchor
and close on the CNN→attention localization migration. Do NOT fabricate metrics; use bracket
placeholders like [X.XX] for any value not in the source row. Tag each cited row's "Cited in" column
with Ch2. Write the prose into section 2.2 of chapters/02-review-of-related-literature/draft.md.
```

---

## Batch C — The generative disease the recognizer must read
- **Rows:** 11, 10, 14, 12, 13, 29, 15 · **Pages:** 3.5–4
- **Objective (gap defense):** Prove typographic hallucination is **endemic, not anecdotal**, and characterize its mechanism and distribution — the input distribution this thesis owns. Scale: uncorrected SDXL renders text correctly "<20%" of the time (11 Glyph-ByT5), and even SOTA VLMs get lost reading fonts via a Stroop-style semantic interference (10). Mechanism: uncontrolled cross-character attention smears adjacent glyphs (14 TextPixs, supplying CER/WER) and multi-instance scenes entangle (12 TextCrafter + CVTG-2K stressor catalogue). Concentration & latent mutation: deformation is worst in the long tail (13 HDGlyph), and diffusion latent interpolation *natively* emits unclassified glyph geometries (29 Kondo = peer-reviewed proof). Evaluation frame: VTPBench/VTPScore (15).
- **Sub-clusters:** C.1 empirical scale (11, 10) · C.2 deformation mechanism (14, 12) · C.3 long-tail concentration + diffusion latent mutation (13, 29) · C.4 evaluation taxonomy (15)

```
/academic-research-skills:ars-lit-review Write Batch C of Chapter 2 (Review of Related Literature) — "Generative AI
Typographic Hallucinations & Diffusion Latent Mutations." Use ONLY references [11,10,14,12,13,29,15]
from literature/references.md. Target 3.5–4 pages of dense, defense-grade synthesis in APA 7.0,
following sub-clusters C.1–C.4 in chapters/02-review-of-related-literature/notes.md. Establish the
deformation as endemic (open on the <20% rendering figure), decompose its mechanism, locate it in the
long tail, and close on the evaluation taxonomy. Emphasize this literature studies deformation only
to SUPPRESS it inside the generator — never to trace deformed output back to a source typeface. Do
NOT fabricate metrics; use bracket placeholders like [X.XX]. Tag each cited row's "Cited in" with Ch2.
Write the prose into section 2.3 of chapters/02-review-of-related-literature/draft.md.
```

---

## Batch B₁ — Logit-space & open-set rejection scores
- **Rows:** 1, 2, 4, 5 · **Pages:** 2.5–3
- **Objective (gap defense):** Supply the **reject-the-unknown** machinery — how the model decides a hallucinated crop falls outside the trained font manifold. Energy-based rejection with boundary-outlier mining (1 Hopfield boosting); training-free, architecture-agnostic logit rescaling (2 LTS); the insight that the *ranking* of runner-up classes is the open-set signal — mapping directly onto Top-K font ordering as an anomaly cue (4 ExCeL); task-oriented survey that situates these post-hoc scores for training-agnostic deployment (5 Lu et al.). Gap: none is evaluated on *typographic* OOD (micro-warping, variable kerning).
- **Sub-clusters:** B₁.1 energy / logit rescaling scores (1, 2) · B₁.2 rank-based rejection + survey scaffold (4, 5)

```
/academic-research-skills:ars-lit-review Write Batch B1 of Chapter 2 (Review of Related Literature) — "Logit-Space Thresholds
& Open-Set Rejection Scores." Use ONLY references [1,2,4,5] from literature/references.md. Target
2.5–3 pages of dense, defense-grade synthesis in APA 7.0, following sub-clusters B1.1–B1.2 in
chapters/02-review-of-related-literature/notes.md. Frame these as the score-and-threshold machinery
that decides "unknown," and foreground ExCeL's runner-up-ranking signal as the precedent for reading
a Top-K font shortlist as an anomaly cue. State the gap: none is tested on typographic OOD. Do NOT
fabricate metrics; use bracket placeholders like [X.XX]. Tag each cited row's "Cited in" with Ch2.
Write the prose into section 2.4 of chapters/02-review-of-related-literature/draft.md.
```

---

## Batch B₂ — Feature disentanglement & frozen-ViT metric embedding
- **Rows:** 3, 6, 7, 8, 9, 23 · **Pages:** 3.5–4
- **Objective (gap defense):** Supply the **representation** the rejection score reads over — a clean, disentangled, layout-independent embedding. Non-negative contrastive learning yields sparse, axis-aligned features that separate known fonts from deformation artifacts (3 NCL); a frozen self-supervised ViT gives all-purpose fine-grained features with no fine-tuning (6 DINOv2); register tokens remove high-norm artifacts so thin-stroke glyph crops read cleanly (7); class-specific prompts localize discriminative traits — serif terminals, stroke contrast — regardless of the word rendered (8 Prompt-CAM); label-free prompt distillation transfers onto a localized palette without per-glyph labels (9 PromptKD); metric-topology clustering justifies mapping distorted inputs to continuous proximity rankings rather than hard buckets (23).
- **Sub-clusters:** B₂.1 disentangled features + frozen backbone (3, 6, 7) · B₂.2 trait localization, label-free distillation & metric topology (8, 9, 23)

```
/academic-research-skills:ars-lit-review Write Batch B2 of Chapter 2 (Review of Related Literature) — "Feature Disentanglement
& Frozen-ViT Metric Embedding." Use ONLY references [3,6,7,8,9,23] from literature/references.md.
Target 3.5–4 pages of dense, defense-grade synthesis in APA 7.0, following sub-clusters B2.1–B2.2 in
chapters/02-review-of-related-literature/notes.md. Frame these as the layout-independent embedding the
Batch B1 rejection score operates over; stress that all are validated on natural-image fine-grained or
CLEAN font benchmarks, never on probabilistically deformed glyphs. Do NOT fabricate metrics; use
bracket placeholders like [X.XX]. Tag each cited row's "Cited in" with Ch2.
Write the prose into section 2.5 of chapters/02-review-of-related-literature/draft.md.
```

---

## Batch D — Deformation-robust distance metrics + calibrated Top-K & human-proxy ground truth
- **Rows:** 16, 17, 24, 18, 19, 20 · **Pages:** 3.5–4
- **Objective (gap defense):** Supply the **measurement** layer — *how close is the predicted font to the crop* and *how trustworthy is the Top-K shortlist*. Distance side abandons the pixel-aligned assumption that breaks on warped glyphs: deep-feature SSIM with attention calibration (16 DeepSSIM), segmentation-embedding content-structure score (17 SAMScore), soft-computing structural-distance optimization (24). Uncertainty side turns Top-K into a *calibrated* set: label-rank-calibrated conformal prediction (18 RC3P) extended to the long tail where rare/display faces live (19). Typography-native precedent: L2@k / cos@k compare top-k classifier distributions over an open-world font set on this thesis's own Storia-AI baseline (20 ControlText).
- **⚠️ Human-proxy note (do NOT fabricate a citation):** No reference is specifically about human panels. The **3-person consensus panel is the thesis's OWN empirical ground truth** (Ch 3/4, per CLAUDE.md). Batch D frames it via the conformal-prediction ground-truth-calibration literature (18, 19) — the statistical scaffolding for judging a calibrated Top-K set against a human-established ground truth. Writer: cite 18/19 for the *calibration logic*, and refer to the human panel as *this study's methodology*, not a literature source.
- **Sub-clusters:** D.1 deformation-robust structural distance (16, 17, 24) · D.2 calibrated Top-K + font-fidelity + human-proxy alignment (18, 19, 20)

```
/academic-research-skills:ars-lit-review Write Batch D of Chapter 2 (Review of Related Literature) — "Advanced Visual Distance
Metrics (SSIM) & Human-Proxy Ground-Truth Alignment." Use ONLY references [16,17,24,18,19,20] from
literature/references.md. Target 3.5–4 pages of dense, defense-grade synthesis in APA 7.0, following
sub-clusters D.1–D.2 in chapters/02-review-of-related-literature/notes.md. Couple a deformation-robust
structural distance with a calibrated Top-K prediction set over a localized open-set Google-Fonts
palette. IMPORTANT: do NOT invent a human-proxy citation — frame the 3-person consensus panel as THIS
STUDY'S own ground-truth methodology, using refs 18/19 only for the calibration logic. Do NOT
fabricate metrics; use bracket placeholders like [X.XX]. Tag each cited row's "Cited in" with Ch2.
Write the prose into section 2.6 of chapters/02-review-of-related-literature/draft.md.
```

---

## After all 5 batches drafted — chapter-level connective tissue
- **Chapter intro (~0.5 pp):** frame the problem-first arc A→C→B₁→B₂→D.
- **Cross-batch synthesis + research gap (~1 pp):** none connects attention-based text isolation → deformation-robust metric embedding → open-set font-identity ranking on a localized Google-Fonts palette. (Reuse gap language from `references.md` batch syntheses.)
- **Conceptual / theoretical framework (~1 pp):** the reject-score (B₁) over disentangled frozen-ViT embedding (B₂), scored by typographic distance + calibrated Top-K (D), against the legacy protocol (A) on the GenAI-deformed input distribution (C).

## Notes
-

---

# ✂️ SHORTENING PASS (draft.md is written but 3× too long)

> This section plans the **compression** of the already-written `draft.md`. The MASTER RRL PLANNER above is the *original composition* blueprint, kept for traceability. This blueprint is the *reduction* blueprint.

**Problem:** `draft.md` = 18,279 words. At our format (12pt, **double-spaced, 1" margins all sides** ≈ 305 words/double-spaced page) that is **~60 pp** — the professor asked for **15–20 pp**.

**Target:** **~20 pp (upper end) ≈ ~6,000 words** — a ~67% cut. Keep as much scholarship as possible while landing inside 15–20 pp.

**Rules (locked with user):**
1. **Keep all 30 sources cited.** Group agreeing sources into citation clusters; never drop a source. `Cited in: Ch2` tags in `references.md` stay valid.
2. **Merge the 13 subsections** (2.2.1–2.6.2) into flowing per-section prose. Drop `### 2.x.y` sub-headings; keep `## 2.x` section headings + each section's bold **Research Gap** closer.
3. No new sources, no fabricated metrics. Keep `[X.XX]` placeholders as-is.

**What to cut (the fat, not the scholarship):**
- The repeated "*the implications for this thesis are…*" restatements — state each source's relevance **once**, at the point it's introduced.
- Worked micro-examples (Garamond/Old-Style runner-up walk-throughs, CIFAR FPR95 number dumps) → compress to a clause; keep the one load-bearing figure per source.
- Decorative numbers; keep only metrics doing argumentative work.
- Preserve the problem-first spine and each section's opening sentence linking back to the prior section.

## Per-section word budget

| § | Merge | Now | Target |
|---|---|---|---|
| 2.1 Introduction | — | ~600 | ~250 |
| 2.2 Legacy / OCR / closed-set | 2.2.1–2.2.4 | ~3,000 | ~850 |
| 2.3 Generative hallucination | 2.3.1–2.3.4 | ~2,800 | ~850 |
| 2.4 Open-set rejection | 2.4.1–2.4.2 | ~2,900 | ~800 |
| 2.5 Feature / frozen-ViT | 2.5.1–2.5.2 | ~2,900 | ~900 |
| 2.6 Distance / measurement | 2.6.1–2.6.2 | ~3,000 | ~900 |
| 2.7 Synthesis & gap | — | ~900 | ~450 |
| 2.8 Conceptual framework | — | ~1,200 | ~500 |
| **Total** | | **~18,300** | **~5,500** (buffer to ~6,000) |

## CLAUDE.md checklist — run on EVERY batch (see `./CLAUDE.md`)
- [ ] Synthesis, not study-by-study listing (merging *helps* — group sources per claim).
- [ ] Both **agreement AND contrast** shown (keep the "however / by contrast" turn).
- [ ] Section **ends with an explicit research gap**.
- [ ] All in-text APA citations valid + still present in `literature/references.md`.
- [ ] No source silently dropped (cross-check the batch's citation list below).

## Batch execution prompts

**Batch S1 — §2.2** (merge 2.2.1–2.2.4 → ~850w). Must retain: Wang et al. (2015) DeepFont; Ponnuru et al. (2024); Bhunia et al. (2018); Wang, Lv, et al. (2025) TransTab; Sheikh et al. (2024) UnSupDLA; Sarker (2021); Plastropoulos & Tegos (2024). Keep the closed-set/rigid-glyph → attention-migration arc; open on DeepFont, close on the gap.

**Batch S2 — §2.3** (merge 2.3.1–2.3.4 → ~850w). Must retain: Liu et al. (2024) Glyph-ByT5 (<20% figure); Li, Song, et al. (2025) Stroop; Gillani et al. (2025) TextPixs (CER/WER); Du et al. (2025) TextCrafter + CVTG-2K; Zhuang et al. (2025) HDGlyph long-tail; Kondo et al. (2024) latent interpolation; Shu et al. (2025) VTPBench/VTPScore. Keep "studied only to SUPPRESS, never to read back" as the gap.

**Batch S3 — §2.4** (merge 2.4.1–2.4.2 → ~800w). Must retain: Hofmann et al. (2024) EHB; Djurisic et al. (2024) LTS; Karunanayake et al. (2025) ExCeL (runner-up-ranking = Top-K anomaly precedent); Lu et al. (2025) survey. Gap: none tested on typographic OOD.

**Batch S4 — §2.5** (merge 2.5.1–2.5.2 → ~900w). Must retain: Wang et al. (2024) NCL; Oquab et al. (2024) DINOv2; Darcet et al. (2024) registers; Chowdhury et al. (2025) Prompt-CAM; Li, Li, et al. (2024) PromptKD; Huang & Zhou (2022) metric topology. Gap: validated on clean/natural-image, never deformed glyphs.

**Batch S5 — §2.6** (merge 2.6.1–2.6.2 → ~900w). Must retain: Wang et al. (2004) classical SSIM; Zhang et al. (2024) DeepSSIM; Li et al. (2025) SAMScore; Umer et al. (2022); Shi et al. (2024) RC3P; Ding et al. (2025) long-tail conformal; Jiang et al. (2025) ControlText L2@k/cos@k + Storia-AI. ⚠️ Human-proxy panel = THIS STUDY's own methodology, not a cited source (refs 18/19 only for calibration logic).

**Batch S6 — §2.1 + §2.7 + §2.8** (connective tissue → ~250 / ~450 / ~500w). Keep the A→C→B₁→B₂→D framing (2.1), the "seams between mature clusters" gap (2.7), and the four-layer pipeline framework (2.8). These reference sources already cited elsewhere — no new citations.

## Verification (after each batch + at end)
```powershell
$f="chapters/02-review-of-related-literature/draft.md"
$wc=((Get-Content $f -Raw) -split '\s+' | ? {$_ -ne ''}).Count
"words=$wc  ~pp=$([math]::Round($wc/305,1))"
```
Final gate: **≤ ~6,100 words (≤20pp)**, not below ~4,600 (≥15pp). Grep `^### ` = no orphan sub-headings; grep `^\*\*Research Gap` = one per theme section.
