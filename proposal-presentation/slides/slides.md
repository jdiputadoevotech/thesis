---
marp: true
paginate: true
theme: default
title: Proposal Defense — Typographic Hallucination in Generative AI Images
footer: "Typographic Hallucination · Open-Set Font Recognition"
---

<!--
DECK SCOPE: Sections 1–3 only (Big Picture · Specific Problem · The Gap).
Section 4 "Your Solution" is the thesis partner's slides — continues after S8.
Authoritative spec: proposal-presentation/requirements.md.
Speaker notes live in HTML comments under each slide (export to PPTX presenter notes).
Keep slide bullets sparse — talk track carries the detail.
-->

# Addressing Typographic Hallucination in Generative AI Images

### An Open-Set Metric Learning Approach to Font Style Recognition

**Proponents:** [JD] · [MC]
**Adviser:** [Adviser name]
**Proposal Defense · [Date]**

<!--
Opening (chair-led): after the chair introduces the panel, introduce yourselves
and lead the short prayer, then open with the one-line hook —
"Generative AI can make a design in seconds, but it cannot spell — and that broken
text has no free tool to recover its font. That gap is what we close."
-->

<!-- STUDY NOTES — Title slide

WHAT this slide is: just the title, names, and the one-sentence hook. Nothing to
argue yet; the job is to plant the five key terms the panel will hear all defense.

DECODE THE TITLE, term by term:
- "Typographic Hallucination" = when a generative AI draws text that looks like
  letters but is subtly wrong — smeared strokes, warped curves, spacing that no
  real font uses. We borrow the word "hallucination" from how chatbots invent
  facts; here the model invents *letterforms*. This is the core phenomenon we study.
- "Generative AI Images" = pictures made from a text prompt by tools like Gemini
  "Nano Banana", GPT Image, Midjourney. The text baked into those pictures is what
  breaks.
- "Open-Set" = a recognition setting where the correct answer might NOT be in your
  list of known classes. Opposite is "closed-set" (answer is always one of your N
  categories). Open-set means the system is allowed — and required — to say
  "none of these / unknown." Critical for us because a hallucinated glyph may match
  no font in our palette.
- "Metric Learning" = a machine-learning approach that learns a distance. Instead
  of classifying "this is font #37," it learns to place similar-looking glyphs
  CLOSE together and different ones FAR apart in a numeric space, then answers by
  nearest-neighbor distance. This is what lets us compare a broken glyph to clean
  reference fonts by *similarity* rather than exact match.
- "Font Style Recognition" = identifying which typeface (font) a piece of text is
  set in. "Style" signals we care about the visual character (serif shapes, weight,
  proportions), not reading the words.

WHY the title is built this way: it names the problem (typographic hallucination),
the domain (GenAI images), and the two-part method (open-set + metric learning)
that make our solution different from every existing font finder. Panel should
leave this slide knowing the topic is "recover the font of broken AI text, for free."
-->


---

<!-- _class: lead -->
## 1 · The Big Picture

Generative AI image tools — Google Gemini "Nano Banana", OpenAI GPT Image, Midjourney — now produce marketing graphics, mockups, and social assets **in seconds**.

**But the text they render is typographically unreliable.**

There is no free, license-clear way to recover the typography of a generative image.

<!--
RATIONALE / why-now (this is the Rationale of the Study). Designers already build
with these tools daily. When they want to reuse the *typography* of a generated
image, they hit a wall: the font is unnamed and the letterforms are broken.
The only fallback is paid identifiers — which, as the next slides show, fail on
exactly this input. So the practical stake: free template reconstruction of
generative typography has no working tool today. Next slide grounds this in our
own experience.
-->

<!-- STUDY NOTES — 1 · The Big Picture

WHAT this slide claims: (1) GenAI image tools are now everyday design tools,
(2) the text they render is unreliable, (3) there is no free/legal way to recover
that text's typography. This is the "Rationale of the Study" — WHY the topic
matters at all, before we make it personal.

DECODE THE TERMS:
- "Generative AI image tools" = software that turns a written prompt into a
  finished picture. The three named ones are the current market leaders; naming
  them shows the problem is mainstream, not a toy.
- "in seconds" = the speed is the whole appeal — designers now reach for these
  first. That's what makes the text flaw matter: high usage, high stakes.
