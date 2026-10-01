"""Render the mixed-font stressor set: crops set in two palette fonts at once,
the labeled ground truth for the homogeneity check (Section 4.10.2).

No in-the-wild collection labels where one typeface ends and another begins,
so the check's detection rate, false-alarm rate and dispersion cutoff are all
measured here. Three kinds of mix, matching the cases of Section 4.4.2:

  word        whole words in font A, the rest in font B: composed typography,
              which the check should split at the word boundary
  char        one word switching from A to B mid-word at a controlled ratio:
              still a contiguous left/right boundary, so still splittable
  interleave  one word alternating A, B, A, B per character: no contiguous
              boundary, so the honest verdict is "mixed typography"

Every crop then goes through the same operator D as the main corpus, so the
check is tested under deformation, not only on clean renders. The boundary is
stored as a fraction of the crop width (`boundary_frac`), measured before the
elastic warp, which can shift it by up to ~0.1 em at the severe end.
`char_fonts` gives each character's font ("A", "B", or "-" for a space).
Single-font negatives are the main corpus itself.

Crops split 50/50 by index: validation calibrates the cutoff, test reports it.

    .venv/Scripts/python.exe src/data/render_mixed.py                 # 4,000 crops
    .venv/Scripts/python.exe src/data/render_mixed.py --n 40 --out /tmp/mixed
    .venv/Scripts/python.exe src/data/render_mixed.py --check
"""

import argparse
import csv
import sys
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from render_corpus import (EM, KERN_JITTER, KERN_MIN, MARGIN, NOISE_SIGMA, OUT_MAX, ROOT, TIER_WEIGHTS,
                           TIERS, BLUR_SIGMA, WORDS, crop_seed, elastic_warp, luminance, pick_colors)

MIXES = {"word": 0.4, "char": 0.4, "interleave": 0.2}
RATIOS = [0.25, 0.5, 0.75]  # share of a char-mix word set in font B
FIELDS = ["image_id", "image_path", "font_a", "font_b", "family_a", "family_b", "mix", "word_text",
          "char_fonts", "boundary_frac", "warp_level", "blur_level", "kern_level", "tier", "seed", "split"]

_fonts = {}


def font(row):
    if row["font_id"] not in _fonts:
        _fonts[row["font_id"]] = ImageFont.truetype(str(ROOT / row["ttf_path"]), EM)
    return _fonts[row["font_id"]]


def sample_mix(rng):
    """Text plus a per-character A/B assignment for one of the three mixes."""
    mix = str(rng.choice(list(MIXES), p=list(MIXES.values())))
    case = str(rng.choice(["lower", "title", "upper"], p=[0.4, 0.3, 0.3]))
    long_words = [w for w in WORDS if len(w) >= 5]
    if mix == "word":
        words = [getattr(str(w), case)() for w in rng.choice(WORDS, size=int(rng.choice([2, 3])), replace=False)]
        k = int(rng.integers(1, len(words)))
        labels = "-".join(("A" if i < k else "B") * len(w) for i, w in enumerate(words))
        return mix, " ".join(words), labels
    word = getattr(str(rng.choice(long_words)), case)()
    if mix == "char":
        j = min(max(1, round(len(word) * (1 - float(rng.choice(RATIOS))))), len(word) - 1)
        return mix, word, "A" * j + "B" * (len(word) - j)
    return mix, word, "".join("AB"[i % 2] for i in range(len(word)))


def typeset_mixed(fa, fb, text, labels, kern, rng):
    """One line, glyph by glyph, each glyph in its own font. The font's pair
    kerning applies only between two glyphs of the same font. Returns the mask
    and the A->B boundary x on it (None when the fonts interleave)."""
    fonts = {"A": fa, "B": fb, "-": fa}
    ascent = max(f.getmetrics()[0] for f in (fa, fb))
    descent = max(f.getmetrics()[1] for f in (fa, fb))
    tracking = kern * rng.uniform(-0.05, 0.15) * EM
    xs, x, prev, prev_lab, ends = [], 0.0, "", "", []
    for ch, lab in zip(text, labels):
        f = fonts[lab]
        xs.append(x)
        same = prev and prev_lab == lab
        adv = f.getlength(prev + ch) - f.getlength(prev) if same else f.getlength(ch)
        ends.append(x + adv)
        x += adv + max(tracking + rng.normal(0, kern * KERN_JITTER * EM), KERN_MIN * EM)
        prev, prev_lab = ch, lab
    pad = EM
    canvas = Image.new("L", (int(x + 2 * pad), int(ascent + descent + 2 * pad)), 0)
    draw = ImageDraw.Draw(canvas)
    for ch, lab, cx in zip(text, labels, xs):
        draw.text((pad + cx, pad + ascent), ch, font=fonts[lab], fill=255, anchor="ls")
    boundary = None
    flat = labels.replace("-", "")
    if "AB" in flat and "BA" not in flat:  # one contiguous A run, then one B run
        last_a = max(i for i, lab in enumerate(labels) if lab == "A")
        first_b = labels.index("B")
        boundary = pad + (ends[last_a] + xs[first_b]) / 2
    return np.asarray(canvas), boundary


