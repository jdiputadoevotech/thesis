"""Render the synthetic text-crop corpus: pristine word crops plus degraded
look-alikes, one metadata row each (Table 1, Section 4.3.1).

The degradation operator D of Section 3.2.3 runs here, once, at render time.
Kerning jitter needs each glyph's advance width, which exists only while the
word is being typeset, so all three components are applied together and their
intensities logged per crop (Section 4.3.2). A crop is a pure function of
(font file, seed): any row regenerates bit-for-bit from its own metadata.

Stored crops are tight rectangles, the shape a word localizer emits at serving
time. Square-padding and the 224x224 resize live in the model's forward()
so training and serving share one preprocessing path (Section 4.3.2).

    .venv/bin/python src/data/render_corpus.py                      # full corpus
    .venv/bin/python src/data/render_corpus.py --per-font 5 --out /tmp/smoke
    .venv/bin/python src/data/render_corpus.py --check
"""

import argparse
import csv
import hashlib
import sys
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
WORDS = list(dict.fromkeys((ROOT / "src/data/words.txt").read_text().split()))

EM = 192            # render-time font size, px; every magnitude of D is a fraction of it
OUT_MAX = 224       # stored crop's longest side
MARGIN = 0.12       # crop margin around the ink, em
MIN_CONTRAST = 80   # fg/bg luminance gap, 0-255 (Chen et al., 2026)
FIELDS = ["image_id", "image_path", "font_id", "family_class", "word_text",
          "warp_level", "blur_level", "kern_level", "split", "seed", "tier"]

# Severity tiers are the stratification key of Section 4.3.2. Each theta is drawn
# independently inside the tier's range, so a crop's tier follows from its floats.
# Severe is capped at 0.90: above it the glyph is unrecoverable even to a human
# rater, and a labeled unrecoverable crop in validation only loosens tau. That
# regime is the unknown verdict's (Section 4.4.2), not a training class.
TIERS = {"pristine": (0.0, 0.0), "mild": (0.05, 0.35),
         "moderate": (0.35, 0.65), "severe": (0.65, 0.90)}
TIER_WEIGHTS = [0.15, 0.30, 0.30, 0.25]

# Operator D at theta = 1. Units are em unless stated.
WARP_AMP, WARP_SMOOTH = 0.10, 0.20   # displacement sd; smoothing sigma of the field
BLUR_SIGMA = 0.05                     # Gaussian blur sigma
NOISE_SIGMA = 25.0                    # additive noise sd on the 0-255 scale, post-downsample
KERN_JITTER, KERN_MIN = 0.15, -0.12   # per-gap jitter sd; tightest gap allowed


def luminance(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def pick_colors(rng):
    while True:
        fg, bg = rng.integers(0, 256, 3), rng.integers(0, 256, 3)
        if abs(luminance(fg) - luminance(bg)) >= MIN_CONTRAST:
            return tuple(int(v) for v in fg), tuple(int(v) for v in bg)


def sample_text(rng):
    n = int(rng.choice([1, 2, 3], p=[0.7, 0.2, 0.1]))
    words = [str(w) for w in rng.choice(WORDS, size=n, replace=False)]
    case = rng.choice(["lower", "title", "upper"], p=[0.4, 0.3, 0.3])
    words = [getattr(w, case)() for w in words]
    if n > 1 and rng.random() < 0.20:  # ~20% of multi-word crops wrap
        k = int(rng.integers(1, n))
        return words, [" ".join(words[:k]), " ".join(words[k:])]
    return words, [" ".join(words)]


def typeset(font, lines, align, kern, rng):
    """Glyph-by-glyph onto an L-mode mask. Pair-aware advances keep the font's
    own kerning at kern=0; jitter perturbs each gap on top of that."""
    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    tracking = kern * rng.uniform(-0.05, 0.15) * EM
    layouts = []
    for line in lines:
        xs, x, prev = [], 0.0, ""
        for ch in line:
            xs.append(x)
            adv = font.getlength(prev + ch) - font.getlength(prev) if prev else font.getlength(ch)
            gap = tracking + rng.normal(0, kern * KERN_JITTER * EM)
            x += adv + max(gap, KERN_MIN * EM)
            prev = ch
        layouts.append((xs, x))
    widest = max(w for _, w in layouts)
    pad = EM
    canvas = Image.new("L", (int(widest + 2 * pad), int(len(lines) * line_h + 2 * pad)), 0)
    draw = ImageDraw.Draw(canvas)
    for row, (line, (xs, w)) in enumerate(zip(lines, layouts)):
        x0 = pad + (widest - w) * {"left": 0.0, "center": 0.5, "right": 1.0}[align]
        y = pad + row * line_h + ascent
        for ch, x in zip(line, xs):
            draw.text((x0 + x, y), ch, font=font, fill=255, anchor="ls")
    return np.asarray(canvas)


def elastic_warp(mask, theta, rng):
    if theta == 0:
        return mask
    h, w = mask.shape
    amp, sig = theta * WARP_AMP * EM, WARP_SMOOTH * EM
    dx = cv2.GaussianBlur(rng.standard_normal((h, w), dtype=np.float32), (0, 0), sig)
    dy = cv2.GaussianBlur(rng.standard_normal((h, w), dtype=np.float32), (0, 0), sig)
    dx *= amp / (dx.std() + 1e-6)
    dy *= amp / (dy.std() + 1e-6)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    return cv2.remap(mask, xs + dx, ys + dy, cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def crop_to_ink(mask):
    # Threshold so a blur halo does not widen the margin with blur level.
    ys, xs = np.nonzero(mask > 32)
    m = int(MARGIN * EM)
    y0, y1 = max(ys.min() - m, 0), min(ys.max() + m + 1, mask.shape[0])
    x0, x1 = max(xs.min() - m, 0), min(xs.max() + m + 1, mask.shape[1])
    return mask[y0:y1, x0:x1]


def render_one(font, seed):
    """One crop and its Table 1 fields, fully determined by (font, seed)."""
    rng = np.random.default_rng(seed)
    tier = str(rng.choice(list(TIERS), p=TIER_WEIGHTS))
    lo, hi = TIERS[tier]
    warp, blur, kern = (rng.uniform(lo, hi, 3) if hi > 0 else np.zeros(3))
    words, lines = sample_text(rng)
    align = str(rng.choice(["left", "center", "right"]))
    fg, bg = pick_colors(rng)

    mask = typeset(font, lines, align, kern, rng)
    mask = elastic_warp(mask, warp, rng)
    if blur > 0:
        mask = cv2.GaussianBlur(mask, (0, 0), blur * BLUR_SIGMA * EM)
    mask = crop_to_ink(mask)

    # Stored as luminance: forward() reduces every input to this channel anyway
    # (Section 4.3.1), and single-channel PNGs are a third the size.
    alpha = mask.astype(np.float32) / 255.0
    img = alpha * luminance(fg) + (1 - alpha) * luminance(bg)
    img = Image.fromarray(img.round().astype(np.uint8), "L")
    scale = OUT_MAX / max(img.size)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))),
                     Image.LANCZOS)
    if blur > 0:
        arr = np.asarray(img, np.float32) + rng.normal(0, blur * NOISE_SIGMA, (img.height, img.width))
        img = Image.fromarray(np.clip(arr, 0, 255).round().astype(np.uint8), "L")

    meta = {"word_text": " ".join(words), "warp_level": round(float(warp), 4),
            "blur_level": round(float(blur), 4), "kern_level": round(float(kern), 4),
            "seed": seed, "tier": tier}
    return img, meta


