# THESIS SYSTEM INSTRUCTIONS: CLAUDE.md

## 🎯 Final Thesis Title
**"Addressing Typographic Hallucination in Generative AI Images: An Open-Set Metric Learning Approach to Font Style Recognition"**

## 🏁 The Master Core Idea
Generative AI tools (DALL-E, Midjourney) introduce "Typographic Hallucinations"—probabilistic glyph deformations, micro-warping, and variable kerning artifacts that cause commercial font identifiers (WhatTheFont) to fail. 

Our framework addresses this academic research gap. Instead of mapping vector shapes to expensive commercial licenses using a closed black box, this system uses a deep-learning-based feature metric pipeline to map hallucinated text crops directly to a localized, open-source palette of the **top 50–100 Google Fonts** to enable seamless, free template reconstruction.

---

## 📂 Repository File Structure

When navigating, reading, or creating content, strictly adhere to the following workspace schema:

- **`assets/`**: Images, figures, data visualizations, and comparative charts. See `assets/README.md`.
- **`chapters/`**: The core academic text composition root. Each chapter folder holds **two file kinds** (see the notes-vs-draft convention below):
  - `01-introduction/` — `notes.md`: Context, Problem Statement, Objectives.
  - `02-review-of-related-literature/` — `notes.md` (Master RRL Planner blueprint) + `draft.md` (the actual publication-grade chapter prose, ~15–20 pp, **written**).
  - `03-technical-background/` — `notes.md`: Foundational concepts (typography, CNNs, metric learning, ViT/DINO, open-set recognition, SSIM) preceding the methodology.
  - `04-methodology/` — `notes.md`: Synthetic pipeline design, training metrics, evaluation logic.
  - `05-results-and-discussion/` — `notes.md`: Comparative charts vs. human proxy & baseline.
  - `06-summary-conclusions-recommendations/` — `notes.md`: Final conclusions and future horizons.
- **`data_creation/`** *(Gitignored Sandbox — NOT in a fresh clone)*: The old, standalone synthetic data generator repository. Reference its scripts for asset production logic.
- **`font-classify/`** *(Gitignored Sandbox — NOT in a fresh clone)*: The cloned Storia-AI repository (Google Font Classifier, 3,474 fonts). Use this exclusively as our comparative testing baseline — it is also the field's reference embedding cited in the RRL (see references row 20). We acknowledge its pre-trained weights fail "in the wild" on actual GenAI text deformations due to pristine over-fitting.

> ⚠️ **Public repo:** this is now a public repository. `data_creation/` and `font-classify/` are separate git repos gitignored here, so they are **absent from a fresh clone** (a collaborator won't see them). Never assume their files exist when running in a clean checkout; treat their contents as documented-but-external. Do not commit secrets, credentials, or private data into this workspace.
- **`ideas/ideas.md`**: Brain dumps, technical tangents, and rough architectural notes.
- **`literature/references.md`**: Formal reference catalog — one row per source in a Markdown table (`# | Author(s) | Year | Title | Link | Key takeaways | Cited in`). Currently ~30 verified sources.
- **`literature/papers/`**: Local PDF store for source papers.
- **`plans/plans.md`**: Active project timeline milestones, tasks, and task delegation.

### 📝 Notes-vs-Draft convention (IMPORTANT)
- **`notes.md`** = planning artifact only: outlines, batch blueprints, evidence maps, execution prompts. **Never the essay.**
- **`draft.md`** = the actual chapter prose, written section by section into numbered sections (e.g. `2.2`, `2.5`).
- Keep planning and prose strictly separated. Do not write essay prose into `notes.md`, and do not leave planning scaffolding (batch labels, write-order comments, internal tracking) inside `draft.md`.

### 🔖 Citation workflow
- `literature/references.md` is the single source of truth for sources. Add/verify the row there **first**, then cite in the chapter draft.
- After citing a source, tag that row's **"Cited in"** column (e.g. `Ch2`).
- Chapter 2 was built with the **academic-research-skills** plugin (`/ars-lit-review`); its 5-batch writing strategy (A→C→B₁→B₂→D) is documented in `chapters/02-review-of-related-literature/notes.md`. Note: the "Batch 1–5" labels in `references.md` are *acquisition* clusters — a different grouping from the A–D *writing* batches.

---

## 🛠️ Data Strategy & Metrics Guide

### 1. The Synthetic Data Pipeline (To be refined in `data_creation/`)
- **Pristine Controls:** Render clean monochrome words using the targeted 50–100 Google Fonts.
- **Algorithmic Degradation:** Systematically apply elastic transformations (warping), Gaussian blur/noise, edge compression, and randomized character tracking to programmatically mimic probabilistic glyph hallucinations.

### 2. Validation Metrics (To be built into `src/` and evaluated in `chapters/04-*`)
- **Top-K Accuracy:** Log Top-1 and Top-3 accuracy profiles.
- **Typographic Distance (SSIM/MSE):** Re-render the predicted match and evaluate the Structural Similarity Index against the input crop to mathematically score visual proximity.
- **Confusion Matrix:** Map errors by typographic structural traits (Serif, Sans-Serif, Display, Monospace) to prove errors linger within identical aesthetic families.
- **Human Proxy Baseline:** Benchmark against a 3-person consensus panel evaluating 100 actual GenAI image text boxes to establish ground truth.

---

## ⚠️ Claude Code Operation Guidelines
1. **Context Management:** Keep text drafting constrained to the respective chapter folders. Do not ingest heavy video or image binaries from `assets/` into the LLM context pool unless explicitly requested.
2. **Read-Only Code Repos:** Treat `data_creation/` and `font-classify/` as independent sandboxes. Analyze their functionality to write the academic text, but do not directly commit new core application logic inside them through this main thesis workspace unless instructed.
3. **No Fabricated Data:** When writing drafts within `chapters/`, flag metrics or values that require empirical training runs using bracket placeholders like `[X.XX%]`. Never hallucinate experimental results.