def render_one(fa_row, fb_row, seed):
    rng = np.random.default_rng(seed)
    tier = str(rng.choice(list(TIERS), p=TIER_WEIGHTS))
    lo, hi = TIERS[tier]
    warp, blur, kern = (rng.uniform(lo, hi, 3) if hi > 0 else np.zeros(3))
    mix, text, labels = sample_mix(rng)
    fg, bg = pick_colors(rng)

    mask, bx = typeset_mixed(font(fa_row), font(fb_row), text, labels, kern, rng)
    mask = elastic_warp(mask, warp, rng)
    if blur > 0:
        mask = cv2.GaussianBlur(mask, (0, 0), blur * BLUR_SIGMA * EM)
    ys, xs = np.nonzero(mask > 32)
    m = int(MARGIN * EM)
    y0, y1 = max(ys.min() - m, 0), min(ys.max() + m + 1, mask.shape[0])
    x0, x1 = max(xs.min() - m, 0), min(xs.max() + m + 1, mask.shape[1])
    mask = mask[y0:y1, x0:x1]

    alpha = mask.astype(np.float32) / 255.0
    img = Image.fromarray((alpha * luminance(fg) + (1 - alpha) * luminance(bg)).round().astype(np.uint8), "L")
    scale = OUT_MAX / max(img.size)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    if blur > 0:
        arr = np.asarray(img, np.float32) + rng.normal(0, blur * NOISE_SIGMA, (img.height, img.width))
        img = Image.fromarray(np.clip(arr, 0, 255).round().astype(np.uint8), "L")

    meta = {"font_a": fa_row["font_id"], "font_b": fb_row["font_id"], "family_a": fa_row["family_class"],
            "family_b": fb_row["family_class"], "mix": mix, "word_text": text, "char_fonts": labels,
            "boundary_frac": "" if bx is None else round((bx - x0) / (x1 - x0), 4),
            "warp_level": round(float(warp), 4), "blur_level": round(float(blur), 4),
            "kern_level": round(float(kern), 4), "tier": tier, "seed": seed}
    return img, meta


def render_range(job):
    lo, hi, fonts, master, out = job
    rows = []
    for i in range(lo, hi):
        seed = crop_seed(master, "mixed", i)
        a, b = np.random.default_rng(seed).choice(len(fonts), size=2, replace=False)
        img, meta = render_one(fonts[a], fonts[b], seed)
        path = out / f"mixed_{i:05d}.png"
        img.save(path, optimize=True)
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        rows.append({"image_id": f"mixed_{i:05d}", "image_path": rel, **meta,
                     "split": "validation" if i % 2 == 0 else "test"})
    return rows


def build(palette, out, n, master, workers):
    fonts = list(csv.DictReader(palette.open()))
    out.mkdir(parents=True, exist_ok=True)
    step = 100
    jobs = [(lo, min(lo + step, n), fonts, master, out) for lo in range(0, n, step)]
    rows = []
    with Pool(workers) as pool:
        for i, batch in enumerate(pool.imap_unordered(render_range, jobs), 1):
            rows.extend(batch)
            print(f"[{i}/{len(jobs)}]", file=sys.stderr)
    rows.sort(key=lambda r: r["image_id"])
    with (out / "metadata.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return rows


def check():
    fonts = {r["font_id"]: r for r in csv.DictReader((ROOT / "data/palette.csv").open())}
    a, b = fonts["Roboto-400"], fonts["AbrilFatface-400"]
    i1, m1 = render_one(a, b, 777)
    i2, m2 = render_one(a, b, 777)
    assert np.array_equal(np.asarray(i1), np.asarray(i2)) and m1 == m2, "not deterministic"
    assert max(i1.size) == OUT_MAX and i1.mode == "L"
    seen = {}
    for s in range(300):
        _, m = render_one(a, b, s)
        seen.setdefault(m["mix"], []).append(m)
        assert len(m["char_fonts"]) == len(m["word_text"]), m
        if m["mix"] == "interleave":
            assert m["boundary_frac"] == "", m
        else:
            assert 0.0 < m["boundary_frac"] < 1.0, m
    assert set(seen) == set(MIXES), seen.keys()
    # The boundary must sit where the text says: left of center when B covers most of the word.
    rng = np.random.default_rng(0)
    _, bx_early = typeset_mixed(font(a), font(b), "fonting", "ABBBBBB", 0.0, rng)
    _, bx_late = typeset_mixed(font(a), font(b), "fonting", "AAAAAAB", 0.0, rng)
    assert bx_early < bx_late, (bx_early, bx_late)
    _, none = typeset_mixed(font(a), font(b), "fonting", "ABABABA", 0.0, rng)
    assert none is None
    print("ok", {k: len(v) for k, v in seen.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--palette", type=Path, default=ROOT / "data/palette.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "data/corpus_mixed")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    if args.check:
        check()
    else:
        rows = build(args.palette, args.out, args.n, args.seed, args.workers)
        print(f"{len(rows)} crops -> {args.out / 'metadata.csv'}")
