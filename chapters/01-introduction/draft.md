# Chapter 1: Introduction

## 1.1 Introduction

Typography is a deliberate design decision. The typeface on a poster, a product mockup, or a social media graphic carries brand identity and tone as much as the words themselves, and a designer who selects a face is choosing a specific, nameable artifact from a catalogue of thousands. Generative AI image tools now enter this workflow directly: systems such as Google's Gemini "Nano Banana", OpenAI's GPT Image, and Midjourney produce finished graphics complete with rendered text in seconds. When a designer wants to adopt or extend the typography of such an image, the first task is to name the font. That single step is where the current generation of tools breaks down.

Three concepts frame the solution this study pursues. The first is the problem itself. This study uses *typographic hallucination* to name the probabilistic glyph deformation that generative models introduce when rendering text: micro-warping of strokes, distorted spacing, and merged or invented letterforms. The second is *open-set recognition*, the requirement that a recognizer rank the closest known fonts and also return an "unknown" verdict when the glyph belongs to no font in its catalogue, as a hallucinated crop often will. The third is *metric learning*: rather than training a fixed classifier over a closed list of fonts, the model learns an embedding in which geometric distance encodes typographic similarity, so that a deformed crop lands near its source font. This chapter introduces these concepts only as far as the problem requires, deferring their technical treatment to Chapter 3.

## 1.2 Background of the Study

Typographic hallucination is a structured failure, not random noise. Generative models render text unreliably because they treat a character string as a semantic token rather than a set of glyphs under sub-character spatial control; uncorrected renderings from a system like Stable Diffusion XL are typographically accurate in fewer than 20% of cases on a design benchmark (Liu et al., 2024). During denoising a character's attention map smears into its neighbors, warping strokes and destabilizing spacing (Gillani et al., 2025), and because diffusion models encode style as a position on a continuous latent manifold rather than a discrete list of named faces, they emit intermediate glyphs that correspond to no real typeface (Kondo et al., 2024). The distortion is worst on the rare and display letterforms in the long tail of usage (Zhuang et al., 2025), precisely the expressive faces a designer is most likely to have chosen.

Font recognition as a field was never built for this input. The classical paradigm, exemplified by DeepFont, learns from clean synthetic specimens and assumes every input contains a geometrically intact glyph to recover (Wang et al., 2015); traditional optical character recognition reaches roughly 98% accuracy on standard document scans for the same reason (Ponnuru et al., 2024). A hallucinated crop violates that assumption, because its signal and its noise are produced together by one generative process. Enlarging the reference catalogue does not resolve the problem: the largest open classifier covers 3,474 Google Fonts yet still overfits pristine glyphs (Jiang et al., 2025), and even a modern frozen Vision Transformer baseline collapses to 40.2% family-level accuracy on non-synthetic input by its authors' own report (Chen et al., 2026). General-purpose vision-language models fare no better, as the lexical meaning of the rendered word overrides their reading of its visual form (Li, Song, et al., 2025).

## 1.3 Statement of the Problem

As the Background established, generative typography arrives probabilistically deformed, while the tools that would name its font assume a geometrically intact glyph and fail as the catalogue scales. The result is a two-part gap that no existing system closes: none reads font identity from a hallucinated rather than a pristine glyph, and none refuses to answer when the glyph belongs to no catalogued font, the open-set case a hallucinated crop routinely presents (Lu et al., 2025). Free, license-clear reconstruction of generative typography therefore has no working tool, and designers are pushed back toward paid identifiers that fail on the very inputs at issue.

## 1.4 Objectives of the Study

### 1.4.1 General Objective

The general objective of this study is to design, build, and evaluate an open-set metric-learning system that identifies the typeface of hallucinated text in generative-AI images, mapping a deformed text crop to a ranked shortlist of the closest fonts in a localized palette of the top 50 to 100 Google Fonts, or to an "unknown" verdict when no palette font applies.

### 1.4.2 Specific Objectives

Specifically, the study aims to:

1. Curate the localized open-set font palette, and build a synthetic data pipeline that renders pristine word crops and degrades them with a controlled operator (elastic warp, blur and noise, and kerning jitter) that reproduces documented generative deformation (Gillani et al., 2025; Kondo et al., 2024).
2. Train a deformation-robust metric embedding on a frozen, register-corrected DINOv2 backbone (Oquab et al., 2024), so that geometric distance in the embedding encodes typographic similarity rather than deformation artifacts.
3. Implement an open-set decision that rejects out-of-palette glyphs through a post-hoc rejection score and produces a calibrated Top-K shortlist over the palette (Lu et al., 2025).
4. Verify each prediction with a re-render-and-compare typographic distance that is robust to geometric misalignment (Zhang et al., 2024), and analyze the system's errors by typographic family and by embedding-distance severity.
5. Evaluate the system under the Top-1 and Top-3 accuracy protocol against the Storia-AI and DINOv2-LoRA closed-set baselines (Chen et al., 2026; Jiang et al., 2025) and against a three-person human-proxy consensus panel on real generative crops.
6. Deploy the trained model behind a web application, so the system can be tested interactively and in real time on uploaded generative-AI images.

## 1.5 Research Questions

The gap in Section 1.3 frames the study's central research question: **how can the typeface of hallucinated text in a generative-AI image be identified against a localized, open-source font palette when the glyph is probabilistically deformed and may belong to no font in the palette?** It resolves into five specific questions, each tracing to an objective above:

1. How can a synthetic dataset reproduce the typographic hallucination of generative models faithfully enough to train a deformation-robust recognizer?
2. Can a metric embedding built on a frozen self-supervised Vision Transformer separate typographic identity from deformation, so that a hallucinated crop lands near its source font?
3. Can an open-set rejection mechanism reliably route an out-of-palette or hallucinated glyph to an "unknown" verdict instead of forcing a match?
4. How accurately does the system rank the correct font in a Top-K shortlist, and how does that accuracy compare against existing closed-set baselines and a human-proxy panel?
5. Does the system's error distribution stay within typographic families, so that its mistakes remain visually close to the correct font?

## 1.6 Scope and Limitations

This study covers the design, training, and evaluation of an open-set font recognizer for hallucinated text. Its scope includes the localized open-source font palette; a synthetic data pipeline that renders pristine word crops and degrades them with a controlled operator of elastic warp, blur and noise, and kerning jitter; a metric-learning stack built on a frozen DINOv2 Vision Transformer in PyTorch; an open-set decision that can reject out-of-palette glyphs; and evaluation under Top-1 and Top-3 accuracy, a re-render-and-compare typographic distance (SSIM/MSE), a confusion matrix organized by typographic family, and a three-person human-proxy panel. The trained model is deployed behind a web application for interactive testing.

Several boundaries limit the study's reach. Recognition targets a localized open-source palette rather than the full commercial font space, because the goal is free, license-clear reconstruction rather than mapping to paid licenses; fonts outside this palette are therefore only reachable through the "unknown" verdict, not named. The system recognizes text crops rather than full-page layout or template reconstruction, keeping the research question on font identity rather than document structure. It treats each font as a discrete identity rather than regressing continuous variable-font axes, and it is confined to Latin-script typography, where the target Google Fonts palette and the documented hallucination behavior are best characterized. Finally, training relies on synthetically degraded crops: the controlled operator approximates but cannot fully reproduce the deformation of every generative model, so a residual synthetic-to-real domain gap constrains how far accuracy on synthetic data transfers to text from unseen generators.

## 1.7 Significance of the Study

For the field of computer science and machine learning, this study contributes an open-set metric-learning approach to deformation-robust font identification. It inverts the prevailing paradigm, which trains closed-set classifiers on pristine glyphs and consequently fails in the wild (Wang et al., 2015; Chen et al., 2026), by learning an embedding that tolerates deformation and can abstain when no catalogued font applies.

For practitioners, meaning designers and everyday users of generative AI tools, the system offers a path to free, license-clear reconstruction of generative typography. It maps a hallucinated crop to open-source Google Fonts rather than to paid commercial licenses, and it works on exactly the deformed inputs on which closed identifiers fail, removing the lock-in those tools impose.

For future researchers, the framework is a building block for deformation-robust recognition beyond fonts. Its combination of a controlled synthetic-degradation pipeline with a post-hoc open-set rejection score is a reusable recipe for any fine-grained recognition task where inputs are probabilistically distorted and the true class may lie outside the training catalogue.
