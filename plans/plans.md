# Plans (tasks & experiments)

Status: ☐ todo · ◐ in progress · ☑ done

## Critical path to the December defense (audit of 2026-10-26)

What the audit found and what was already fixed is in `plans/revision-log.md`. Real-generative results, Ch6 and the web app are the open work.

| Status | Task | Notes | Updated |
|--------|------|-------|---------|
| ☐ | Contact the 3 expert raters | Fill the letters (`chapters/appendices/srs/Transmittal Letter - *.md` still hold `<Position>`, `<Address>`, `<estimated time>`), add a consent and data-privacy paragraph to the rating form, check whether USC requires ethics clearance, then send. The panel is the long pole: Table 16, Ch5 §5.5.2 and Ch6 (RQ4) wait on it. | 2026-10-26 |
| ◐ | Generate the real-generative images | Tooling done: `src/data/generate_real.py`, plan in `data/real/plan.csv` (84 images: 60 SDXL, 12 ChatGPT, 12 Gemini; Bing dropped 2026-10-28), steps in `data/real/README.md`. Done: the 60 SDXL images (Colab T4, 2026-10-28; garbled text confirmed on the pilot). Left: the 24 ChatGPT and Gemini images through `generate_real.py api` (model ids and a one-image trial first), then `intake`, `real.py localize` and `generate_real.py select`. | 2026-10-28 |
| ◐ | Fix and host the rater app for remote raters | Identity fix built and self-tested 2026-10-28 (`server.py`: links, consent, audit chain, receipts, hidden controls; `Gate.jsx`; see `src/rater/README.md`). Left: run `tokens` and `controls`, host it (tunnel) with the 100-crop set, a dry run with a friend, send the letters and links, collect receipts. | 2026-10-28 |
| ☐ | Dry-run `real.py` end to end | localize → sheet → predict → score on a handful of images before the raters start. `predict` has never run on real crops. On the Mac pass `--no-gpu`. | 2026-10-26 |
| ☐ | Increment 4 detail | Gate the homogeneity search behind a middle-cut probe on CPU (3 passes instead of 15; FINDINGS 11b: middle-only detects 46.4% against 43.5%) and re-measure detection with the gate. Build the image in GitHub Actions (x86), since SVC1 is aarch64. Triage by SRS priority: High first, Docker (Med) last. | 2026-10-26 |
| ☐ | Draft Ch6 | RQs 1–3 and 5 can be answered from the synthetic results now; RQ4 after Table 16. `to_final_docx.py` picks the draft up automatically. | 2026-10-26 |
| ☐ | Rewrite the abstract | Still says results are deferred. After Table 16. | 2026-10-26 |
| ☐ | Strengthen Ch5 (cheap, on cached features) | (a) a control trained on pristine crops only; (b) AUROC of the model's own top-1 similarity as a correct-vs-wrong detector, against re-render SSIM 0.710; (c) bootstrap CIs on test metrics (resample crops; resample fonts for FPR@95); (d) a qualitative figure (tier examples with Top-3; Cormorant → Cormorant Garamond, Courier Prime → Arvo); (e) a threats-to-validity subsection. | 2026-10-26 |
| ☐ | Ch4 housekeeping | Table 2 says Python 3.13, the venv runs 3.10.12; the 4.x subfolder drafts duplicate `draft.md` (pick one source of truth); SRS REQ-4.3-4 against §4.4. | 2026-10-26 |
| ☐ | Paperwork | Line spacing (1.5 or double) against the department manual; AI-use disclosure rules (USC and IEEE); regenerate `Final Paper.docx` once Ch5 and Ch6 are final. | 2026-10-26 |
| ☐ | Final defense: deck, script, Q&A | Only the proposal deck exists. The oral exam is 50% and individual: both members must be able to explain every Ch5 number and every Ch3 equation. | 2026-10-26 |
| ☐ | Back up trained weights and features | `data/models/` (20 models) and `data/features/` live only on the RTX 3050 laptop; only `models/font_recognizer.pt` is in git. Copy them off and record checksums. | 2026-10-26 |
| ☐ | Repo privacy | `07 - CABARRUBIAS & DIPUTADO/` (33 files: CVs, signed approval sheet, agreement letters, consultation logs) is tracked in a public repo. Decide: make the repo private, or untrack and purge history (force-push; needs both members). | 2026-10-26 |
| ☐ | Letter to the advisers | Draft from `plans/revision-log.md`. | 2026-10-26 |
| ☐ | Conference paper | Venues and costs in `plans/conference-targets.md`; real results will not exist before mid-November. | 2026-10-26 |

