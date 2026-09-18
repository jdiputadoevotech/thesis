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
| ◐ | Corpus + metadata | Smoke-tested (80 fonts × 8, all TTFs load). **Full render runs off Matt's laptop** (Colab or the data-side machine, per §4.9.2): `python src/data/render_corpus.py` → `data/corpus/` + `metadata.csv` (Table 1 columns + `tier`, the stratification key; 70/15/15 by `(font_id, tier)`). Deterministic, so wherever it runs yields the same bytes given `palette.csv` + the pinned TTFs. | 2026-09-18 |
| ☐ | Mixed-font stressor set | Two palette fonts per line at controlled ratios; the only labeled ground truth for the homogeneity check (§4.10.2). | 2026-09-16 |

## Increment 2 — Metric embedding (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
| ☐ | Pull backbones | `facebook/dinov2-base`, `google/siglip-base-patch16-224`, `google/vit-base-patch16-224`, `facebook/convnext-tiny-224` (~2 GB total). | 2026-09-16 |
| ☐ | Preprocessing in `forward()` | Square-pad → 224² → grayscale ×3 → ImageNet norm. Verified identical train vs. serve (§4.10.1). | 2026-09-16 |
| ☐ | Teacher: DINOv2 + LoRA | r=8, α=16. Offline only, discarded after distillation. | 2026-09-16 |
| ☐ | Student: metric head `f_θ` | Triplet loss on labels + distillation from teacher. Frozen backbone. | 2026-09-16 |

## Increment 3 — Open-set decision and evaluation (§4.6.3)

| Status | Plan / experiment | Notes | Updated |
|--------|-------------------|-------|---------|
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
| ☑ | Decide training host | **Google Colab free tier (T4).** Training code is written CUDA-first; corpus ships to Drive; checkpoint every epoch against the 12h session cap. Data generation stays local on the M2. | 2026-09-16 |
| ☐ | Reconcile Python version | Table 2 (§4.8) pins 3.13; local pyenv runs 3.10.12. Change one so the reproducibility claim in §4.7.3 holds. | 2026-09-16 |
