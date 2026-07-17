# Chapter 1 — Introduction: Writing Rules

Folder-local rules for drafting/grading `draft.md`. Distilled from the professor's Chapter 1 guide (see `notes.md`). These govern **this chapter only**; the root `CLAUDE.md` and thesis title/core-idea still apply.

## Prime directive
Take the reader from a **broad real-world problem → the specific algorithmic solution** we propose. Every section must move down that funnel. If a paragraph doesn't advance the funnel, cut it.

## No repetition across sections
Each fact, stat, and framing gets **one home section**; later sections reference it, they do not restate it. The reader should never meet the same sentence twice.
- **Stats have one home.** A number (SDXL <20%, 3,474-font baseline, 40.2% family-level collapse, OCR ~98%, Stroop-effect VLM failure, etc.) is stated once — in **Background** — with its citation. Later sections invoke the conclusion without re-quoting the figure.
- **Introduction vs Background** is the main overlap risk now that the two are separate sections. Introduction = broad framing, why it matters today, and the *definitions* of key concepts. Background = the *evolution*, frameworks, and *why* the failure happens (mechanism, why catalogue-scaling fails) — this is where the stats live. Do not define a concept in both, and do not carry the stats up into the Introduction.
- **Definitions live in the Introduction.** Introduce each key concept on first use with a short operational gloss (typographic hallucination, open-set recognition, metric learning); do not re-define it in full elsewhere. Deep technical treatment is deferred to Ch3.
- **Statement of the Problem** names the gap in one line; it does not re-walk the Background mechanism. **Research Questions** are their own section (after Objectives) — do not pre-list them inside the Statement of the Problem.
- Recurring anchors (typographic hallucination, the 50–100 Google Fonts palette, the metrics) may be *named* in several sections, but the full explanation appears once.

## Required sections (in order)
1. **Introduction** — broad overview of the field; why it matters today; definitions of key concepts.
2. **Background** — evolution/milestones of font recognition, frameworks, and *why* it fails on hallucinated GenAI text. Home for the stats.
3. **Statement of the Problem** — the one-sentence gap + general framing.
4. **Objectives of the Study** — one general, several specific.
5. **Research Questions** — own section, placed **after** Objectives.
6. **Scope and Limitations.**
7. **Significance of the Study.**

## Per-section rules

### Introduction
- Open broad: generative AI image tools entering the design/typography workflow, and why naming the font matters today.
- Define key concepts on first use with a short **operational gloss** (typographic hallucination, open-set recognition, metric learning) — this is now the definitions home; defer deep treatment to Ch3.
- Banned: clichés and empty openers ("Since the dawn of time…", "In today's fast-paced world…").
- Keep the stats out — they live in Background. Introduction frames; Background evidences.

### Background
- Narrow from the field to the specific failure: the evolution of font recognition (classical DeepFont/OCR → catalogue-scaling → frozen-ViT baselines), the frameworks involved, and *why* each fails on hallucinated GenAI text.
- **Home for the stats.** Ground claims in **current stats or foundational papers** — cite from `literature/references.md`, tag its "Cited in" column `Ch1`. Each number stated once here (SDXL <20%, 3,474-font baseline, 40.2% family collapse, OCR ~98%, Stroop-effect VLM failure).

### Statement of the Problem
- One-sentence gap: what current tools (WhatTheFont, closed identifiers) fail to do on hallucinated GenAI text.
- Do **not** re-walk the Background mechanism, and do **not** list the research questions here — they are their own section after Objectives.

### Objectives
- **General** = broad aim, mirrors the thesis title. Harder to measure directly. One sentence.
- **Specific** = narrow, actionable, **measurable** tasks that decompose the general objective. Each should trace to a research question and an evaluation metric (Top-K accuracy, SSIM/MSE, confusion matrix, human proxy).
- Verb test: specific objectives start with measurable verbs (build, synthesize, train, compare, evaluate) — not vague ones (explore, understand).

### Research Questions
- Own section, placed **after** Objectives (professor's order).
- Numbered specific questions. Each must map to an objective and, later, a results section.

### Scope and Limitations
- **Scope (included):** the 50–100 Google Fonts palette, synthetic degradation pipeline, PyTorch/ViT/DINOv2 stack, the exact metrics evaluated, the web-app deployment.
- **Boundaries that limit reach (each with a reason):** recognition targets a localized open-source palette, not the full commercial 3,474-font space (goal is free, license-clear reconstruction); text-crop recognition only, not full-page layout; discrete font identity, not continuous variable-font axes; Latin-script only.
- **Real-world limitations (honest constraints):** training relies on synthetically degraded crops, so a residual synthetic-to-real domain gap constrains transfer to unseen generators; compute budget may cap epochs. Since this section is titled "Scope and Limitations," these belong here.

### Significance
Break down by stakeholder — no generic "this helps society":
- **Field (CS / ML):** methodological contribution (open-set metric-learning approach to deformation-robust font ID).
- **Practitioners (designers / GenAI users):** free template reconstruction, no commercial license lock-in.
- **Future researchers:** building block for deformation-robust recognition beyond fonts.

## Limitations vs Delimitations (do not confuse)
| | Delimitation | Limitation |
|---|---|---|
| Who decided | We did | Reality / environment |
| Set when | Before research | Found during/after |
| Phrase | "This study focuses exclusively on…" | "Due to constraints in [X], this study could not…" |

Our chapter's section is titled **"Scope and Limitations"**, so real-world limitations (out of our control — e.g. compute budget capping epochs, synthetic-vs-real domain gap) belong there, acknowledged honestly. The table above is kept only to keep the distinction clear: state chosen boundaries and real constraints separately, and do not dress a real limitation up as a chosen boundary. Honesty ≠ weakness — it shows rigor.

## Data / integrity
- No fabricated numbers. Real values only; unmeasured values use the `[X.XX%]`/`[N]` placeholder (root rule #3).
- Literature stats come from `literature/references.md` (single source of truth). Verify before citing.

## Page format
A4, 1-inch margins on all sides except the left (1.5 inches), double-spaced, 12pt → **~250 words/page**. Convert any page target to a word budget before drafting.

## Notes-vs-draft
`notes.md` = planning + the professor's guide. `draft.md` = the actual chapter prose. Never write essay prose into `notes.md`; never leave planning scaffolding in `draft.md`.