## Parallel track — start immediately, blocks Chapter 5

These depend on no code. Their lead time, not the build, is the schedule risk.

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☐ | Recruit 3 expert raters | Typography/design professionals, screened per §4.2.3. 300 judgments total. Recruiting is the long pole. | 2026-09-16 |
| ☐ | Collect real-generative images | Generators: SDXL, Gemini, ChatGPT Image (Bing Image Creator dropped 2026-10-28: no API, and it adds no model family, since it runs an OpenAI model). Purposive quota: 4 family classes × mild→severe hallucination. Localize to N=100 word crops. **Risk: all three render text comparatively well, so the severe end of the severity quota will be hard to fill — see prompting note below.** | 2026-09-16 |
| ◐ | Prompt recipes for severe hallucination | The quota needs failures, and modern generators mostly succeed on short focal text. Push toward failure with: long/rare/invented words, small or background text (signage, packaging, book spines), curved or textured surfaces, several text elements in one image, and explicitly display/ornamental type. Log the prompt with every crop. Encoded in `src/data/generate_real.py` (TEXTS, SCENES); untested until the first images exist, so pilot 5 severe prompts first. | 2026-10-26 |
| ☑ | Build rater web form | `src/rater/` (React + Vite frontend + `server.py` backend). Per-crop item + live 80-font `@font-face` palette reference sheet + coherence question (§4.2.3, Appendix B). Writes directly to `data/real/labels.csv`. | 2026-10-19 |
| ☑ | ~~Re-clone `font-classify`~~ not needed | `src/model/baselines.py` downloads both baselines from the Hugging Face Hub (`storia/font-classify-onnx`, `dchen0/font_classifier_v4`), so `real.py predict` runs without the sandbox. Read from the code on 2026-10-26; not yet run on real crops. | 2026-10-26 |

## Increment 1 — Synthetic data pipeline (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☑ | Freeze palette | `src/data/build_palette.py` → `data/palette.csv`. 80 fonts, one weight (400) each; quota 32 sans / 24 serif / 16 display / 8 mono. TTFs pinned by SHA256 + GF version URL. | 2026-09-16 |
| ☑ | Fixed word list | `src/data/words.txt`, ~400 common English words, shared across all fonts (§4.3.1). Word count per crop 70/20/10 for 1/2/3 words; case lower/Title/UPPER. | 2026-09-18 |
| ☑ | Renderer | `src/data/render_corpus.py`. Pillow glyph-by-glyph at 192 px em → tight ink crop → longest side 224. Colors sampled RGB with contrast ≥ 80, stored as luminance (forward() grayscales anyway; 3× smaller). Alignment jitter, ~20% wrap. ~12 KB/crop → ~540 MB for 46k. 8 cores: ~18 min full run. | 2026-09-18 |
| ☑ | Degradation operator `D` | In `render_corpus.py`, applied once at render time (see §4.3.2 edit). Kerning: per-gap jitter + tracking on pair-aware advances. Warp: smoothed random displacement field via `cv2.remap`. Blur on the ink mask, noise after downsample. Four severity tiers (pristine 15% / mild 30% / moderate 30% / severe 25%), each θ drawn independently within the tier. Severe capped at θ = 0.90 after inspecting a 40-crop severe sheet: above it glyphs are unrecoverable to a human, and labeled mush in validation only loosens τ (raises FPR@95TPR). Knobs if retuning: `WARP_AMP`, `BLUR_SIGMA`, `NOISE_SIGMA`, `TIERS`. | 2026-09-18 |
| ☑ | Corpus + metadata | `data/corpus/` + `metadata.csv`: 46,000 crops (80 × 575), Table 1 columns + `tier`, 70/15/15 by `(font_id, tier)`. Deterministic: spot-checked crops re-render byte-identical. | 2026-10-01 |
| ☑ | Mixed-font stressor set | `src/data/render_mixed.py` → `data/corpus_mixed/` (4,000 crops). Two palette fonts per crop: by whole word (40%), mid-word at 25/50/75% (40%), or interleaved per character (20%), then operator D. Records each character's font (`char_fonts`) and the A→B boundary as a fraction of crop width (none for interleave). 50/50 validation/test by index. Labeled ground truth for the homogeneity check. | 2026-10-01 |

