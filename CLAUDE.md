# THESIS SYSTEM INSTRUCTIONS: CLAUDE.md

## 🎯 Final Thesis Title
**"Addressing Typographic Hallucination in Generative AI Images: An Open-Set Metric Learning Approach to Font Style Recognition"**

## 🏁 The Master Core Idea
Generative AI tools (DALL-E, Midjourney) introduce "Typographic Hallucinations"—probabilistic glyph deformations, micro-warping, and variable kerning artifacts that cause commercial font identifiers (WhatTheFont) to fail. 

Our framework addresses this academic research gap. Instead of mapping vector shapes to expensive commercial licenses using a closed black box, this system uses a deep-learning-based feature metric pipeline to map hallucinated text crops directly to a localized, open-source palette of the **top 50–100 Google Fonts** to enable seamless, free template reconstruction.

---

## 📂 Repository File Structure (Mapped from image_49f437.png)

When navigating, reading, or creating content, strictly adhere to the following workspace schema:

- **`assets/`**: Images, figures, data visualizations, and comparative charts.
- **`chapters/`**: The core academic text composition root.
  - `01-introduction/notes.md` - Context, Problem Statement, Objectives.
  - `02-review-of-related-literature/notes.md` - Synthesized SOTA, theoretical frameworks.
  - `03-methodology/notes.md` - Synthetic pipeline design, training metrics, evaluation logic.
  - `04-results-and-discussion/notes.md` - Comparative charts vs. human proxy & baseline.
  - `05-summary-conclusions-recommendations/` - Final conclusions and future horizons.
- **`data_creation/`** *(Gitignored Sandbox)*: The old, standalone synthetic data generator repository. Reference its scripts for asset production logic.
- **`font-classify/`** *(Gitignored Sandbox)*: The cloned Storia-AI repository. Use this exclusively as our comparative testing baseline. We acknowledge its pre-trained weights fail "in the wild" on actual GenAI text deformations due to pristine over-fitting.
- **`ideas/ideas.md`**: Brain dumps, technical tangents, and rough architectural notes.
- **`literature/references.md`**: Formal reference citation catalog, verified paper DOIs, and annotated bibliographies.
- **`plans/plans.md`**: Active project timeline milestones, tasks, and task delegation.

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