- "typographically unreliable" = the LETTERS specifically come out wrong, even
  when the rest of the image looks great. "Typography" = the craft/appearance of
  arranged type (fonts, spacing, weight).
- "license-clear" = legally safe to reuse. Commercial font-ID tools point you to
  PAID fonts with restrictive licenses. "License-clear" means we aim for fonts you
  can legally use for free (Google Fonts).
- "recover the typography" = figure out the font so you can re-typeset the text
  yourself in an editable file.

WHY it flows to the next slide: this slide argues the problem matters to the whole
design world (abstract rationale). The next slide narrows to "and it personally
blocks US at work" (personal rationale). General stake first, personal stake second.

LIKELY PANEL PROBE: "Isn't AI text getting better?" Answer: even improving models
still fail most of the time on stylized fonts, and once a broken image exists there
is still no free tool to recover its font — the recovery gap stays open regardless.
-->


---

## 1 · Where This Started — Our Internship

At the company we intern for, we build a pipeline that turns an **AI-generated image into an editable `.psd`** file.

- We generate the images with AI and **prompt for a specific font**
- The rendered font comes back **inaccurate** — it looks different from what we asked for
- To make the `.psd` truly editable, we must **identify the real font** — the missing link in our own pipeline

*This thesis grew directly out of that gap.*

![w:520](assets/pipeline-placeholder.png)

<!--
This is the personal rationale — why WE picked this topic, not just why it matters
abstractly. Tell the story plainly: our internship builds an AI-image -> editable
.psd pipeline. The one step that breaks is font identity — we prompt a font, the AI
renders something close-but-wrong, and without the true font the .psd can't be
faithfully rebuilt. So this is not a hypothetical problem; it is a wall we hit at
work. SCREENSHOTS: replace assets/pipeline-placeholder.png with real screenshots of
the existing pipeline (drop PNGs into proposal-presentation/slides/assets/). Show the
AI image on one side and the .psd / font-mismatch on the other — concrete proof the
problem is real and we already own the surrounding tooling.
-->

<!-- STUDY NOTES — 1 · Where This Started — Our Internship

WHAT this slide does: turns the abstract problem into a real wall we hit at work.
This is the "personal rationale" — why WE chose this, which makes the thesis
credible and grounded, not invented for a paper.

THE STORY IN PLAIN TERMS: at our internship we built a pipeline (an automated
multi-step process) that takes an AI-generated image and rebuilds it as an editable
Photoshop file. Every step works EXCEPT one: the font. We prompt for a specific
font, the AI renders something close but wrong, and without knowing the true font
we cannot faithfully rebuild the editable file.

DECODE THE TERMS:
- ".psd" = Photoshop Document — a layered, fully editable image file. "Editable"
  means each text block is real, re-typeable text in its correct font, not a flat
  picture. That is the deliverable our pipeline promises.
- "pipeline" = a chain of automated steps, each feeding the next (generate image →
  segment → extract text → rebuild layers → output .psd).
- "prompt for a specific font" = we tell the AI "use font X." The AI does not obey
  precisely — it renders an approximation. That mismatch is the failure point.
- "the missing link" = font identification is the one broken step; fix it and the
  whole pipeline delivers a truly editable file. This thesis IS that missing link.

WHY it matters for the defense: it answers "why should we believe this problem is
real?" with lived evidence and shows we already own the surrounding engineering —
we only need to solve the font step. The placeholder image will become real
screenshots (AI image vs. broken .psd) as visual proof.

LIKELY PANEL PROBE: "Is this just an internship deliverable, not research?" Answer:
the internship exposed the gap, but the gap itself (deformation-robust, open-set,
free font recovery) is unsolved in the literature — that is the research contribution,
covered in the Gap section.
-->


---

## 2 · The Problem Is Real

- AI draws text wrong **most of the time** — under **1 in 5** images have correct letters *(Liu, 2024)*
- It **smears letters together** and invents shapes matching **no real font** — **"typographic hallucination"** *(Gillani, 2025; Kondo, 2024)*
- Font-finder tools need **clean letters**, so they break *(Wang, 2015)*: a 3,474-font tool still fails on messy text *(Jiang, 2025)*, the best system drops to **40%** *(Chen, 2026)*, and AI assistants read the **word, not the shape** *(Li, 2025)*

