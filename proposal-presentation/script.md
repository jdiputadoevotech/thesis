# Proposal Presentation — Speaker Script & Q&A Prep

> **Per-slide talk track lives inline** in `slides/slides.md` as Marp `<!-- speaker notes -->`
> comments (they export to PowerPoint presenter notes). This file holds the **Q&A prep** —
> the 40-minute stress-test is worth more rehearsal than the 30-minute deck.
> Scope here: **Sections 1–3** (partner owns Section 4 Q&A).

## Timing
- 30 min presentation · 40 min Q&A · 20 min deliberation (see `requirements.md`)
- Sections 1–3 ≈ 9 content slides ≈ **10–12 min**; leave the rest for the partner's Section 4.

---

## Anticipated Q&A — Sections 1–3

### On the internship origin (S1b)
- **Q: Is this just an internal tool for your employer?**
  A: The internship is where we *found* the problem, but the contribution is general and
  open-source — any designer reusing generative typography hits the same wall. Our pipeline is
  concrete proof the problem is real and that font identity is the missing link, not the scope
  limit. (Show the pipeline screenshot.)

- **Q: You already built an AI→.psd pipeline — what's left to research?**
  A: Everything except font identity is solved in that pipeline. The unsolved step is exactly
  this thesis: recovering the true font from a deformed, prompted-but-wrong glyph, open-set over
  a localized palette. That step has no working tool (see Sections 2–3).

### On the problem framing
- **Q: Isn't this just WhatTheFont for AI images?**
  A: No. WhatTheFont-class tools are closed-set and assume an intact glyph — they *cannot say
  "unknown"* and collapse on deformed input. Our contribution is (a) reading a **deformed** glyph and
  (b) **open-set rejection**. Neither exists in commercial identifiers.

- **Q: Why not just fix the text inside the generator instead?**
  A: That is a different problem (generation), and it is the generator vendor's to solve. We take the
  hallucinated output as an *inevitable input distribution* (Liu et al., 2024 show <20% accuracy is
  the default state) and recover font identity from it — useful for any image already made.

- **Q: The <20% figure — is that still current?**
  A: It is Liu et al. (2024), Glyph-ByT5, on uncorrected SDXL. It is the anchor stat, verified in
  `literature/references.md` (row 11). Glyph-aware correction raises it to ~90%, but uncorrected
  output — what a designer actually receives — stays broken.

### On scope
- **Q: Why only 50–100 Google Fonts, not the full catalogue?**
  A: A localized palette is what makes **open-set rejection tractable** and template reconstruction
  **license-clear** (Google Fonts are free). Scaling the catalogue is proven *not* to help — Jiang et
  al. (2025) show a 3,474-font classifier still overfits pristine glyphs. Breadth is not the bottleneck;
  deformation-robustness is.

- **Q: How do you validate your synthetic degradation matches real hallucination?**
  A: Two ways. (1) The degradation operator (elastic warp, blur/noise, kerning jitter) is built to
  reproduce *documented* mechanisms — attention bleed (Gillani et al., 2025) and latent-manifold
  interpolation (Kondo et al., 2024). (2) Final evaluation is on a **3-person human-proxy panel judging
  real generative crops**, not just synthetic data — so the ground truth is real hallucination.

- **Q: What is the "unknown" verdict — isn't that just the model failing?**
  A: It is a deliberate open-set feature (Lu et al., 2025). A hallucinated glyph often belongs to *no*
  catalogued font; forcing a match would be wrong. Correctly saying "unknown" is a success, and we
  measure it explicitly.

### On the gap / novelty
- **Q: Each piece already exists — what's actually new?**
  A: The **seam**. No prior work connects attention-based text isolation → deformation-robust metric
  embedding → open-set font-identity ranking on a localized palette. Every cited field solves one link
  and leaves the same blind spot: they assume a clean glyph exists.

- **Q: Chen et al. (2026) already do frozen-ViT font classification — how are you different?**
  A: They are the closest antecedent and our baseline, but explicitly **closed-set, trained on pristine
  renders**; by their own report family accuracy collapses to 40.2% on non-synthetic input. We target
  exactly that failure regime with open-set rejection.

### On feasibility (expect this from a technical panelist)
- **Q: Why frozen DINOv2 instead of fine-tuning?**
  A: A frozen, register-corrected backbone (Oquab et al., 2024; Darcet et al., 2024) gives clean,
  general patch features without overfitting to synthetic deformation — we learn the *metric*, not the
  features. [Confirm compute/timeline detail with Section 4.]

---

## Delivery reminders
- Read the **central question** (S4) and the **blind spot** (S6) verbatim and slowly — they are the spine.
- Gold Standard Rule (`requirements.md`): take panel feedback **gratefully**. Coachability > a perfect deck.
- Placeholders on title slide (`[JD]`, `[MC]`, adviser, date) — fill before export.
