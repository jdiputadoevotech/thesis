# Proposal Defense — Speaker Script, Slides 1–11

> **The PPTX is the source of truth.** `Proposal Presentation template.pptx` (and its PDF export)
> is the deck. This file is the talk track that mirrors it — it is not a second deck and must not
> become one. If a slide changes in PowerPoint, change the **On screen** block here to match.
>
> Scope: the presenter's part only — title through Technical Background. Matt takes over at The Solution.
> Q&A ammunition lives in `../script.md`. Defense spec lives in `../requirements.md`.

## Timing

| # | Slide | Budget |
|---|---|---|
| S1 | Title | 1:00 |
| S2 | The Big Picture | 1:15 |
| S3 | The Specific Problem | 3:00 |
| S4 | Research Question | 1:30 |
| S5 | Without an Answer | 1:30 |
| S6 | Significance | 2:15 |
| S7 | Scope & Limitations | 3:45 |
| S8 | The Gap | 2:15 |
| S9 | Technical Background: Reading Type | 1:00 |
| S10 | Technical Background: Deciding and Refusing | 1:00 |
| S11 | Technical Background: How We Measure | 1:00 |
| — | Handoff | 0:15 |
| | **Total** | **≈ 19:45** |

Budgets are measured off the written **Say** blocks at ~130 wpm.

> ⚠️ **The presenter's half is now ≈ 19:45 of a 30-minute total, leaving Matt ≈ 10.** This is the
> deck's tightest constraint and it is getting worse with each expansion — S7 alone has grown from
> 1:30 to 3:45. Rehearse both halves together against a timer *before* trusting these numbers. If
> Matt cannot fit in 10 minutes, cut in the order below; the first two cuts alone recover ~1:30.

Cut order when running long:

1. **S7** — the "top fifty to a hundred" paragraph explaining *why* the palette skews serif/sans
   (~85 words, ~40s; it is marked inline in the Say block). Drop it and go straight to the Zhuang
   paragraph — the bullet still lands.
2. **S7** — if more is needed, compress the whole palette-coverage limitation to one line: "our
   thinnest coverage is display and script, which is where deformation is worst; that is what the
   unknown verdict is for." The full version survives as Q&A ammunition in the **If probed** lines.