## Increment 2 — Metric embedding (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☑ | Pull backbones | Only `facebook/dinov2-base` pulled so far. `src/model/encoder.py` takes `--backbone`, so the other three (SigLIP, ViT, ConvNeXt) are one flag each in Increment 3's comparison. Note: SigLIP/ViT use their own ±1 normalization, not ImageNet. | 2026-09-22 |
| ☑ | Preprocessing in `forward()` | `Preprocess` in `encoder.py`: square-pad (border-median fill) → 224² bilinear → grayscale ×3 → per-backbone norm. Skew test in `train_head.py --check` passes: served `FontEmbedder` on raw PNGs reproduces the cached path, min cosine 1.00000 over 20 val crops (§4.10.1). | 2026-09-22 |
| ☑ | Feature cache | `src/model/cache_features.py`. Backbone is frozen and each crop's deformation is fixed, so features are computed once: `data/features/dinov2.npz` (46k × 1536, 146 MB, ~8 min). Head training then costs ~2 min instead of hours. | 2026-09-22 |
| ☑ | Teacher: DINOv2 + LoRA | `src/model/train_teacher.py`. r=8, α=16 on query+value, dropout 0.1 = 294,912 trainable params (Chen et al.'s config; their v1 said ~150K, corrected to ~295K in v2 — see `references.md` row 36). **10 epochs** (default): val Top-1 34.2 → **64.2%**, plateaued by epoch 8 (`reports/incr2/teacher10.json`, SVC1). The earlier 5-epoch laptop teacher reached 60.2%. A 4-point better teacher lifted the student only 0.3 points: the frozen features, not the teacher, now bound the student. | 2026-10-01 |
| ☑ | Student: metric head `f_θ` | `src/model/train_head.py`. [LayerNorm → 1536→512 → GELU → 512→256, L2-norm], batch-all triplet (batch-hard collapsed; Hermans et al., 2017), margin 0.2. **Tuned defaults: 120 epochs, P=16 × K=8, KD weight 0.5**, picked on validation by the one-knob sweep (`src/model/sweep.py` → `reports/incr2/sweep.json`; margin, lr and head size made no difference). Val Top-1 on SVC1: defaults 41.06% → tuned 43.41% → + 10-epoch teacher **43.70%** (Top-3 65.6%, family 88.1%). **5-fold CV: 43.79% ± 0.33** Top-1, Top-3 66.4%, family 88.4% (`dinov2_cv.json`). KD ablation, same settings: 40.41% without vs 43.70% with (+3.3; `dinov2_nokd.json`). The severe tier stayed at ~23% under every setting. `dinov2_combo.json` = tuned head with the 5-epoch teacher (43.41%). | 2026-10-01 |
| ☑ | Separability evidence | `reports/incr2/*.json` (committed) + Figure `assets/figures/embedding_tsne.png` from `src/visualization/embedding_tsne.py`: frozen vs. head t-SNE, colored by family. Serif/display/mono separate under the head; families are intermixed without it. | 2026-09-22 |

## Increment 3 — Open-set decision and evaluation (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☑ | Unknown-font set | Gap found 2026-10-01: §4.10.2 measured FPR on "out-of-palette crops" but no synthetic set had any. `build_palette.py --unknown` → `data/unknown.csv`: the next 20 fonts below the palette cutoff (8/6/4/2), symbol faces excluded. Split by font: 10 validation (model choice), 10 test (Ch5). `data/corpus_unknown/`, 11,500 crops. Ch4 §4.3.1 + §4.10.2 updated. | 2026-10-01 |
| ☑ | Last-layer vs multi-layer head, open-set | Multi-layer wins on the open-set measure too: FPR@95 87.1% vs 92.2%, AUROC 0.654 vs 0.614 (validation). Adopted, then outlier exposure added (40 background fonts, 128/batch, margin 0.4): FPR 75.3 ± 2.4% over 3 seeds. `reports/incr3/FINDINGS.md` 1–8. | 2026-10-04 |
| ☑ | Prototypes + calibrate τ | `src/model/open_set.py`: per-font mean training embedding; τ at 95% recall on known validation crops; `--final` scores test with that τ. | 2026-10-04 |
| ☑ | Homogeneity check | The patch-column design failed (chance-level). Replaced by a cut search with the font embedding (`src/model/homogeneity.py`, cuts 35–65%, pieces ≥ 1.25× crop height, per-cut z): test 45.7% of contiguous two-font crops at 5.4% false alarm. §4.4.2 rewritten. | 2026-10-04 |
| ☑ | Metrics | Top-1/Top-3, FPR@95, AUROC, family confusion, severity Π (Chen et al. definition), split-conformal Top-K (`open_set.py`); re-render SSIM / DeepSSIM (`rerender.py`). **Final test numbers frozen 2026-10-02** (FINDINGS, "Final test results"). | 2026-10-04 |
| ☑ | Backbone comparison | Final recipe, last-layer features for all four (laptop, 2026-10-04). Test Top-1: DINOv2 41.0%, ConvNeXt-T 33.8%, ViT 32.7%, SigLIP 26.0%; DINOv2 also best on FPR (80.3%). Latency per crop GPU/CPU: final model 26/332 ms, ConvNeXt 14/98 ms. **CPU-only demo misses SRS REQ-5.1-1** once the homogeneity check's 14 extra passes are counted (~25 s for 5 regions): decide in Increment 4. FINDINGS "Backbone comparison". | 2026-10-04 |
| ◐ | Baseline comparison | **Synthetic done** (test: ours 51.4% vs Storia-AI 21.2% on 77 fonts; ours 57.8% vs Chen et al. 14.9% on 17). **Real-generative crops still open:** blocked on the panel-labeled set. | 2026-10-04 |

## Increment 4 — Web application (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☑ | FastAPI `/predict` | `src/app/server.py`: typed contract, weights and localizer loaded once, stateless; 415/400/413/no-text cases and determinism pass `--check`. Capped at 12 regions (largest first) and 2048 px. CPU latency on the M2: 30 s for 10 regions with the two-typeface check, 10 s without, so REQ-5.1-1 still needs the probe gate (Increment 4 detail) or a GPU. | 2026-10-29 |
| ◐ | EasyOCR localizer wrapper | Word-granularity boxes done (the same `boxes_to_crops` the evaluation uses). Merging adjacent same-verdict words in the UI is not built. | 2026-10-29 |
| ☑ | React + Vite frontend | `src/app/src`: boxes over the image, a card per region with live previews in the real Google Font, unknown folded away, mixed split in two. Checked headless against real SDXL and ChatGPT images. | 2026-10-29 |
| ☐ | Docker image | Single host, no external deps at inference beyond bundled weights and fonts. | 2026-09-16 |

## Environment issues

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☐ | Free disk space | 10 GB free of 228 GB (96% full). Corpus ~0.5 GB + backbones ~2 GB + EasyOCR ~0.1 GB fits, but with no margin. Colab moves the backbones off the laptop, which buys most of it back. | 2026-09-16 |
| ☑ | Train on SVC1 | DCISM GB10 server (aarch64, Blackwell) via `scripts/svc1.sh` (sync/data/setup/run/log/jobs/pull). Server torch 2.14.0+cu130, laptop torch 2.6.0+cu124: each machine is deterministic but they differ (same head: 40.50% laptop vs 41.06% server). **Server runs are canonical from 2026-09-30**; don't mix the two in one table. Server outbound internet is closed at night (SSH still works), and SSH is blocked from some campus networks. GPU is shared, so speed varies. | 2026-10-01 |
| ⚠ | SVC1 storage failure (2026-10-02) | Server rebooted 02:32, 09:03, 09:06, 09:46; then installed files corrupted (torch import segfault, numpy 'bad marshal data'), a job died with heap corruption, and reads return `OSError: [Errno 5] Input/output error`. **Do not trust new SVC1 results until the admin confirms the disk is repaired.** Rescued to the laptop, checksum-verified: all 20 models in `data/models/` (incl. final head and teacher10) and features teacher10, dinov2_mid_background, dinov2_mid_unknown, dinov2_unknown. Unreadable on the server, regenerable from the laptop corpus: dinov2_mid, dinov2_mid_mixed, dinov2_mixed, dinov2_mid_background_x3. Committed results (reports/) were all produced before the corruption appeared and verified bit-identical after the torch reinstall. | 2026-10-02 |
| ☑ | Decide training host | **Google Colab free tier (T4).** Training code is written CUDA-first; corpus ships to Drive; checkpoint every epoch against the 12h session cap. Data generation stays local on the M2. | 2026-09-16 |
| ☐ | Reconcile Python version | Table 2 (§4.8) pins 3.13; local pyenv runs 3.10.12. Change one so the reproducibility claim in §4.7.3 holds. | 2026-09-16 |
