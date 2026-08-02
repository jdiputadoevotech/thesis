# Proposal Defense — Speaker Script, Slides 1–8

> **The PPTX is the source of truth.** `Proposal Presentation template.pptx` (and its PDF export)
> is the deck. This file is the talk track that mirrors it — it is not a second deck and must not
> become one. If a slide changes in PowerPoint, change the **On screen** block here to match.
>
> Scope: the presenter's part only — title through The Gap. Matt takes over at The Solution.
> Q&A ammunition lives in `../script.md`. Defense spec lives in `../requirements.md`.

## Timing

| # | Slide | Budget |
|---|---|---|
| S1 | Title | 1:00 |
| S2 | The Big Picture | 1:15 |
| S3 | The Specific Problem | 3:00 |
| S4 | Research Question | 1:30 |
| S5 | Without an Answer | 1:30 |
| S6 | Significance | 2:00 |
| S7 | Scope & Limitations | 2:00 |
| S8 | The Gap | 2:15 |
| — | Handoff | 0:15 |
| | **Total** | **≈ 14:45** |

Budgets are measured off the written **Say** blocks at ~130 wpm. Rehearse against a timer — if
you run past 15:00, cut S8's third bullet (the human-consensus point) and trim S7's scope lines;
they carry the most words per unit of argument. Inside S3, the first cut is the encoder paragraph
(*"nothing inside the model catches it"*) — Kondo and Gillani carry the mechanism on their own.

## Ownership map — read before editing anything

Each fact has exactly one home. Everywhere else names the conclusion and moves on. An advisor
flagged repetition in the mock defense; this map is how it stays fixed.

| Slide | Owns | Must NOT say |
|---|---|---|
| S2 | Adoption. These are everyday design tools — and a real broken word is on screen. | "AI gets text wrong." Let them read the typo. |
| S3 | The measured rate (Liu), the mechanism (Gillani, Kondo), today's products failing (Wang, Jiang). | Re-describing what a hallucination looks like — S2 showed one. |
| S4 | The central question, verbatim. | Any new evidence. Any hint of the answer. |
| S5 | The human cost while the question is unanswered. | Tool capability (S3 owns it), beneficiaries (S6 owns them). |
| S6 | Beneficiaries and what becomes possible. | Restating the cost — S5 just said it. |
| S7 | The perimeter and the honest limits. | Re-arguing why free fonts matter. |
| S8 | The research-level blind spot: the field never posed this question. | S3's point in new clothes. **S3 = shipped products break. S8 = nobody asked.** |

---

## S1 · Title — 1:00

**On screen**
Addressing Typographic Hallucination in Generative AI Images: An Open-Set Metric Learning
Approach to Font Style Recognition · Janritch D. Diputado, Matt Erron G. Cabarrubias ·
Christine D. Bandalan, MEng · Department of Computer, Information Sciences and Mathematics ·
University of San Carlos

**Say**

After the chair introduces the panel, introduce yourselves, lead the short prayer, then:

"Good morning. Our study is titled *Addressing Typographic Hallucination in Generative AI
Images: An Open-Set Metric Learning Approach to Font Style Recognition*. Three words in that
title carry the whole thesis, so let me give them to you now and we will keep coming back to
them. *Typographic hallucination* is what happens when a generative model draws something that
looks like letters but is subtly wrong. *Open-set* means the system is allowed to answer
'none of these.' *Metric learning* means we identify a font by measuring visual distance rather
than by picking from a fixed list."

**→ Transition out**

"Generative AI can produce a finished design in seconds — but it cannot spell. And once that
broken text exists, there is no free way back to its font. Let me show you what I mean."

**If probed** — "Style, not the words" — we identify the typeface, not what it says. That is OCR's job, not ours.

---

## S2 · The Big Picture — 1:30

**On screen**
Two AI-generated marketing posters (badminton training, pickleball tournament).

**Say**

"These two posters were generated from a text prompt. No designer, no layout file, seconds of
work. This is genuinely how marketing material gets made now — small businesses, campus orgs,
social media teams reach for these tools first because the output looks professional and costs
nothing.

Take a moment with the one on the right." *(pause — let them find it)* "Community
**TOURNNAMT**. Everything else in that poster is publishable. The typography is not.

And notice what you cannot do about it. You cannot open the poster and retype that one word,
because it is not text — it is pixels. You would have to know the font first."

**→ Transition out**

"Now, one bad poster is an anecdote. A panel should not accept a thesis built on an anecdote —
so here is the measurement."

**If probed** — Yes, newer models are improving. That does not close this study: uncorrected output is still what a designer receives, and every image already generated stays broken.

---

## S3 · The Specific Problem — 2:30

**On screen**
- AI draws text wrong **most of the time** *(Liu et al., 2024)*
- The AI **smears nearby letters together** and invents shapes that **match no real font** *(Gillani et al., 2025; Kondo et al., 2024)*
- Font-finder tools need **clean letters**, or they break *(Wang, 2015)*: a 3,474-font tool still fails on messy text *(Jiang, 2025)*
- *(hallucinated text crop: "Cartchy tuns … a pasadise of sweet teats")*

