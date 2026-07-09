# Chapter 1: Introduction

## 1.2 Statement of the Problem and Objectives

### 1.2.1 Statement of the Problem

Generative AI image tools such as Google's Gemini "Nano Banana", OpenAI's GPT Image, and Midjourney now produce marketing graphics, mockups, and social media assets in seconds, but the text they render is typographically unreliable. These models treat a character string as a semantic unit and lack the sub-character spatial control needed for accurate letterforms, so fewer than 20% of uncorrected renderings from a system like Stable Diffusion XL are typographically accurate (Liu et al., 2024). The failure is not random noise on otherwise correct letters. During denoising, a character's attention map bleeds into its neighbors, which warps strokes, distorts spacing, and merges adjacent glyphs (Gillani et al., 2025); and because diffusion models encode font style as a position on a continuous latent manifold rather than a discrete catalogue, they emit intermediate glyphs that match no named typeface (Kondo et al., 2024). This study terms the resulting probabilistic glyph deformation *typographic hallucination*, and it falls hardest on the display and script faces a designer is most likely to have chosen for visual effect (Zhuang et al., 2025).

For a designer who wants to reuse the typography of a generative image, this deformation breaks the tools that would normally name the font. Commercial identifiers, and the classical recognition paradigm they descend from, were trained on clean synthetic specimens and assume every input contains a geometrically intact glyph to recover (Wang et al., 2015). That assumption holds for a scanned document but not for a hallucinated crop, where signal and noise emerge together from the same generative process. Scaling the catalogue does not fix it: the largest open reference classifier, covering 3,474 Google Fonts, still overfits pristine glyphs (Jiang et al., 2025), and even the current frozen Vision Transformer state of the art collapses on non-synthetic input by its authors' own report, with family-level accuracy falling to 40.2% (Chen et al., 2026). General-purpose vision-language models are no escape either, because the lexical meaning of the rendered word overrides their reading of its visual form (Li, Song, et al., 2025). Two capabilities are missing at once. No available system reads font identity from a deformed rather than pristine glyph, and none can refuse to answer when the glyph belongs to no catalogued font, which is the normal case for a hallucinated crop and the situation open-set recognition exists to handle (Lu et al., 2025). The practical result is that free, license-clear reconstruction of generative typography has no working tool, and designers are pushed back toward paid identifiers that fail on the very inputs at issue.

This study addresses that gap. The central question it asks is: **how can the typeface of hallucinated text in a generative-AI image be identified against a localized, open-source font palette when the glyph is probabilistically deformed and may belong to no font in the palette?** This general question resolves into five specific questions:

1. How can a synthetic dataset reproduce the typographic hallucination of generative models faithfully enough to train a deformation-robust recognizer?
2. Can a metric embedding built on a frozen self-supervised Vision Transformer separate typographic identity from deformation, so that a hallucinated crop lands near its source font?
3. Can an open-set rejection mechanism reliably route an out-of-palette or hallucinated glyph to an "unknown" verdict instead of forcing a match?
4. How accurately does the system rank the correct font in a Top-K shortlist, and how does that accuracy compare against existing closed-set baselines and a human-proxy panel?
5. Does the system's error distribution stay within typographic families, so that its mistakes remain visually close to the correct font?

### 1.2.2 General Objective

The general objective of this study is to design, build, and evaluate an open-set metric-learning system that identifies the typeface of hallucinated text in generative-AI images, mapping a deformed text crop to a ranked shortlist of the closest fonts in a localized palette of the top 50 to 100 Google Fonts, or to an "unknown" verdict when no palette font applies.

### 1.2.3 Specific Objectives

Specifically, the study aims to:

1. Curate a localized open-set palette of the top 50 to 100 Google Fonts across the serif, sans-serif, display, and monospace classes, and build a synthetic data pipeline that renders pristine word crops and degrades them with a controlled operator (elastic warp, blur and noise, and kerning jitter) that reproduces documented generative deformation (Gillani et al., 2025; Kondo et al., 2024).
2. Train a deformation-robust metric embedding on a frozen, register-corrected DINOv2 backbone (Oquab et al., 2024), so that geometric distance in the embedding encodes typographic similarity rather than deformation artifacts.
3. Implement an open-set decision that rejects out-of-palette glyphs through a post-hoc rejection score and produces a calibrated Top-K shortlist over the palette (Lu et al., 2025).
4. Verify each prediction with a re-render-and-compare typographic distance that is robust to geometric misalignment (Zhang et al., 2024), and analyze the system's errors by typographic family and by embedding-distance severity.
5. Evaluate the system under the Top-1 and Top-3 accuracy protocol against the Storia-AI and DINOv2-LoRA closed-set baselines (Chen et al., 2026; Jiang et al., 2025) and against a three-person human-proxy consensus panel on real generative crops.
6. Deploy the trained model behind a web application, so the system can be tested interactively and in real time on uploaded generative-AI images.
