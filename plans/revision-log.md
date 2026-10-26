# Revision log: changes since the proposal defense

Prepared 2026-10-26, after a full audit of the repo. The proposal defense was on 2026-08-03 and passed with minor revisions. This file is the source for the letter to the advisers: what changed, why, on what evidence, and which commit holds it. No experiment was re-run and no reported number changed; every fix below is a text, reference, or build correction.

## Fixes made 2026-10-26

| ID | Change | Where | Kind | Adviser sign-off | Commits |
|---|---|---|---|---|---|
| R1 | Chen et al. (2026) figures updated to arXiv v2 | Ch1 §1.2, Ch2 §2.2 and §2.6, Ch3 §3.4.3, Ch4 §4.1, `references.md` row 36, proposal deck and script | Factual correction | Inform | `71e1abe` `52066ef` `8d8d8b0` |
| R2 | Three cited sources added to the reference list | Bibliography | Documentation | Inform | `75c9464` |
| R3 | "Register-corrected" dropped from the backbone description | Ch1 Objective 2, Ch2 §2.5, Ch3 §3.4.2 | Alignment with what was built | Inform | `6c7770d` |
| R4 | Objective 4 reworded | Ch1 §1.4.2 | Alignment with the result | **Yes** | `059cb78` |
| R5 | "Benign failure" claim replaced by a measured proxy | Ch5 §5.3.2, `FINDINGS.md`, new script | Claim calibration | Inform | `18e5743` `50b98b2` |
| R6 | DeepFont author list | Ch2 §2.2 | Correction | None | `b4ad521` |
| R7 | Chapter number in the Ch6 notes heading | Ch6 notes | Housekeeping | None | `5a4ed41` |
| R8 | Final-paper build now includes Ch5 and Ch6 | `to_final_docx.py` | Build | None | `8c9f294` |

### R1. Chen et al. (2026) figures updated to arXiv v2

- **Before.** Ch1: a frozen ViT baseline "collapses to 40.2% family-level accuracy on non-synthetic input". Ch2: "roughly 86% Top-1", "about 0.2% of the backbone's parameters", family-level accuracy "collapsing to 40.2%", severity "errors costing 55% of a random baseline". Ch3: "roughly 150,000 parameters", "approximately 86%", "family-level accuracy falls to 40.2%". Ch4: expanding to 394 variants "dropped family-level accuracy to 40.2%".
- **After.** 99.0% Top-1 on the paper's own synthetic test set across 394 variants (32 families); about 1% of the backbone trainable (about 295,000 LoRA parameters plus a head); Π = 0.0069; family-level 99.4%. "Fails on photographs" became the authors' wording: trained and evaluated entirely on synthetic renders, and "may not generalize perfectly to photographs of printed text" or "heavily stylized graphics" (their §8). Ch4 now cites the paper's own finding that its remaining errors are overwhelmingly weight-variant confusions within a family.
- **Why.** We had read arXiv v1 (2026-02-14). The paper was revised on 2026-04-03 (v2) and the v1 numbers were superseded. We noticed on 2026-10-01 and recorded it in `references.md`, but the chapters were not updated, so Ch1–Ch4 disagreed with Ch5, which already used v2. Anyone opening the paper on arXiv sees v2.
- **Effect on the argument.** None of the thesis claims depends on the old numbers. "Pristine-trained models do not transfer to deformed crops" now rests on our own measurement (Ch5 §5.4.1, Table 12: the released Chen weights score 14.9% Top-1 on the 17 shared fonts and 11.1% unmasked). The palette-size argument in Ch4 keeps its Storia-AI evidence.
- **Evidence.** arXiv abstract page (v2): 99.0%, about 1% of 87.2M parameters, 394 variants in 32 families, "140× less severe than random guessing". v2 HTML: Table 2 (99.4% family-level; SWER 0.0054 against 0.7778 random, Π = 0.0069), §6.4, §8. Re-checked 2026-10-26.
- **The archived proposal deck and script** carried the same v1 numbers (`slides.md`, `script.md`). They were corrected in place; the version presented on 2026-08-03 is preserved in git history (before `8d8d8b0`).

### R2. Three cited sources added to the reference list