**Say**

"First bullet. Liu and colleagues measured this in 2024: fewer than one in five generated images
render their text correctly. So what you just saw is not the unlucky poster — it is the normal
outcome.

Second bullet is *why*, and this is the part that matters for our method.

Start with what the model is *not* doing. When we set type, the software looks up a font file and
stamps a stored outline — an exact vector for that letter. A diffusion model has no font file and
does no lookup. It paints pixels. What it learned from training images is not a catalogue of
typefaces; it is a continuous sense of how letters look — where a stroke thickens, whether a serif
is there, how round a bowl is. A font lives in that space as a blend of traits, not as an entry
you select from.

Two documented consequences. Kondo's group: because the space is continuous, the model can land
*between* two real fonts and emit a letterform no foundry ever cut. It reads as type because every
trait is plausible; it matches nothing because it was sampled, not chosen. Gillani's group: the
model paints the whole word at once through attention, and attention does not respect character
boundaries — neighbouring letters share evidence and strokes bleed together. Look at the crop:
*Cartchy tuns*, and at the end, *sweet teats*.

And nothing inside the model catches it, because — Liu again — the text encoder handles the word
as meaning, not as shapes. It has no sub-character spatial sense to check the drawing against.

That is the crux. The damage is not dirt on top of a real font. Sometimes there is no real font
underneath.

Third bullet is where the practical wall is. Every font identifier available today — Wang's line
of work, and the commercial tools built on it — assumes a geometrically intact glyph it can
measure. That assumption holds for a scanned document. It fails here. And you cannot fix it with
a bigger catalogue: Jiang's 2025 classifier covers three thousand four hundred seventy-four
Google Fonts and still fails on deformed input. The bottleneck is not how many fonts you know."

**→ Transition out**

"So: the failure is the normal case, we know the mechanism, and nothing on the market touches it.
That leaves one question that has to be stated precisely."

**If probed** — Chen et al. (2026): state-of-the-art drops from ~86% on clean glyphs to 40.2% on deformed input. Held for Q&A; full answer in `../script.md`.

**If probed — "so it's a rendering bug?"** No. Rendering implies a correct outline exists and got damaged. Here the glyph is *drawn*, never rendered: style is a continuous latent manifold, so an out-of-catalogue letterform is a valid sample, not a fault (Kondo et al., 2024). Deformation also concentrates in the long tail — display, script, and rare faces (Zhuang et al., 2025) — exactly where clean-glyph recognizers are most confident. That is why our system must be allowed to answer "unknown."

---

## S4 · Research Question — 1:30

**On screen**
How can the typeface of hallucinated text in a generative-AI image be identified against a
localized, open-source font palette when the glyph is probabilistically deformed and may belong
to no font in the palette?

**Say**

Read it verbatim, unhurried. Then unpack only the loaded phrases:

"Three phrases in there are doing real work.

*A localized, open-source font palette* — we are not matching against every font that exists. We
match against a small, deliberately chosen set of free Google Fonts.

*Probabilistically deformed* — the distortion is random on every render. The same prompt twice
gives you two different deformations. So we cannot memorise the damage; we have to read through
it.

*May belong to no font in the palette* — and this is the one panels usually push on. Because of
the mechanism I described, the honest answer is sometimes 'unknown.' A system that always names
a font would be confidently wrong. Ours has to be able to decline."

**→ Transition out**

*(pause)* "That is the question. Before I say who is helped by answering it — I want you to see
what happens for as long as nobody can."

**If probed** — The central question resolves into five specific questions: dataset fidelity, the metric embedding, open-set rejection, Top-K accuracy against baselines and the human panel, and whether errors stay inside typographic families. Offer to walk them only if asked.

---

## S5 · Without an Answer — 1:30

**On screen**
- The image is finished — the design is not
- Today: retype by eye, guess, or pay for a font that still misses
- The poster stays a picture, never a template

**Say**

"Put yourself in front of that pickleball poster with a client waiting.

The image is done. The design is not — one word is misspelled and you cannot edit it. So you
have three moves, and all three are bad.

You retype the whole text block by eye and try to match the font from memory. That is manual
work on something a machine already made, and the match is a guess.

You use a paid identifier. It charges you, it hands you a licensed commercial font, and — as we
just established — on deformed letters it hands you the wrong one anyway. You have now paid for
a mismatch.

Or you regenerate and hope. Same probability, new typo.

So the poster stays what it is: a picture. It never becomes a template you can reuse, rebrand, or
hand to a client. Everything the generator saved you, that last step takes back."

**→ Transition out**

"That is the cost of the question staying open. Here is who is standing on the other side of it."

**If probed** — This is exactly the wall we hit at our internship: we build a pipeline that turns an AI image into an editable `.psd`, and font identity is the one step that has no solution. Verbal only — no slide.

---

## S6 · Significance — 2:00

**On screen**
1. The first *free, open-set, license-clear* font identifier for hallucinated generative text; enables template reconstruction with open-source Google Fonts.
2. **Companies/Establishments** could use the tool to save costs on AI generated content to create marketing material.
3. **Graphic Designers/AI Gen users** have more creative freedom and control over AI generated text material.

