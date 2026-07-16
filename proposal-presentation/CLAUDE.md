# PROPOSAL PRESENTATION — FOLDER INSTRUCTIONS

Defense deck + supporting materials for the thesis proposal presentation.
**Not a chapter.** Draws from `chapters/` prose but lives separate — this is the
oral-defense deliverable, not thesis text.

> ⚠️ **ALWAYS reference `requirements.md` first** before drafting or editing any
> slide, script, or deliverable in this folder. It is the authoritative spec —
> slide structure, time budget (30/40/20), rubric weights, presentation flow, and
> the required content of every section all live there. Keep all work aligned to it.

## 🎯 Thesis
**"Addressing Typographic Hallucination in Generative AI Images: An Open-Set
Metric Learning Approach to Font Style Recognition"**

## 📂 Layout
- `requirements.md` — advisor/panel rubric, deadline, format specs, slide count limits.
- `slides/` — the deck (pptx / pdf / Google Slides link). Exported figures from `assets/figures/`.
- `script.md` — speaker notes, talking points, per-slide timing, anticipated Q&A.
- `CLAUDE.md` — this file.

## 🔗 Source material (pull from, don't duplicate)
- Problem/objectives → `chapters/01-introduction/`
- Related lit → `chapters/02-review-of-related-literature/draft.md`
- Technical background + 7 figures → `chapters/03-technical-background/draft.md`, `assets/figures/`
- Methodology (pipeline, metrics, Gantt) → `chapters/04-methodology/`
- Timeline → `plans/plans.md`

## 📏 Slide word budget (speaker-driven deck)
Slides are cue cards, not the script — the talk track lives in the Marp `<!-- notes -->`.
Keep every slide inside these caps or it overflows the frame (spills into the footer/logo):

- **Title (`##`):** ≤ 8 words.
- **Body total:** **≤ 45 words** per slide (hard cap ~55). Aim for 30–40.
- **Bullets:** ≤ 5 top-level; **≤ 2 lines each** on screen. Avoid sub-bullets — collapse
  related points into one line with commas (e.g. the three "tools fail" stats on one bullet).
- **One idea per slide.** If it needs > 45 words, split it or push detail to the speaker notes.
- Citations are `*(Author, Year)*` inline — they count toward the word budget, so keep them short.

Rule of thumb: if a slide can't be read aloud in ~40 seconds, it's too full.

## ⚠️ Rules
1. Reuse existing figures from `assets/figures/` — don't regenerate for slides.
2. No fabricated results. Bracketed `[X.XX%]`/`[N]` only for values no run/decision has produced
   yet (see main `CLAUDE.md` rule 3); use real values where the drafts already have them.
3. Keep deck content in sync with chapter drafts — chapters are source of truth.