- **Before.** The reference list had 38 entries; `references.md` had 41 rows. Missing: Chen, Lowe & Zinn (2026), Hermans, Beyer & Leibe (2017), Hendrycks, Mazeika & Dietterich (2019). All three are cited in the chapters (Chen in Ch1–Ch5; Hermans and Hendrycks in Ch4 and Ch5).
- **After.** Entries added in APA 7, in the adviser-mandated groups: the two arXiv preprints under Web Articles, the ICLR paper under Conference Proceedings Articles.
- **Why.** Every in-text citation must have a matching entry.
- **Check.** A script compared every (surname, year) pair in Ch1–Ch5 with the list: 46 distinct pairs, none missing afterwards (two false hits, fixed in R6 or a regex artefact on "Sarker's").

### R3. "Register-corrected" dropped from the backbone description

- **Before.** Objective 2 and Ch2 §2.5 described a "frozen, register-corrected DINOv2 backbone". Ch3 §3.4.2 said the register repair "matters directly for glyph crops".
- **After.** Objective 2: "a frozen DINOv2 backbone". Ch2: registers remove artifact tokens "that appear in its larger variants". Ch3: the artifacts appear only in models of ViT-Large size and above, so the ViT-B/14 used here needs no registers.
- **Why.** The built encoder is `facebook/dinov2-base` (`src/model/encoder.py`), which has no registers, and Ch4–Ch5 never use them. Darcet et al. (2024), §2.1: "only the three largest models exhibit outliers"; Figure 4: "they appear with models larger than and including ViT-Large". Tiny, Small and Base show none, so the thesis promised a fix it does not need.
- **Effect.** Words only. The model and every result are unchanged. If an examiner asks why no registers: the paper reports none at Base size.

### R4. Objective 4 reworded (needs adviser sign-off)

- **Before.** "Verify each prediction with a re-render-and-compare typographic distance that is robust to geometric misalignment (Zhang et al., 2024) ..."
- **After.** "Evaluate a re-render-and-compare typographic distance (classical SSIM and the misalignment-tolerant DeepSSIM of Zhang et al., 2024) as a post-hoc check on each prediction ..."
- **Why.** Ch5 Table 14 shows DeepSSIM is not robust here: re-rendering the true font scores 0.485, 0.205, 0.087 at mild, moderate, severe deformation (SSIM 0.267, 0.059, 0.023), and DeepSSIM separates correct from wrong predictions no better than classical SSIM (AUROC 0.664 against 0.710). Ch4 was already softened on 2026-10-02 (`230bcfe`, `db89a49`); Ch1 still promised robustness.
- **Effect.** The objective now asks whether the check works, not that it works. The re-render check stays an offline diagnostic. This changes the wording of an objective that was defended, so the advisers should approve it.

### R5. "Benign failure" claim replaced by a measured proxy

- **Before.** Ch5 §5.3.2: for template reconstruction the failure mode "is benign ... an open-source substitute that is visually almost indistinguishable from the true font".
- **After.** The paragraph says harmlessness depends on how close the returned font is, that no human judgment was collected, and reports a structural proxy: of 2,710 wrongly accepted crops covered by the three most frequent matches per font, 2,018 (74.5%) went to a palette font of the unknown font's own structural family. Six fonts stay in family on every listed match; Courier Prime 23%, Special Elite 0%, Smooch Sans 24%, Bangers 39%.
- **Why.** The claim was an assertion, and Table 10 itself shows counterexamples (the monospace Courier Prime mostly maps to proportional slab serifs).
- **Evidence.** `src/model/family_match.py` reads the frozen test report and writes `reports/incr3/family_match.json`. It is descriptive and no design choice depends on it. Limit: the report keeps only the top three matches per font, so the share covers 62.3% of the 4,348 accepted crops.
- **Effect.** The open-set discussion is more cautious, and monospace and display faces are now stated as a limitation.

### R6, R7, R8

- **R6.** Ch2 §2.2 listed DeepFont's authors as "Wang, Yang, Jin, Shechtman, Aseem and Huang" (Aseem is Agarwala's first name). Now "Wang et al.'s (2015)". The reference-list entry was already correct.
- **R7.** `chapters/06-.../notes.md` was headed "Chapter 5".
- **R8.** `to_final_docx.py` stopped at Ch4, so Results and Discussion never reached the Word file. Ch5 is included; Ch6 is skipped with a notice until drafted. Test-built to a scratch file (pandoc and the layout pass ran clean); the tracked `Final Paper.docx` was not regenerated.