<!--
This slide does double duty: the problem is real AND existing tools can't touch it.
Lead with the load-bearing <20% stat (Liu) — measured, not anecdotal. Then it is
systematic, not luck: attention bleed (Gillani) + continuous latent manifold emitting
glyphs between real fonts (Kondo); worst on display/script faces a designer picks for
effect (Zhuang 2025). Then the pivot: the classical paradigm and WhatTheFont-class
tools assume a geometrically intact glyph to recover (Wang) — true for a scan, false
for a hallucinated crop. Throwing more fonts at it doesn't help (Jiang's 3,474), the
SOTA collapses 86%->40.2% off pristine input (Chen), and VLMs hit Stroop interference
where reading the word overrides seeing its shape (Li). Optional visual: uncomment the
degradation figure below.
-->

<!-- STUDY NOTES — 2 · The Problem Is Real

WHAT this slide proves TWO things at once: (A) AI really does draw text wrong, and
(B) existing font-finder tools cannot handle that broken text. Every bullet is
backed by a cited paper so it reads as measured fact, not opinion.

BULLET 1 — "under 1 in 5 images have correct letters (Liu, 2024)":
- Meaning: in a controlled study, fewer than ~20% of generated images rendered the
  text correctly. So the failure is the NORM, not a rare glitch.
- Why it leads: it is the strongest, most quantified stat — measured, not anecdotal.

BULLET 2 — "smears letters together, invents shapes matching no real font —
'typographic hallucination' (Gillani, 2025; Kondo, 2024)":
- This explains the MECHANISM, i.e. WHY it fails, so the panel sees it is systematic,
  not bad luck.
- "smears letters together" = attention bleed: the model mixes neighboring letters
  because it doesn't cleanly separate them.
- "invents shapes matching no real font" = the model generates from a continuous
  latent space (a smooth numeric landscape of possible shapes), so it can output a
  glyph that sits BETWEEN two real fonts and belongs to neither. This is exactly why
  we need "open-set" — the true answer may be "no font."
- "typographic hallucination" = our name for this whole effect (see title notes).

BULLET 3 — "font-finder tools need clean letters, so they break (Wang, 2015)...":
- This is the PIVOT: even if you wanted to identify the font, today's tools can't.
- "need clean letters" = the classical recognition paradigm assumes a geometrically
  intact, undamaged glyph (true for a scanned document, false for a hallucinated crop).
- "a 3,474-font tool still fails (Jiang, 2025)" = throwing MORE fonts at the problem
  doesn't help; the issue is broken input, not a small catalog.
- "the best system drops to 40% (Chen, 2026)" = state-of-the-art accuracy collapses
  from ~86% on clean text to ~40% on deformed text. "SOTA" = state of the art, the
  current best published system.
- "AI assistants read the word, not the shape (Li, 2025)" = vision-language models
  (VLMs) suffer Stroop interference: they READ "HELLO" and report the meaning instead
  of analyzing the letter shapes. Stroop = the classic effect where reading a word
  overrides noticing its visual form. So VLMs are the wrong tool too.

WHY the slide is structured problem→mechanism→tools-fail: it walks the panel from
"this happens" to "here's why" to "and nothing existing fixes it," which sets up our
Statement of the Problem on the next slide.

TERM CHEAT-SHEET:
- "glyph" = the drawn shape of a single character (the visual 'A', not the letter A).
- "crop" = the cut-out image patch containing just the text we analyze.
- "latent manifold / latent space" = the internal numeric space a generative model
  samples shapes from; being continuous is why in-between (fake) fonts appear.
-->


<!-- ![w:820](../../assets/figures/degradation_pipeline.png) -->

---

## 2 · Statement of the Problem

**How can the typeface of hallucinated text in a generative-AI image be identified against a localized, open-source font palette when the glyph is probabilistically deformed and may belong to no font in the palette?**

Two capabilities are missing **at once**:

1. Read font identity from a **deformed**, not pristine, glyph
2. **Refuse to answer** when the glyph belongs to no catalogued font

