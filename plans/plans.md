# Plans (tasks & experiments)

Status: ☐ todo · ◐ in progress · ☑ done

## Parallel track — start immediately, blocks Chapter 5

These depend on no code. Their lead time, not the build, is the schedule risk.

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☐ | Recruit 3 expert raters | Typography/design professionals, screened per §4.2.3. 300 judgments total. Recruiting is the long pole. | 2026-09-16 |
| ☐ | Collect real-generative images | Three generators: Bing Image Creator (DALL·E 3), Gemini, ChatGPT Image. Purposive quota: 4 family classes × mild→severe hallucination. Localize to N=100 word crops. **Risk: all three render text comparatively well, so the severe end of the severity quota will be hard to fill — see prompting note below.** | 2026-09-16 |
| ☐ | Prompt recipes for severe hallucination | The quota needs failures, and modern generators mostly succeed on short focal text. Push toward failure with: long/rare/invented words, small or background text (signage, packaging, book spines), curved or textured surfaces, several text elements in one image, and explicitly display/ornamental type. Log the prompt with every crop. | 2026-09-16 |
| ☐ | Build rater web form | Per-crop item + palette reference sheet + coherence question (§4.2.3). Appendix-reproducible, platform-neutral. | 2026-09-16 |
| ☐ | Re-clone `font-classify` | Storia-AI baseline (§4.10.2); sandbox is absent from disk. | 2026-09-16 |

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
| ☐ | Last-layer vs multi-layer head, open-set | **First Increment 3 run.** Both heads were chosen on closed-set Top-1 only (Increment 2). Compare FPR@95% recall on the unknown-font *validation* fonts before adopting blocks 3/6/9/12 as the default. Features cached on SVC1: `{dinov2,dinov2_mid}_{unknown,mixed}.npz`. | 2026-10-01 |
| ☐ | Prototypes + calibrate τ | Per-font centroid over training crops; τ at 95% recall on validation (§4.4.2 step 8). | 2026-09-16 |
| ☐ | Homogeneity check | Column-pooled patch tokens, 2-cluster dispersion cutoff, single contiguous split, mixed-typography verdict. | 2026-09-16 |
| ☐ | Metrics | Top-1/Top-3, FPR@95%TPR, structural re-render distance, conformal coverage, centroid severity index, confusion matrix by family. | 2026-09-16 |
| ☐ | Backbone comparison | Table 5 candidates, same corpus and calibration recipe. Per-crop CPU/GPU latency on the deployment machine. | 2026-09-16 |
| ☐ | Baseline comparison | Storia-AI + Chen et al. DINOv2-LoRA on the same real-generative crops. | 2026-09-16 |

## Increment 4 — Web application (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☐ | FastAPI `/predict` | Pydantic contract, weights loaded once at startup, stateless. | 2026-09-16 |
| ☐ | EasyOCR localizer wrapper | Word-granularity boxes; adjacent same-verdict words merged in the UI. | 2026-09-16 |
| ☐ | React + Vite frontend | Upload → per-region Top-K cards with live font previews, or unknown / mixed-typography verdict. | 2026-09-16 |
| ☐ | Docker image | Single host, no external deps at inference beyond bundled weights and fonts. | 2026-09-16 |

## Environment issues

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☐ | Free disk space | 10 GB free of 228 GB (96% full). Corpus ~0.5 GB + backbones ~2 GB + EasyOCR ~0.1 GB fits, but with no margin. Colab moves the backbones off the laptop, which buys most of it back. | 2026-09-16 |
| ☑ | Train on SVC1 | DCISM GB10 server (aarch64, Blackwell) via `scripts/svc1.sh` (sync/data/setup/run/log/jobs/pull). Server torch 2.14.0+cu130, laptop torch 2.6.0+cu124: each machine is deterministic but they differ (same head: 40.50% laptop vs 41.06% server). **Server runs are canonical from 2026-09-30**; don't mix the two in one table. Server outbound internet is closed at night (SSH still works), and SSH is blocked from some campus networks. GPU is shared, so speed varies. | 2026-10-01 |
| ⚠ | SVC1 storage failure (2026-10-02) | Server rebooted 02:32, 09:03, 09:06, 09:46; then installed files corrupted (torch import segfault, numpy 'bad marshal data'), a job died with heap corruption, and reads return `OSError: [Errno 5] Input/output error`. **Do not trust new SVC1 results until the admin confirms the disk is repaired.** Rescued to the laptop, checksum-verified: all 20 models in `data/models/` (incl. final head and teacher10) and features teacher10, dinov2_mid_background, dinov2_mid_unknown, dinov2_unknown. Unreadable on the server, regenerable from the laptop corpus: dinov2_mid, dinov2_mid_mixed, dinov2_mixed, dinov2_mid_background_x3. Committed results (reports/) were all produced before the corruption appeared and verified bit-identical after the torch reinstall. | 2026-10-02 |
| ☑ | Decide training host | **Google Colab free tier (T4).** Training code is written CUDA-first; corpus ships to Drive; checkpoint every epoch against the 12h session cap. Data generation stays local on the M2. | 2026-09-16 |
| ☐ | Reconcile Python version | Table 2 (§4.8) pins 3.13; local pyenv runs 3.10.12. Change one so the reproducibility claim in §4.7.3 holds. | 2026-09-16 |