## Open decisions for the advisers

1. **Objective 4 wording** (R4): approve or propose alternative wording.
2. **Design drift between the RRL and the built system.** Ch2 §2.5 and §2.7 present non-negative contrastive features (Wang et al., 2024), trait-localized prompts (Chowdhury et al., 2025), label-free prompt distillation (Li, Li, et al., 2024) and logit-space rejection scores as the building blocks. The built system (Ch4, `src/model/`) uses a frozen DINOv2, a triplet metric head with LoRA-teacher distillation, outlier exposure and a prototype-cosine rejection score. Options: a short "design evolution" paragraph in Ch4, or reframe §2.5 and §2.7 as literature the design draws on. Not changed yet.
3. **SRS REQ-4.3-4** (the app should show an SSIM score) against Ch4 §4.4 (the re-render check is offline and the designer never sees it): keep one.
4. **Generators for the real-generative set.** Ch4 §4.3.1 names DALL·E, Midjourney and Stable Diffusion as examples; Ch5 §5.5.2 and the plan name Bing Image Creator, Gemini and ChatGPT Image. These render text well, so the severe tier may stay empty. The generation plan therefore adds SDXL (the model Ch1 cites at under 20% text accuracy), which Ch4's "Stable Diffusion" already covers; Ch5 §5.5.2 must list the generators actually used once the set exists. Also, the README removes boxes that are not text (localizer false positives) by hand and logs them, which Ch4 §4.3.1 ("every text box the localizer emits becomes one evaluation crop") should mention.
5. **Python version.** Ch4 Table 2 pins 3.13; the local environment runs 3.10.12. Needs the versions actually used on both machines.
6. **Document format.** `to_final_docx.py` produces 1.5 line spacing; the repo guidelines say double. Confirm against the department manual.
7. **Abstract** still says results are deferred; it is rewritten after Table 16 (real-generative results) exists.

## Earlier changes since the proposal defense (from git history)

- 2026-08-07 `fba6974`: methodology updated for mixed typography (panel question on regions with several fonts; word-level localization and a "mixed typography" verdict; SRS v1.2).
- 2026-10-01 `b52cf1c`, `fbb97da`: unknown-font set and mixed-font stressor set added (no synthetic set contained unknown fonts, so FPR could not be measured).
- 2026-10-01 `1dccace`, `0b4d9eb`: outlier-exposure head becomes the default model (Hendrycks et al., 2019); batch-all replaced batch-hard triplet mining after batch-hard collapsed (Ch5 §5.2.2).
- 2026-10-02 `6b32236`: homogeneity check rewritten; the patch-column design flagged no more mixed crops than its false-alarm rate, so a tuned cut search replaced it (Ch5 §5.3.3).
- 2026-10-02 `230bcfe`, `db89a49`: Ch4 no longer asserts the re-render metrics are deformation-robust; SAMScore dropped from the re-render check.
- 2026-10-02 `e2ab992`: SVC1 storage failure; final test numbers computed on the laptop with a parity check (Ch5 §5.1).
- 2026-10-04 `cbfa15b`: backbone comparison (Table 15) and latency; the CPU path misses REQ-5.1-1.
- 2026-10-05 `e7742ca`, 2026-10-24 `d583895`: real-generative evaluation pipeline and the expert-panel rater app.

## Not changed

- Chapter 5 tables and every reported number; the SRS; the model, weights and bundle; `Final Paper.docx`.
- Real-generative results (Table 16 stays placeholders until the panel has labelled).

## Letter outline

1. Update since the 2026-08-03 defense: Increments 1–3 complete; Ch5 drafted through §5.5.1; Table 16 and Ch6 depend on the expert panel.
2. Corrections to cited literature: R1, R2, R6.
3. Changes to match what was built and found: R3, R4 (approval requested), R5.
4. Questions: items 2–6 above.
5. Plan to the December defense: real-generative set and panel, web application, Chapter 6, final paper.