3. **S11** — collapse to one spoken line ("we score with Top-K, an SSIM re-render check, and a
   three-rater Fleiss' κ panel"); Matt's measurement slides cover the same instruments in detail.
4. **S3** — the encoder paragraph (*"nothing inside the model catches it"*); Kondo and Gillani
   carry the mechanism on their own.

**S9–S11 exist because the advisor asked for a technical background before The Solution.** They
are a vocabulary primer, not an argument: the panel meets *f_θ*, τ, DINOv2, conformal Top-K, and
Fleiss' κ here so that Matt's slides can use the words without stopping to define them. Every line
on them is traceable to `chapters/03-technical-background/draft.md` or
`chapters/04-methodology/draft.md` — the section is printed next to each claim below, because the
panel is expected to cross-check.

## Ownership map — read before editing anything

Each fact has exactly one home. Everywhere else names the conclusion and moves on. An advisor
flagged repetition in the mock defense; this map is how it stays fixed.

| Slide | Owns | Must NOT say |
|---|---|---|
| S2 | Adoption. These are everyday design tools — and a real broken word is on screen. | "AI gets text wrong." Let them read the typo. |
| S3 | The measured rate (Liu), the mechanism (Gillani, Kondo), today's products failing (Wang, Jiang). | Re-describing what a hallucination looks like — S2 showed one. |
| S4 | The central question, verbatim. | Any new evidence. Any hint of the answer. |
| S5 | The human cost while the question is unanswered. | Tool capability (S3 owns it), beneficiaries (S6 owns them). |
| S6 | Beneficiaries and what becomes possible — including the reusable artifacts other researchers inherit. | Restating the cost (S5 just said it). **And do not say the field lacks a human-consensus benchmark — S8 owns that.** Name the artifact; let S8 land why it is missing. |
| S7 | The perimeter and the honest limits. | Re-arguing why free fonts matter. |
| S8 | The research-level blind spot: the field never posed this question. | S3's point in new clothes. **S3 = shipped products break. S8 = nobody asked.** |
| S9 | How a crop becomes a point: glyph traits, the degradation operator *D*, the metric head *f_θ*. | Why the gap exists (S8 owns it). Any accuracy figure. |
| S10 | The refusal mechanism: open-set, the threshold τ, the calibrated shortlist. | Re-arguing *that* the system should refuse — S4 and S7 already established it. This slide is only *how*. |
| S11 | The measurement instruments and what each one asks. | Results. Nothing has been run. Name the instrument, not an outcome. |

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

**If probed — "so it's a rendering bug?"** No. Rendering implies a correct outline exists and got damaged. Here the glyph is *drawn*, never rendered: style is a continuous latent manifold, so an out-of-catalogue letterform is a valid sample, not a fault (Kondo et al., 2024). That is why our system must be allowed to answer "unknown."
> *Do not add the long-tail point here.* Zhuang's finding — that deformation concentrates in display, script, and rare faces — is **S7's**, where it is on screen and fully unpacked against our palette coverage. Spending it at S3 means saying it twice.

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

## S6 · Significance — 2:15

**On screen**
1. First *free, open-set, license-clear* font identifier — makes the template rebuild legal
2. **Designers / AI-gen users** — creative control over AI typography, not whatever the model rendered
3. **Companies** — reuse AI marketing material without buying a font licence
4. **Researchers** — a reproducible hallucinated-type corpus and the first human-consensus benchmark

*(43 words. Four beneficiaries do not fit at the previous phrasing — three alone already ran 49
words, and adding researchers verbatim would have hit 71 against a 45-word cap. Every line is
compressed; the full argument stays in the **Say** block, which is where it belongs.)*

**Say**

"Four groups.

First, the field. To our knowledge this is the first font identifier that is free, that works on
hallucinated text, and that is allowed to say 'unknown.' Each of those exists somewhere on its
own. Together, in one system, they do not. And the *free* part is not a cost footnote — it is
what makes the output usable. If the answer is a licensed commercial font, the designer still
cannot ship the rebuild. Point them at a Google Font and the design is legally reusable the
moment they know its name.

Second, designers and AI-gen users. This is the creative-control point. Right now the model
decides your typography and you accept whatever it renders. Recover the font and the decision
comes back to you — regenerate the text properly, change the weight, keep the layout. You direct
the tool instead of negotiating with it.

Third, companies and establishments — the small business that generates its own marketing
material precisely because it has no design budget. They are the ones with the least room to
absorb either a font licence or a designer's hours.

Fourth, other researchers — and this one is different in kind. The first bullet is what is *new*;
this one is what is *reusable*. We leave two artifacts behind. A synthetic corpus of deformed type
that is seed-deterministic, so anyone can regenerate our exact training data. And a hundred real
generative crops, each labeled independently by three typographers with their agreement reported.
Whoever works on this next does not have to build either one."

**→ Transition out**

"For that payoff to be real and not a promise, we had to bound the work. This is exactly how far
it goes — and where it stops."

**If probed** — Beyond fonts: the recipe is controlled synthetic degradation plus post-hoc open-set rejection. That pairing transfers to any fine-grained recognition task where inputs are randomly distorted and the true class may sit outside the catalogue.

**If probed — "isn't bullet 4 the same as bullet 1?"** No. One is the claim, the other is the leftovers. Bullet 1 says no system currently does free + hallucination-robust + open-set together. Bullet 4 is the reusable output regardless of whether our accuracy numbers land: the seeded corpus (Chapter 4 §4.2.1) and the human-labeled benchmark (§4.2.3) hold their value even if the model underperforms.

---

## S7 · Scope & Limitations — 3:45

**On screen**

*Scope*
- **Top 50–100 Google Fonts** (serif · sans-serif · display · mono)
- **English/Latin** fonts only
- Font **classification** only — localization is off-the-shelf
- Can answer **"unknown"** when no font fits

*Limitations*
- Only three deformations modeled — **elastic warp, blur/noise, kerning jitter** — not every generator's artifacts *(Gillani, 2025; Chen, 2026)*
- Palette cannot span every typeface — a top-50–100 list is mostly serif and sans, so **display and script are our thinnest coverage**, and that is exactly where generative deformation is worst *(Zhuang, 2025)*

*(75 words — deliberately over the ~55 hard cap, because the coverage limitation is not
self-explanatory at slide length and a panelist who has to ask "why display and script?" has
already lost the point. **Recommended: split this into two slides** — S7a Scope, S7b Limitations.
That costs no spoken time (the **Say** block is unchanged either way), puts each half comfortably
under the cap, and gives the limitations room to breathe. If it must stay one slide, cut scope line
4 to just **Can answer "unknown"** and accept a dense frame. Two limitations stay spoken-only —
the 3-person panel as a proxy, and the unknown-threshold trade-off. Do not add them to the slide.)*

*(Wording note: the PPTX previously read "not localization of texts within the images," which reads
as "we never localize." The conceptual-framework figure six slides later shows a live localization
step, so a cross-checking panelist would catch the contradiction. Chapter 4 §4.4.2 is precise —
the localizer runs, it is off-the-shelf, and it is not a contribution of this work. The bullet above
now says that.)*

**Say**

"Scope first — four bounds, each chosen for a reason.

Fifty to a hundred Google Fonts across the four families. Bounded on purpose: you can only
reliably say 'none of these' when 'these' is well defined. A small, known palette is what makes
the unknown answer meaningful.

Second line is that capability stated as scope — the system is built to abstain.

Latin only. And our contribution is the classification, not the finding. Locating the text inside
the image is done by an off-the-shelf detector — it does run, on every upload, but we did not build
it and we do not claim it. We identify the font of a text crop; we do not rebuild page structure.

Now the limitations, and I would rather raise these than have you find them.

First, our degradation pipeline models exactly three deformations — elastic warp, blur and noise,
and kerning jitter. Those three were not picked casually; warp and kerning jitter come from
Gillani's attention-smearing mechanism, blur and noise from the render-quality baseline Chen's
group used, and each one is a dial we log per image. But three is three. A generator we
never tested may break type in a fourth way we did not model, so accuracy on our synthetic data
may not fully transfer to it.

Second, and this is the one I would press on if I were you: we cannot cover every kind of typeface,
and the gap is not evenly spread.

*(⏱ The next paragraph is the single longest optional passage in the presenter's half — about 85
words, roughly 40 seconds. It is the "why" behind the bullet. If the rehearsal clock is tight, drop
it and go straight to the Zhuang paragraph; the bullet still lands, just with less colour.)*

Start with what a 'top fifty to a hundred' list actually contains. Popularity rankings track how
often a face gets used, and most type gets used for body copy — paragraphs, captions, labels. Body
copy is set in serif and sans-serif. So a popularity-ranked palette is overwhelmingly serif and
sans by construction. Display and script faces are used sparingly and deliberately, one headline at
a time, so they sit far down that ranking. They are our long tail.

Now the second half of the problem. Generative deformation is not uniform either. Zhuang's group
measured this: it concentrates in exactly that long tail — the display, script, and rare faces.
Which means our thinnest coverage sits directly on top of the hardest input. The place we are least
equipped to name a font is the place the model is most likely to have mangled one.

That is an uncomfortable overlap and I would rather say it than have you find it. It is also
precisely why the system is built to abstain: on a face we do not carry, deformed past recognition,
the honest output is 'unknown' — not the nearest thing in our palette dressed up as an answer. And
every commercial or foundry typeface is outside the palette by construction, so those return
'unknown' too.

Third, our human baseline is three people. That is a reasonable proxy for what a person can tell.
It is not authoritative ground truth, and we will not present it as one — Jiang's group says the
quiet part out loud: font ground truth is usually unavailable, and many fonts look alike.

And fourth, the unknown threshold is a genuine trade-off — the standard one the rejection
literature reports, surveyed by Lu and colleagues. Set it strict and we reject matches that
were actually right. Set it loose and hallucinated glyphs get forced onto a font. It is tunable,
but it does not disappear."

**→ Transition out**

"Those bounds are ours — we chose them. The next one we did not choose. It is what we found
missing when we read the field."

**If probed** — Two more limitations held back: compute budget caps training epochs and palette size; text localization is an off-the-shelf component, so its failures propagate into the crops we analyse.

**If probed — "why only those three deformations?"** Each maps to a documented mechanism: elastic warp and kerning jitter to cross-character attention bleeding (Gillani et al., 2025), blur and noise to the render-quality baseline our synthetic precedent used (Chen et al., 2026). Chapter 3 §3.2.3 defines them formally as the operator *D*, and Chapter 4 Table 1 logs each level per image, so the bound is auditable rather than asserted.

**If probed — "then why not just add more display and script faces?"** Because the palette bound is what makes the unknown verdict meaningful — you can only say "none of these" when "these" is a defined, well-sampled set, and every face we add needs its own ~575 rendered variants and its share of a fixed compute budget (Chapter 4 §4.3.1). Widening the palette to chase the tail would thin the coverage of every class in it. The design answer is not a bigger catalogue — that is the failure mode we cite Jiang et al. (2025) for on S3, where 3,474 fonts still break on deformed input. It is abstention plus an honest statement of where coverage is thin, which is what this slide is.

**If probed — "can you quantify how thin?"** Not yet. The palette is specified as 50–100 faces across four family classes (Chapter 4 §4.3.1); the exact per-class split is fixed when the palette is finalized, and the family-level breakdown will appear in the confusion matrix of Chapter 5. We are not going to invent a number here.

---

## S8 · The Gap — 2:00

**On screen**
- Current studies train on **pristine glyphs**, not AI-generated images *(Wang, 2015; Chen, 2026)*
- They treat AI deformations as **bugs to suppress in generation**, not as typographic identity to recover *(Du, 2025; Zhuang, 2025)*
- Predictions are scored **machine-vs-label** — classifier top-k or MLLM judge, never human consensus *(Jiang, 2025; Shu, 2025)*

*(47 words — inside the ~55 hard cap. Citations use the folder's short `*(Author, Year)*` form, as
S3 already does; the full `et al.` strings would push this slide 12 words over.)*

**Say**

"Earlier I cited Wang and Chen as tools that break. Here they are again for a different reason —
not what their systems fail at, but what the field assumed before building them.

Every one of these studies trains on pristine glyphs. Clean renders, straight from the font file.
The assumption underneath is that a correct letterform exists somewhere and the job is to recover
it — treat the damage as noise and invert it. That assumption is reasonable for a scan. For a
generative glyph it is false, because the deformation is not something that happened *to* the
letter. It is how the model drew it.

Second: there is a large body of work on generative text, and it is all pointed the other way —
at suppressing deformation inside the generator so the model renders cleanly next time. Du's group
gates attention so text regions stop bleeding into each other; Zhuang's group rebuilds the
rendering path for rare glyphs. Useful work, both of them. But nobody turns around and reads the
broken output back to recover what typeface it was reaching for. That direction is empty.

Third, and this one is methodological: look at how the field checks its own font predictions.
Jiang's group runs into this directly — they admit font ground truth is usually unavailable and
that many fonts look alike — and their answer is to push both images through a pre-trained font
classifier and compare the top-k probability distributions that come out.
Shu's group scores generated text with a multimodal model acting as judge. In both cases the
referee is another machine. We could not find a study that asks whether three people looking at the
same deformed crop would agree on the font.

So the blind spot is one sentence: no one recovers font identity from a natively deformed
generative glyph, scored open-set, against a localized palette."

**→ Transition out**

"To recap — the problem is measured, the question is stated, the cost of leaving it open is
concrete, and the gap is real. Before Matt shows you the system we built to close it, let me hand
you the vocabulary it runs on, so none of it arrives cold."

**If probed** — Chen et al. (2026) is the closest antecedent and our comparative baseline: frozen-ViT font classification, but explicitly closed-set and trained on pristine renders. We target the regime where they collapse.

**If probed — "which paper says nobody uses a human panel?"** None, and we would not claim one does. The citable half is what the field *does* do: Jiang et al. (2025) score font fidelity by classifier top-k distribution, Shu et al. (2025) by an MLLM judge. The absence of a human-consensus check is our reading of that evidence, not a finding we are attributing to anyone.

---

## S9 · Technical Background: Reading Type — 1:00

**On screen**
- Font identity lives in **stroke, serif, x-height** — not in the word
- **Degradation D**: warp · blur · kerning jitter, applied to clean renders
- **Metric head f_θ** turns a crop into a point; same font lands near
- Backbone: **frozen DINOv2** ViT, never retrained

*(40 words. Figure: `assets/figures/degradation_pipeline.png`.)*

**Say**

"Four terms, and then Matt can use them freely.

First, what the system actually looks at. Not the word — the *shape*. Stroke thickness, whether a
serif is there, how tall the lowercase body is. Those traits are what separate one typeface from
another, and they survive when the spelling does not.

Second, *D*. That is our degradation operator: we take a clean render of a known Google Font and
deliberately break it — elastic warp, blur and noise, jittered letter spacing. We know the font,
because we chose it, and we know exactly how much damage we did, because we set the dials. That is
how we manufacture labeled hallucinated text.

Third, *f-theta* — the metric head. It takes a crop and returns a point in a space. Crops set in
the same typeface land near each other; different typefaces land apart. Recognition then becomes a
distance measurement instead of a lookup, which is the whole reason a deformed glyph can still be
placed *near* its source.

Fourth, the backbone underneath it: DINOv2, a vision transformer that already learned general
shape features without labels, from images that were never about type. We freeze it. Its weights
never move. Only the small head on top learns anything about typography."

**→ Transition out**

"That gets us a point in a space. Now — how does the system decide whether that point is close
enough to name a font at all?"

**If probed** — All four are defined in Chapter 3: font anatomy §3.2.1, the operator *D* §3.2.3 (Eq. 3), the metric embedding and triplet loss §3.3.2 (Eqs. 4–6), the frozen encoder §3.4.2.

**If probed — "why freeze the backbone?"** Two reasons: in-the-wild crops arrive with no font labels, so we cannot fine-tune on them; and a frozen encoder keeps general shape knowledge that a small font-specific network would lose. Chapter 4 §4.3.2 keeps LoRA fine-tuning off the open-set path for exactly that reason.

---

## S10 · Technical Background: Deciding and Refusing — 1:00

**On screen**
- **Open-set**: allowed to answer *"unknown"* instead of forcing a label
- Match test: distance to nearest palette font vs. threshold **τ**, set so 95% of true in-palette crops pass
- Shortlist calibrated by **conformal prediction** *(Shi, 2024)*
- Candidate score under test: **energy** *E(x)* *(Hofmann, 2024)*

*(43 words. Figure: `assets/figures/embedding_space.png`.)*

**Say**

"You already know the system has to be able to decline. This slide is the machinery that lets it.

The decision is one comparison. We measure the distance from the crop's point to the nearest font
in the palette, and we ask whether that distance is under a threshold — tau. Under it, we name the
font. Over it, we say unknown, and we name nothing at all.

Tau is not a number we pick by feel. We calibrate it on validation data, at the cutoff where
ninety-five per cent of crops whose font genuinely *is* in the palette get accepted. That fixes the
trade-off in the open, and it means we can report how often an out-of-palette crop slips through.

When we do name a font, we do not hand over one guess. We return a short ranked list, and conformal
prediction sizes that list so it carries a stated confidence rather than an arbitrary top-three.

And the distance itself is a design choice we are still testing. The default is embedding distance.
The alternative in the literature is an energy score, which reads how far off-manifold an input is.
We evaluate both at the same operating point; whichever rejects better, wins."

**→ Transition out**

"Naming a font is easy to claim. So the last thing to hand you is how we check whether the name was
right."

**If probed** — Open-set recognition and the rejection score are Chapter 3 §3.3.3 (Eqs. 7–8); the threshold τ and its 95%-recall calibration are Chapter 4 §4.4.2, with the false-positive rate at that operating point reported per §4.10.2; the calibrated shortlist is §4.2.2 (Shi et al., 2024 — RC3P; Ding et al., 2025).

**If probed — "so which score do you actually use?"** Distance to the nearest palette font is the default and the one the framework diagram shows. Energy is a named candidate we benchmark against it — Chapter 3 §3.3.3 flags that no OOD score has been validated on typographic deformation, so deciding between them by measurement is part of the work, not a gap in it.

**If probed — "an unknown could mean two things"** Correct, and we say so in Chapter 4 §4.4.2: the font may sit outside our 50–100, or the glyph may be hallucinated past recovery. Both surface identically. What the verdict guarantees is that no font is invented to fill the gap.

---

## S11 · Technical Background: How We Measure — 1:00

**On screen**
- **Top-1 / Top-3 accuracy** — is the true font in the shortlist *(Wang, 2015)*
- **Re-render check** — SSIM of re-rendered prediction vs. the crop
- **Fleiss' κ** — three raters, 2-of-3 agreement fixes the label
- Confusion matrix by family: serif · sans · display · mono

*(38 words. Figure: `assets/figures/ssim_pipeline.png`.)*

**Say**

"Four instruments, and none of them has produced a number yet — this is a proposal.

Top-1 and Top-3 accuracy: does the true font come back first, or at least in the shortlist. That is
DeepFont's protocol from 2015, and we keep it so our results are comparable to the field's.

The re-render check: we take the font we predicted, render the same word in it, and score how
closely that rendering matches the original crop structurally, using SSIM. It answers a different
question from accuracy — not *was the label right*, but *does the answer actually look like the
input*.

Fleiss' kappa: our ground truth for real generative crops comes from three typographers who label
the same hundred crops independently, blind to each other and to the model. Two of three must agree
before a label is fixed, and kappa is the number that tells you how much they agreed overall. We
report it whatever it says.

And the confusion matrix, broken down by family. If we get a font wrong, we want to know whether we
missed inside the serif family or jumped from a serif to a monospace. Those are not equally bad
errors, and the matrix is what makes the difference visible."

**→ Transition out**

"That is the vocabulary and that is the yardstick. Matt will now take you through the system
itself."

*Then stop talking.*

**If probed** — Top-K is Chapter 4 §4.2.2 (Wang et al., 2015); the structural-similarity metrics are Chapter 3 §3.4.4 (Eq. 11) with the deformation-robust successors DeepSSIM and SAMScore; the human-proxy rubric and its 2-of-3 rule are §4.2.3; validation and the family-weighted severity index are §4.10.2 (Chen et al., 2026).

**If probed — "three raters is not many"** Agreed, and we list it as a limitation on S7. It is an accuracy floor and a proxy for what a person can tell, not authoritative ground truth, and we will not present it as one. The bound is expert effort: a hundred crops labeled by three people is three hundred independent judgments.

---

## Delivery reminders

- Read **S4** (the question) and the final sentence of **S8** (the blind spot) verbatim and slowly. They are the spine.
- The pause after S4 is deliberate. Let the question sit before moving to S5.
- **S9–S11 change register.** S1–S8 argue; S9–S11 explain. Slow down, drop the persuasion, and say each term once, plainly. If the panel is nodding, move — do not elaborate.
- Every S9–S11 claim has a chapter section printed in its **If probed** line. If a panelist reaches for the document, name the section rather than paraphrasing it again.
- Gold Standard Rule (`../requirements.md`): the panel grades coachability. Take feedback gratefully — a flawed proposal defended graciously beats a perfect one defended defensively.
- Fill the defense date on the title slide before export.

---

## Appendix — pending PPTX corrections outside this script

Not talk track. These are deck↔chapter mismatches found while writing S9–S11, and they sit in
**Matt's half**, so they are recorded here only to be handed over. Each is a line a cross-checking
panelist lands on.

| Slide | Currently says | Chapter says | Change to |
|---|---|---|---|
| The Solution (Energy/RC3P) | "Energy Score Bouncer" | Ch4 §4.4.2 decides with distance vs. calibrated **τ**; energy is surveyed literature in Ch3 §3.3.3 | "Rejects with a calibrated threshold **τ**; **energy score** *E(x)* benchmarked as an alternative *(Hofmann, 2024)*" — now backed by Ch4 §4.10.2 |
| The Solution (Energy/RC3P) | "RC3P Conformal Prediction" | Ch4 §4.2.2 — Shi et al. (2024) *is* RC3P | Content is right; add the citation *(Shi, 2024)* |
| Methodology (synthetic data) | "DINOV2-ViTB/24" | Ch4 §4.3.1: **ViT-B/14** | Typo — the patch size is 14 |
| If NOT Answered | "how ti looks" | — | "how it looks" |
| The Gap | `et. al.,` between two sources | — | Short form `*(Author, Year; Author, Year)*`, matching S3 |

`chapters/04-methodology/draft.md` §4.10.2 has already been amended to name the energy score as a
benchmarked alternative, so the first row is now safe to say out loud. The rest are deck-side only.