<!--
Read the central question verbatim — it is the spine of the whole proposal. Then the
crux: no existing system does *either* of these, let alone both together. Reading a
deformed glyph is a metric-embedding problem; refusing an out-of-palette glyph is an
open-set recognition problem (Lu et al., 2025) — and a hallucinated crop is the normal,
not the edge, case. The central question resolves into 5 specific questions (dataset
fidelity, metric embedding on frozen ViT, open-set rejection, Top-K accuracy vs
baselines + human panel, whether errors stay within typographic families) — offer to
walk through them if the panel asks; otherwise keep moving.
-->

<!-- STUDY NOTES — 2 · Statement of the Problem

WHAT this slide is: the single central research question, read VERBATIM. It is the
spine of the whole proposal — everything else exists to answer it.

DECODE THE CENTRAL QUESTION, phrase by phrase:
- "How can the typeface of hallucinated text ... be identified" = the goal: name
  the font of broken AI text.
- "against a localized, open-source font palette" = we don't match against every
  font on earth; we match against a small, chosen set of free Google Fonts. "Palette"
  = our curated shortlist of candidate fonts. "Localized" = deliberately small/bounded.
  "Open-source" = free and legally reusable.
- "when the glyph is probabilistically deformed" = the input is randomly warped by
  the generative model (each render distorts differently — that's the "probabilistic"
  part). We must read the font THROUGH that distortion.
- "and may belong to no font in the palette" = the true font might not be in our set
  (or might be a fake in-between shape), so the system must be able to decline.

THE TWO MISSING CAPABILITIES (this is the key takeaway):
1. "Read font identity from a deformed glyph" = a METRIC-EMBEDDING problem: learn a
   distance that stays reliable even when the glyph is warped, so the nearest clean
   font is still the right one.
2. "Refuse to answer when the glyph belongs to no catalogued font" = an OPEN-SET
   RECOGNITION problem: know when NONE of your known fonts fit and output "unknown."

WHY BOTH AT ONCE IS THE HARD PART: existing systems do neither of these, and
certainly not together. And for us the hard case (a deformed, possibly-unknown glyph)
is the NORMAL input, not a rare edge case — so both capabilities are mandatory, not
optional.

DECODE THE SUPPORTING TERMS:
- "metric embedding" = converting a glyph image into a point in a numeric space where
  distance = visual similarity (see Metric Learning in title notes).
- "open-set recognition (Lu et al., 2025)" = the formal name for a classifier that can
  say "none of the above" instead of always picking a known class.
- "frozen ViT" (mentioned in speaker notes) = a Vision Transformer (image model)
  whose weights we do NOT retrain ("frozen"); we reuse its general visual features and
  only learn the distance on top. Cheaper and avoids overfitting.

STRUCTURE NOTE: the one central question breaks into 5 specific sub-questions (dataset
fidelity, the metric embedding, open-set rejection, Top-K accuracy vs baselines + human
panel, and whether errors stay within font families). Only walk those if the panel asks.
-->


---

## 2 · Significance & Scope

**Significance** — first **free** font identifier for AI-hallucinated text; enables rebuilding editable templates with open-source Google Fonts.

**Scope**
- **Top 50–100 Google Fonts** (serif · sans-serif · display · mono)
- Tested against existing tools **and a 3-person human panel**
- Can answer **"unknown"** when no font fits

**Delimitation** — not a general OCR or all-fonts tool; palette is bounded on purpose.

<!--
Significance and Scope are assembled from the objectives (Ch1 has no standalone
prose for these yet — flag internally, not to the panel). Significance framing:
this is not "a better WhatTheFont," it is the free, open-set capability that does
not exist. Scope boundaries all come straight from the six specific objectives —
stress the palette is deliberately localized (50–100 fonts), which is what makes
open-set rejection tractable. Delimitation manages panel expectations: we are not
solving general OCR, and "unknown" is a feature, not a failure.
-->

<!-- STUDY NOTES — 2 · Significance & Scope

WHAT this slide answers THREE standard proposal questions: why does this matter
(Significance), what exactly will we build/test (Scope), and what will we NOT do
(Delimitation). Panels always look for these three.

SIGNIFICANCE — "first free font identifier for AI-hallucinated text":
- The contribution isn't "a better version of an existing tool." It is a capability
  that does not exist at all: free + works on broken AI text + can say unknown.