def crop_seed(master, font_id, i):
    return int.from_bytes(hashlib.sha256(f"{master}:{font_id}:{i}".encode()).digest()[:4], "little")


def render_font(job):
    row, n, master, out = job
    font = ImageFont.truetype(str(ROOT / row["ttf_path"]), EM)
    (out / row["font_id"]).mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(n):
        image_id = f"{row['font_id']}_{i:04d}"
        path = out / row["font_id"] / f"{image_id}.png"
        img, meta = render_one(font, crop_seed(master, row["font_id"], i))
        img.save(path, optimize=True)
        rows.append({"image_id": image_id, "image_path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                     "font_id": row["font_id"], "family_class": row["family_class"], **meta})
    return rows


def assign_splits(rows, master, frac=(0.70, 0.15, 0.15)):
    """70/15/15, stratified by font and severity tier (Section 4.3.2)."""
    rng = np.random.default_rng(master)
    groups = {}
    for r in rows:
        groups.setdefault((r["font_id"], r["tier"]), []).append(r)
    for key in sorted(groups):
        g = groups[key]
        rng.shuffle(g)
        c1, c2 = round(len(g) * frac[0]), round(len(g) * (frac[0] + frac[1]))
        for i, r in enumerate(g):
            r["split"] = "train" if i < c1 else "validation" if i < c2 else "test"
    return rows


def build(palette, out, per_font, master, workers):
    fonts = list(csv.DictReader(palette.open()))
    jobs = [(f, per_font, master, out) for f in fonts]
    rows = []
    with Pool(workers) as pool:
        for i, batch in enumerate(pool.imap_unordered(render_font, jobs), 1):
            rows.extend(batch)
            print(f"[{i}/{len(fonts)}] {batch[0]['font_id']}", file=sys.stderr)
    rows = assign_splits(rows, master)
    rows.sort(key=lambda r: r["image_id"])
    with (out / "metadata.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return rows


def check():
    font = ImageFont.truetype(str(ROOT / "data/fonts/Roboto-400.ttf"), EM)
    rng = np.random.default_rng(0)
    for _ in range(200):
        fg, bg = pick_colors(rng)
        assert abs(luminance(fg) - luminance(bg)) >= MIN_CONTRAST
    a, ma = render_one(font, 12345)
    b, mb = render_one(font, 12345)
    assert np.array_equal(np.asarray(a), np.asarray(b)) and ma == mb, "not deterministic"
    assert max(a.size) == OUT_MAX and a.mode == "L", (a.size, a.mode)
    w0 = typeset(font, ["Kerning"], "left", 0.0, np.random.default_rng(1)).shape[1]
    w1 = typeset(font, ["Kerning"], "left", 1.0, np.random.default_rng(1)).shape[1]
    assert w0 != w1, "kern jitter had no effect on advance"
    m = typeset(font, ["warp"], "left", 0.0, rng)
    assert np.array_equal(elastic_warp(m, 0.0, rng), m), "warp at theta=0 must be identity"
    tiers = {render_one(font, s)[1]["tier"] for s in range(40)}
    assert tiers == set(TIERS), f"tiers seen: {tiers}"
    fake = [{"font_id": "F", "tier": t, "image_id": f"F_{i}"} for t in TIERS for i in range(100)]
    counts = {}
    for r in assign_splits(fake, 0):
        counts[r["split"]] = counts.get(r["split"], 0) + 1
    assert counts == {"train": 280, "validation": 60, "test": 60}, counts
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--palette", type=Path, default=ROOT / "data/palette.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "data/corpus")
    ap.add_argument("--per-font", type=int, default=575)  # Section 4.3.1 baseline
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    if args.check:
        check()
    else:
        rows = build(args.palette, args.out, args.per_font, args.seed, args.workers)
        print(f"{len(rows)} crops -> {args.out / 'metadata.csv'}")
