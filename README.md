# Addressing Typographic Hallucination in Generative AI Images

**An Open-Set Metric Learning Approach to Font Style Recognition**

Undergraduate thesis workspace. This repository holds the **written thesis** (chapter drafts,
literature catalog, plans, figures). The two code repositories are maintained separately (see
[Code repositories](#code-repositories) below).

## The idea in one paragraph
Generative AI tools (DALL·E, Midjourney) introduce *typographic hallucinations* — probabilistic
glyph deformations, micro-warping, and variable kerning that cause commercial font identifiers
(e.g. WhatTheFont) to fail. Instead of mapping vector shapes to expensive commercial licenses via
a closed black box, this framework uses a deep-learning feature-metric pipeline to map hallucinated
text crops directly to a localized, open-source palette of the **top 50–100 Google Fonts**, enabling
free template reconstruction.

## Layout
| Path | What's here |
|------|-------------|
| `chapters/` | The thesis text, one folder per chapter (PH 5-chapter structure). See the notes/draft convention below. |
| `literature/references.md` | Running source catalog — one row per source (~30 verified). `Cited in` column tracks usage. |
| `literature/papers/` | Local PDFs of source papers. |
| `ideas/ideas.md` | Idea inbox, newest on top. |
| `plans/plans.md` | Task/experiment plans + status. |
| `assets/` | Figures, diagrams, comparative charts. |

### Chapters (PH 5-chapter)
1. Introduction — The Problem and Its Background
2. Review of Related Literature (RRL) — *drafted (~15–20 pp)*
3. Methodology
4. Results and Discussion
5. Summary, Conclusions, and Recommendations

### notes.md vs draft.md
Each chapter folder holds up to two kinds of file:
- **`notes.md`** — planning only: outlines, blueprints, evidence maps. *Not the essay.*
- **`draft.md`** — the actual chapter prose, written into numbered sections (e.g. `2.2`, `2.5`).

Keep the two separate: no essay prose in `notes.md`, no planning scaffolding in `draft.md`.

## How to use
- New source to cite → add a row in `literature/references.md`, then tag its `Cited in` column.
- Random idea → top of `ideas/ideas.md`.
- Planning an experiment/task → `plans/plans.md`.
- Drafting a chapter → write prose in that chapter's `draft.md` (plan first in `notes.md`).

## Code repositories
These are **independent git repositories, not included in this repo** (they carry their own history
and large data/model artifacts):
- **`data_creation`** — synthetic dataset generator: renders clean Google-Font words, then applies
  algorithmic degradation (elastic warping, blur/noise, edge compression, randomized tracking) to
  mimic glyph hallucination.
- **`font-classify`** — the comparative baseline (Storia-AI Google Font Classifier, 3,474 fonts).

> Partners/collaborators: clone these alongside this repo as sibling folders `data_creation/` and
> `font-classify/` to reproduce the pipeline. Ask the maintainer for access links.

---
*Writing/output format (Markdown → LaTeX/Word) not finalized; drafts currently live as Markdown.*