- "enables rebuilding editable templates with open-source Google Fonts" = the payoff:
  once you know the font, you can re-typeset the design for free and hand back an
  editable file (ties straight back to the internship pipeline).

SCOPE — the exact boundaries of what we test:
- "Top 50–100 Google Fonts (serif · sans-serif · display · mono)" = our palette size
  and coverage. The four categories are the main typographic families:
    * serif = fonts with little feet/strokes on letter ends (e.g. Times).
    * sans-serif = no feet, clean (e.g. Arial).
    * display = decorative/headline fonts, high style — the ones AI mangles WORST.
    * mono(space) = every character same width (e.g. Courier), code-style fonts.
- "Tested against existing tools AND a 3-person human panel" = two benchmarks: current
  software (baseline) and human judgment (ground-truth proxy). The human panel gives a
  realistic "what a person could tell" bar to compare our accuracy against.
- "Can answer 'unknown' when no font fits" = the open-set capability, restated as a
  user-facing feature.

DELIMITATION — "not a general OCR or all-fonts tool; palette is bounded on purpose":
- "OCR" = Optical Character Recognition — reading the TEXT (the words). We are NOT
  doing that; we identify the FONT (the style). Saying so stops the panel from judging
  us on a goal we never set.
- "bounded on purpose" = the small palette is a design choice, not a limitation we
  failed to overcome. A small known set is precisely what makes "unknown" detection
  (open-set rejection) mathematically tractable — you can only reliably say "none of
  these" when "these" is a well-defined, limited set.