**Say**

"Three groups.

First, the field. To our knowledge this is the first font identifier that is free, that works on
hallucinated text, and that is allowed to say 'unknown.' Each of those exists somewhere on its
own. Together, in one system, they do not. And the *free* part is not a cost footnote — it is
what makes the output usable. If the answer is a licensed commercial font, the designer still
cannot ship the rebuild. Point them at a Google Font and the design is legally reusable the
moment they know its name.

Second, companies and establishments — the small business that generates its own marketing
material precisely because it has no design budget. They are the ones with the least room to
absorb either a font licence or a designer's hours.

Third, designers and AI-gen users. This is the creative-control point. Right now the model
decides your typography and you accept whatever it renders. Recover the font and the decision
comes back to you — regenerate the text properly, change the weight, keep the layout. You direct
the tool instead of negotiating with it."

**→ Transition out**

"For that payoff to be real and not a promise, we had to bound the work. This is exactly how far
it goes — and where it stops."

**If probed** — Beyond fonts: the recipe is controlled synthetic degradation plus post-hoc open-set rejection. That pairing transfers to any fine-grained recognition task where inputs are randomly distorted and the true class may sit outside the catalogue.

---

## S7 · Scope & Limitations — 1:30

**On screen**

*Scope*
- **Top 50–100 Google Fonts** (serif · sans-serif · display · mono)
- Can answer **"unknown"** when no font fits
- English/Latin fonts only
- Cropped text

*Limitations*
- Synthetic degradation ≠ every generator
- 3-person panel is a proxy, not ground truth
- Unknown-threshold trades coverage for accuracy

*(Slide sits at ~40 words with these three lines — at the folder cap. Keep them this short; the
full wording is in the talk track below.)*

**Say**

"Scope first — four bounds, each chosen for a reason.

Fifty to a hundred Google Fonts across the four families. Bounded on purpose: you can only
reliably say 'none of these' when 'these' is well defined. A small, known palette is what makes
the unknown answer meaningful.

Second line is that capability stated as scope — the system is built to abstain.

Latin only, and cropped text regions rather than whole layouts. We identify the font of a text
crop; we do not rebuild page structure.

Now the limitations, and I would rather raise these than have you find them.

Our degradation pipeline imitates documented hallucination mechanisms. It approximates them — it
does not reproduce the behaviour of every generative model, so accuracy on synthetic data may
not fully transfer to a generator we never saw.

Our human baseline is three people. That is a reasonable proxy for what a person can tell. It is
not authoritative ground truth, and we will not present it as one.

And the unknown threshold is a genuine trade-off. Set it strict and we reject matches that were
actually right. Set it loose and hallucinated glyphs get forced onto a font. It is tunable, but
it does not disappear."

**→ Transition out**

"Those bounds are ours — we chose them. The next one we did not choose. It is what we found
missing when we read the field."

**If probed** — Two more limitations held back: compute budget caps training epochs and palette size; text localization is an off-the-shelf component, so its failures propagate into the crops we analyse.

---

## S8 · The Gap — 2:00

**On screen**
- **Current studies train on pristine glyphs instead of AI generated images** *(Wang et al., 2015; Chen et al., 2026)*
- They treat AI deformations as bugs to suppress in generation; not to identify its underlying typographic identity
- No human consensus panel on reviewing of results

**Say**

"Earlier I cited Wang and Chen as tools that break. Here they are again for a different reason —
not what their systems fail at, but what the field assumed before building them.

Every one of these studies trains on pristine glyphs. Clean renders, straight from the font file.
The assumption underneath is that a correct letterform exists somewhere and the job is to recover
it — treat the damage as noise and invert it. That assumption is reasonable for a scan. For a
generative glyph it is false, because the deformation is not something that happened *to* the
letter. It is how the model drew it.

Second: there is a large body of work on generative text, and it is all pointed the other way —
at suppressing deformation inside the generator so the model renders cleanly next time. Useful
work. But nobody turns around and reads the broken output back to recover what typeface it was
reaching for. That direction is empty.

Third, and this one is methodological: we could not find a study that checks its font predictions
against human consensus. Everything is scored machine-against-label. Nobody asked whether a person
looking at the same deformed crop would agree.

So the blind spot is one sentence: no one recovers font identity from a natively deformed
generative glyph, scored open-set, against a localized palette."

**→ Transition out**

"To recap — the problem is measured, the question is stated, the cost of leaving it open is
concrete, and the gap is real. Matt will now take you through how we close it."

*Then stop talking.*

**If probed** — Chen et al. (2026) is the closest antecedent and our comparative baseline: frozen-ViT font classification, but explicitly closed-set and trained on pristine renders. We target the regime where they collapse.

---

## Delivery reminders

- Read **S4** (the question) and the final sentence of **S8** (the blind spot) verbatim and slowly. They are the spine.
- The pause after S4 is deliberate. Let the question sit before moving to S5.
- Gold Standard Rule (`../requirements.md`): the panel grades coachability. Take feedback gratefully — a flawed proposal defended graciously beats a perfect one defended defensively.
- Fill the defense date on the title slide before export.