WHY DELIMITATION IS STRATEGIC: it manages expectations. "Unknown" is framed as a
FEATURE (honest refusal) rather than a failure (couldn't answer). Reframing the
limitation as a strength is deliberate.
-->


---

<!-- _class: lead -->
## 3 · The Gap — The Blind Spot

All prior work assumes a **clean glyph exists to be recovered**, and treats deformation as noise to invert.

**No one recovers font identity from a natively deformed generative glyph — scored open-set over a localized palette.**

<!--
This is the single most important sentence of the rationale. Slow down here. The
entire literature — legacy recognition, generative-text research, open-set methods,
metric embeddings, distance metrics — shares one assumption: a topologically faithful
glyph exists somewhere to recover. This thesis inverts the question: what if the
deformation is not noise but an irreducible, probabilistic property of the generative
model itself? Then you cannot "clean" it — you must recognize *through* it, and reject
when it belongs to nothing catalogued.
-->

<!-- STUDY NOTES — 3 · The Gap — The Blind Spot

WHAT this slide is: the single most important sentence of the whole rationale. It
names the exact hole in existing research that our thesis fills. Deliver it slowly.

THE SHARED ASSUMPTION (the blind spot):
- "All prior work assumes a clean glyph exists to be recovered" = every existing
  approach believes there is one true, undamaged letter shape hiding under the damage,
  and the job is to uncover it.
- "treats deformation as noise to invert" = they treat the warping like static on a
  photo — random junk you can filter out to get the clean original back. "Invert" =
  mathematically undo. "Noise" = unwanted random corruption on top of a real signal.

OUR INVERSION (the new idea):
- "No one recovers font identity from a natively deformed generative glyph — scored
  open-set over a localized palette."
- "natively deformed" = the deformation is BUILT IN by the generative model, not added
  afterward. This is the crux: what if the warping is NOT removable noise but an
  irreducible, probabilistic property of how the model draws? Then there is no clean
  original to recover — you must recognize the font THROUGH the deformation, not clean
  it off first.
- "scored open-set over a localized palette" = and you must also be able to reject
  (say "unknown") against a small known font set. "Scored" = we measure/rank matches
  by a numeric similarity score.

WHY THIS IS THE HEART OF THE THESIS: it reframes the entire problem. Everyone else:
"remove the damage, then recognize." Us: "the damage is permanent — recognize despite
it, and admit when nothing fits." That reframing is the original contribution; the next
slide shows five research fields that all share this same blind spot.

TERM CHEAT-SHEET:
- "recover / recovery" = reconstruct the original clean glyph before identifying it.
- "irreducible" = cannot be removed or reduced away; a fundamental property.
- "probabilistic" = varies randomly each time the model renders; not fixed.
-->


---

## 3 · Five Gaps, Five Clusters

| Cluster | The blind spot | Anchor |
|---|---|---|
| **Legacy recognition** | recover a glyph, never *read* deformation | Wang 2015 |
| **Generative text** | suppress deformation in-generator, never read it back | Liu 2024 · Zhuang 2025 |
| **Open-set rejection** | validated on natural images only, not font micro-irregularities | Karunanayake 2025 · Lu 2025 |
| **Metric embedding** | works on clean glyphs, untested under warping | Oquab 2024 · Wang 2024 |
| **Visual distance metrics** | assume an undeformed input glyph | Zhang 2024 |

**Seam:** none connects text isolation → deformation-robust embedding → open-set ranking on a localized palette.

<!--
Walk the table top to bottom — one line each, this is the RRL condensed. Each field
solves a piece but leaves the same blind spot from a different angle. The punchline is
the "Seam" row: the contribution is not any single component, it is *connecting* them
into one pipeline that no prior work joins. If a panelist pushes on any one cluster,
you have the verbatim gap sentence from Chapter 2 §2.2–2.6 to back each row.
-->

<!-- STUDY NOTES — 3 · Five Gaps, Five Clusters

WHAT this slide is: the entire Review of Related Literature (Chapter 2) compressed
into one table. Five research fields ("clusters") each solve PART of our problem but
all leave the SAME blind spot. The table proves the gap is real across the whole field,
not just one paper.

READ EACH ROW AS: [field] → [what it can't do] → [the paper we cite as proof].

ROW 1 — Legacy recognition (Wang 2015):
- "Legacy recognition" = classical font/character recognition — the pre-deep-learning
  and early-CNN approaches, e.g. WhatTheFont-style tools.
- Blind spot: they RECOVER a clean glyph but never READ the deformation itself as
  information. They assume the damage is removable.

ROW 2 — Generative text (Liu 2024 · Zhuang 2025):
- "Generative text" = research on making AI render text BETTER inside the generator.
- Blind spot: they try to SUPPRESS deformation at generation time; nobody reads the
  broken output back afterward to identify its font. Opposite end of the pipe from us.

ROW 3 — Open-set rejection (Karunanayake 2025 · Lu 2025):
- "Open-set rejection" = methods for saying "unknown / none of my classes" (see title
  notes).
- Blind spot: validated only on NATURAL images (photos of cats, cars, scenes), never
  on font MICRO-IRREGULARITIES — the tiny stroke/curve differences that separate fonts.
  So the technique exists but was never tested on our kind of input.

ROW 4 — Metric embedding (Oquab 2024 · Wang 2024):
- "Metric embedding" = the distance-learning approach we use (Oquab 2024 = DINOv2, the
  image model we build on).
- Blind spot: proven on CLEAN glyphs, untested under warping. The tool we need, never
  stress-tested in the condition we need it.

ROW 5 — Visual distance metrics (Zhang 2024):
- "Visual distance metrics" = ways to score how visually similar two images are (e.g.
  SSIM, LPIPS — used to check if our re-rendered font matches the input).
- Blind spot: they assume an UNDEFORMED input glyph to compare against. Same assumption
  breaks again.

THE PUNCHLINE — the "Seam" row:
- "none connects text isolation → deformation-robust embedding → open-set ranking on a
  localized palette."
- "Seam" = the join between fields where the work SHOULD connect but doesn't. Our
  contribution is not inventing any single component — it is STITCHING these five into
  one working pipeline that no prior work joins.
- The three stages named are our pipeline: (1) text isolation = cut the text out of the
  image; (2) deformation-robust embedding = turn the warped glyph into a reliable point
  in metric space; (3) open-set ranking = rank candidate fonts and reject if none fit.

WHY A TABLE: it lets a panelist attack any single field and get a crisp one-line answer,
while the visual pattern (same blind spot, five times) makes the gap undeniable.

"Anchor" column = the flagship paper that best represents each cluster's blind spot —
your citation to defend that row if challenged.
-->


---

## 3 · The Baseline That Fails in the Wild

- **Storia-AI / ControlText** — 3,474-font classifier, the field's reference embedding *(Jiang et al., 2025)*
- Together with **WhatTheFont-class** commercial identifiers:
  - reference-grade **on clean glyphs**
  - **collapse on hallucinated crops** — the exact regime we target

→ This is our comparative baseline. **Our solution begins here.**

<!--
Close section 3 by naming the concrete baseline we measure against: Storia-AI's
Google Font Classifier (our font-classify/ sandbox), which ControlText (Jiang 2025)
established as the reference embedding. It is genuinely strong — on clean glyphs. It
is validated only on undeformed input and collapses in open-set generative
environments. That collapse is the opening for our approach. HANDOFF: this is where
the partner's Section 4 "Your Solution" begins.
-->

<!-- STUDY NOTES — 3 · The Baseline That Fails in the Wild

WHAT this slide is: names the concrete system we will measure OURSELVES against, and
shows it fails exactly where we operate. Closing the Gap section by pointing at the
opening our solution steps into.

DECODE THE BASELINE:
- "baseline" = the reference system you compare your new method to, to prove yours is
  better. You must name one; ours is Storia-AI's Google Font Classifier.
- "Storia-AI / ControlText — 3,474-font classifier (Jiang et al., 2025)" = an
  open-source deep-learning model that identifies fonts across 3,474 Google Fonts.
  ControlText (the Jiang 2025 paper) established it as "the field's reference
  embedding" = the standard, widely-cited feature representation others compare to.
  It lives in our font-classify/ sandbox — we run it directly, not just cite it.
- "reference embedding" = the benchmark numeric representation of a glyph that the
  field treats as the one to beat.

DECODE THE FAILURE:
- "WhatTheFont-class commercial identifiers" = paid font-ID tools of the same family
  (upload an image, get a font name + a link to buy it).
- "reference-grade on clean glyphs" = genuinely excellent — on undamaged, scanned, or
  vector-clean input. We concede it is strong; that makes the next line credible.
- "collapse on hallucinated crops — the exact regime we target" = on warped AI text it
  falls apart. "In the wild" = real-world messy input, as opposed to lab-clean test
  data. "Regime" = the operating condition/environment. Their weakness is precisely
  our target zone.
- WHY it fails ties back to the Gap: it was trained and validated only on pristine
  input (over-fitted to clean glyphs), so it has never learned to handle native
  deformation or to say "unknown."

WHY END THE SECTION HERE: "Our solution begins here" is the deliberate handoff line.
We have now shown (1) the problem is real, (2) the central question, (3) the gap, and
(4) the concrete tool that fails in that gap. That failure is the door the partner's
Section 4 walks through with the proposed solution.

TERM CHEAT-SHEET:
- "classifier" = a model that assigns an input to one of N known categories (here,
  which of 3,474 fonts) — note: closed-set, which is part of why it can't say unknown.
- "over-fitted / over-fitting" = a model tuned so tightly to its clean training data
  that it fails on anything different (like our deformed crops).
-->


---

<!-- _class: lead -->
## Section 4 · Your Solution

*(continues — thesis partner)*

<!-- STUDY NOTES — Section 4 handoff

WHAT this slide is: just the transition marker. Your part (Sections 1–3: Big Picture,
the Problem, the Gap) ends; your thesis partner takes over with Section 4 (the proposed
solution — the metric-learning + open-set pipeline that fills the gap you just proved).

WHAT YOU'VE ESTABLISHED by this point (the through-line to remember):
1. Big Picture — GenAI text is unreliable and has no free font-recovery tool.
2. Internship — we personally hit this wall building an AI-image → editable .psd pipeline.
3. Problem Is Real — measured proof it fails, plus proof existing tools can't fix it.
4. Statement of the Problem — the central question: read a deformed glyph AND reject
   unknowns, over a small free-font palette.
5. Significance & Scope — first free, open-set identifier; bounded palette on purpose.
6. The Gap — everyone assumes a clean glyph exists to recover; we recognize THROUGH
   the deformation instead.
7. Five Clusters — five fields, same blind spot; contribution is the seam that joins them.
8. Baseline — Storia-AI/WhatTheFont are strong on clean glyphs, collapse on ours.

Hand to partner cleanly: "We've shown the problem is real, unsolved, and where existing
tools fail. [Partner] will now show how we solve it." Then stop talking.
-->

