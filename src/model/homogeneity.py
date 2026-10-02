"""Homogeneity check: is a crop set in one typeface, or two?

Two methods. `columns` is the design Section 4.4.2 first specified; it does
not work (reports/incr3/FINDINGS.md, finding 9) and is kept as the record of
that result. `search` is its replacement:

  search  cut the crop at each of CUTS (fractions of its width), embed the
          left and right pieces with the trained font head, and take the
          cosine distance between them. The crop is flagged when the largest
          distance clears a cutoff (5% false alarm on single-font validation
          crops); the cut with that distance is the boundary. Each piece costs
          one encoder pass, so the check is 2 x len(CUTS) extra passes per crop.
          It looks only for one left/right boundary: an interleaved crop has
          no single cut that separates its fonts, so its detection is measured
          but not expected.

The `columns` method, as first designed:

Section 4.4.2. A 224x224 crop reaches DINOv2 as a 16 x 16 grid of patch
tokens. Empty patches (padding, gaps) are left out, the rest are pooled by
grid column into a left-to-right style profile, and the column profiles are
split into two clusters. The dispersion is the cosine distance between the
two cluster means. Above a calibrated cutoff the crop is flagged:
  - the two clusters form one contiguous left run and one right run -> a
    boundary exists, at a column mapped back to a fraction of the crop width;
  - the clusters interleave -> per-letter drift, "mixed typography".
Below the cutoff the crop is treated as one typeface.

The cutoff follows the tau recipe: the dispersion that 95% of single-font
validation crops stay under (a 5% false-alarm rate). Ground truth comes from
the mixed-font stressor set (src/data/render_mixed.py).

Empty patches can be found two ways, and both are computed so validation
data can choose: by the CLS token's attention (the chapter's wording), or by
ink pixels in the prepared crop. DINOv2 without registers is known to park
high-attention artifact tokens on empty background (Darcet et al., 2024),
which can make the attention mask unreliable.

    .venv/bin/python src/model/homogeneity.py cache       # columns: patch profiles, ~10 min on SVC1
    .venv/bin/python src/model/homogeneity.py evaluate    # columns: validation halves only
    .venv/bin/python src/model/homogeneity.py search      # search: cache distances at every grid cut
    .venv/bin/python src/model/homogeneity.py tune        # search: compare variants on that cache
    .venv/bin/python src/model/homogeneity.py --check
"""

import argparse
from pathlib import Path
import json
import sys

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score

from encoder import BACKBONES, ROOT, SIZE, Crops, Preprocess, collate, load_rows

GRID = 16            # patches per side at 224 px, patch size 14
BLOCK = 12           # encoder block whose patch tokens are read
INK = 0.15           # |pixel - background| above this (0-1 scale) counts as ink
MIN_COLS = 4         # fewer ink columns than this: too short to split, treated as one typeface
FALSE_ALARM = 0.05   # share of single-font crops allowed above the cutoff
CACHE = ROOT / "data/features/homogeneity.npz"
CUTS = np.round(np.arange(0.2, 0.81, 0.1), 2)   # candidate cut positions, fraction of crop width
MIN_PIECE = 1 / 8                                # no piece narrower than this share of the crop


def profiles(model, prep, imgs):
    """Per crop: column profiles (GRID, d), attention mass per column, and the
    largest ink share of any patch in the column. Max, not mean: square padding
    leaves a wide word as a band one or two patch rows tall, which a column
    mean would dilute below any threshold."""
    x = prep(imgs)
    out = model(pixel_values=x, output_hidden_states=True, output_attentions=True)
    tok = model.layernorm(out.hidden_states[BLOCK])[:, 1:]                   # (B, 256, d)
    att = out.attentions[-1][:, :, 0, 1:].mean(1)                            # CLS -> patches, (B, 256)
    b, _, d = tok.shape
    tok = tok.view(b, GRID, GRID, d)                                         # rows, cols
    att = att.view(b, GRID, GRID)
    # Ink from the prepared crop itself: distance from its border median.
    gray = x[:, 0] * prep.std[0, 0] + prep.mean[0, 0]                        # undo normalization
    bg = torch.cat([gray[:, 0], gray[:, -1], gray[:, :, 0], gray[:, :, -1]], 1).median(1).values
    ink = ((gray - bg[:, None, None]).abs() > INK).float()
    ink = F.avg_pool2d(ink[:, None], SIZE // GRID)[:, 0]                     # share of ink per patch
    w = ink / ink.sum(1, keepdim=True).clamp_min(1e-6)                       # weight within each column
    cols = (tok * w[..., None]).sum(1)                                       # ink-weighted column profile
    return cols, att.sum(1), ink.amax(1)


def cache(args):
    from transformers import AutoModel
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModel.from_pretrained(BACKBONES["dinov2"][0], attn_implementation="eager").to(dev).eval()
    prep = Preprocess("dinov2").to(dev)
    sets = {"mixed": load_rows(ROOT / "data/corpus_mixed"),
            "single": [r for r in load_rows() if r["split"] in ("validation", "test")]}
    out = {}
    for name, rows in sets.items():
        loader = torch.utils.data.DataLoader(Crops(rows), batch_size=32, num_workers=args.workers,
                                             collate_fn=collate)
        cols, att, ink = [], [], []
        with torch.no_grad(), torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
            for i, (imgs, _) in enumerate(loader):
                c, a, k = profiles(model, prep, imgs)
                cols.append(c.float().cpu().numpy().astype(np.float16))
                att.append(a.float().cpu().numpy())
                ink.append(k.float().cpu().numpy())
                if i % 50 == 0:
                    print(f"{name} {i * 32}/{len(rows)}", file=sys.stderr)
        out |= {f"{name}_ids": np.array([r["image_id"] for r in rows]), f"{name}_cols": np.concatenate(cols),
                f"{name}_att": np.concatenate(att), f"{name}_ink": np.concatenate(ink)}
    np.savez(CACHE, **out)
    print(f"-> {CACHE}")


def split_columns(cols, keep, seed=0):
    """Two-cluster split of the kept columns. Returns (dispersion, labels over
    kept columns, contiguous?, boundary column or None)."""
    v = F.normalize(torch.as_tensor(cols[keep], dtype=torch.float32), dim=-1).numpy()
    if len(v) < MIN_COLS:
        return 0.0, None, False, None
    lab = KMeans(2, n_init=10, random_state=seed).fit_predict(v)
    if lab.min() == lab.max():
        return 0.0, lab, False, None
    m = F.normalize(torch.as_tensor(np.stack([v[lab == 0].mean(0), v[lab == 1].mean(0)])), dim=-1)
    disp = float(1 - (m[0] @ m[1]))
    changes = int((lab[1:] != lab[:-1]).sum())
    idx = np.flatnonzero(keep)
    boundary = (idx[np.argmax(lab[1:] != lab[:-1])] + 1) if changes == 1 else None
    return disp, lab, changes == 1, boundary


def keep_mask(att, ink, mode):
    """Which columns carry ink. 'ink': some patch in the column is at least 5%
    ink. 'attention': CLS attention mass above half the crop's mean column mass."""
    if mode == "ink":
        return ink > 0.05
    return att > 0.5 * att.mean()


def crop_fraction(boundary_col, width, height):
    """Undo the square padding: grid column -> fraction of the stored crop's width."""
    side = max(width, height)
    left = (side - width) / 2
    x = boundary_col * side / GRID - left
    return float(np.clip(x / width, 0, 1))


def evaluate(args):
    from PIL import Image
    z = np.load(CACHE)
    single = {r["image_id"]: r for r in load_rows()}
    mixed = {r["image_id"]: r for r in load_rows(ROOT / "data/corpus_mixed")}
    split = "test" if args.final else "validation"
    report = {"split": split, "block": BLOCK, "false_alarm_target": FALSE_ALARM}
    for mode in ("ink", "attention"):
        s_ids = z["single_ids"]
        s_disp = np.array([split_columns(c, keep_mask(a, k, mode))[0]
                           for c, a, k in zip(z["single_cols"], z["single_att"], z["single_ink"])])
        s_split = np.array([single[i]["split"] for i in s_ids])
        # Calibrate on validation single-font crops (first half); report false alarm
        # on the held-out half, or on the test partition with --final.
        val = np.flatnonzero(s_split == "validation")
        rng = np.random.default_rng(0)
        cal = rng.permutation(val)[: len(val) // 2]
        cutoff = float(np.quantile(s_disp[cal], 1 - FALSE_ALARM))
        held = np.setdiff1d(val, cal) if not args.final else np.flatnonzero(s_split == "test")

        res = {"cutoff": cutoff, "single_false_alarm": float((s_disp[held] >= cutoff).mean()), "by_mix": {}}
        m_ids = z["mixed_ids"]
        sel = [j for j, i in enumerate(m_ids) if mixed[i]["split"] == split]
        rows_by = {}
        for j in sel:
            r = mixed[m_ids[j]]
            disp, _, contig, bcol = split_columns(z["mixed_cols"][j], keep_mask(z["mixed_att"][j], z["mixed_ink"][j], mode))
            flagged = disp >= cutoff
            verdict = "one" if not flagged else ("split" if contig else "mixed")
            err = None
            if verdict == "split" and r["boundary_frac"]:
                w, h = Image.open(ROOT / r["image_path"]).size
                err = abs(crop_fraction(bcol, w, h) - float(r["boundary_frac"]))
            rows_by.setdefault(r["mix"], []).append((verdict, err, r["tier"], r["family_a"] == r["family_b"]))
        for mix, items in rows_by.items():
            v = np.array([x[0] for x in items])
            errs = [x[1] for x in items if x[1] is not None]
            same = np.array([x[3] for x in items])
            tier = np.array([x[2] for x in items])
            res["by_mix"][mix] = {
                "n": len(items),
                "detected": float((v != "one").mean()),
                "verdict_split": float((v == "split").mean()),
                "verdict_mixed": float((v == "mixed").mean()),
                "boundary_error_median": float(np.median(errs)) if errs else None,
                "boundary_within_10pct": float(np.mean(np.array(errs) <= 0.10)) if errs else None,
                "detected_same_family": float((v[same] != "one").mean()),
                "detected_cross_family": float((v[~same] != "one").mean()),
                "detected_by_tier": {t: float((v[tier == t] != "one").mean()) for t in sorted(set(tier))},
            }
        report[mode] = res
        print(mode, json.dumps({k: res[k] for k in ("cutoff", "single_false_alarm")}),
              {m: (round(x["detected"], 3), round(x["verdict_split"], 3), round(x["verdict_mixed"], 3))
               for m, x in res["by_mix"].items()})
    out = ROOT / f"reports/incr3/homogeneity{'_final' if args.final else ''}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"-> {out}")


def cut_distances(emb, imgs, dev, cuts=CUTS):
    """(n_crops, len(cuts)) cosine distances between the font embeddings of the
    left and right pieces of each crop, cut at each fraction of its width."""
    pieces = []
    for img in imgs:
        w = img.shape[1]
        for f in cuts:
            c = int(np.clip(round(w * f), max(1, round(w * MIN_PIECE)), w - max(1, round(w * MIN_PIECE))))
            pieces += [img[:, :c], img[:, c:]]
    with torch.no_grad(), torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
        z = emb(pieces).float()
    return (1 - (z[0::2] * z[1::2]).sum(1)).view(len(imgs), len(cuts)).cpu().numpy()


GRID_CUTS = np.round(np.arange(0.10, 0.91, 0.05), 2)   # cut grid cached once; variants pick from it
SEARCH_CACHE = ROOT / "data/features/homogeneity_cuts{}.npz"
N_SINGLE = 3000                                          # single-font crops sampled for calibration


def search(args):
    """Cache the left/right distance at every grid cut for single-font and mixed
    crops (validation, or test with --final), with each crop's size."""
    from encoder import FontEmbedder, read_crop
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    emb = FontEmbedder.load(ROOT / args.head).to(dev)
    split = "test" if args.final else "validation"
    single = [r for r in load_rows() if r["split"] == split]
    single = [single[i] for i in sorted(np.random.default_rng(0).choice(len(single), N_SINGLE, replace=False))]
    mixed = [r for r in load_rows(ROOT / "data/corpus_mixed") if r["split"] == split]

    def run(rows, name, bs=8, every=25):
        # Progress is saved every `every` batches and resumed on a rerun: the shared
        # server rebooted every ~40 min on 2 Oct, shorter than one set takes.
        part = Path(str(SEARCH_CACHE).format(f"_{name}{'_final' if args.final else ''}_part"))
        ids = [r["image_id"] for r in rows]
        out, sizes = [], []
        if part.exists():
            z = np.load(part)
            if list(z["ids"]) == ids[: len(z["ids"])]:
                out, sizes = [z["d"]], [tuple(x) for x in z["hw"]]
                print(f"{name}: resuming at {len(z['ids'])}/{len(rows)}", file=sys.stderr)
        done = len(sizes)
        for k, i in enumerate(range(done, len(rows), bs)):
            imgs = [read_crop(r) for r in rows[i:i + bs]]
            out.append(cut_distances(emb, imgs, dev, GRID_CUTS))
            sizes += [img.shape[:2] for img in imgs]
            if k % every == every - 1 or i + bs >= len(rows):
                np.savez(part, ids=ids[: len(sizes)], d=np.concatenate(out), hw=np.array(sizes))
                print(f"{name} {len(sizes)}/{len(rows)} saved", file=sys.stderr)
        return np.concatenate(out), np.array(sizes)

    s_d, s_hw = run(single, "single")
    m_d, m_hw = run(mixed, "mixed")
    np.savez(str(SEARCH_CACHE).format("_final" if args.final else ""), grid=GRID_CUTS,
             single_ids=[r["image_id"] for r in single], single_d=s_d, single_hw=s_hw,
             mixed_ids=[r["image_id"] for r in mixed], mixed_d=m_d, mixed_hw=m_hw)
    print("cached", s_d.shape, m_d.shape)


def variant_scores(d, hw, grid, lo, hi, min_aspect, stats=None):
    """Per crop: the best cut's score and index. A cut is allowed if it lies in
    [lo, hi] and both pieces are at least min_aspect wide relative to the crop
    height. With stats=(mean, sd) per grid cut, distances are z-scored per cut
    first, so a cut position that is noisy on single-font crops counts for less."""
    h, w = hw[:, :1].astype(float), hw[:, 1:].astype(float)
    ok = (grid >= lo) & (grid <= hi)
    ok = ok[None, :] & (grid[None, :] * w / h >= min_aspect) & ((1 - grid[None, :]) * w / h >= min_aspect)
    z = d if stats is None else (d - stats[0]) / stats[1]
    z = np.where(ok, z, -np.inf)
    return z.max(1), z.argmax(1)


def tune(args):
    """Compare search variants on the validation cache. Chosen by the detection
    of contiguous (word + mid-word) mixes at 5% false alarm."""
    c = np.load(str(SEARCH_CACHE).format(""))
    grid = c["grid"]
    mixed = {r["image_id"]: r for r in load_rows(ROOT / "data/corpus_mixed")}
    m_rows = [mixed[i] for i in c["mixed_ids"]]
    mix = np.array([r["mix"] for r in m_rows])
    contiguous = mix != "interleave"
    true_b = np.array([float(r["boundary_frac"]) if r["boundary_frac"] else np.nan for r in m_rows])
    n = len(c["single_d"])
    cal = np.random.default_rng(0).permutation(n)[: n // 2]
    held = np.setdiff1d(np.arange(n), cal)
    stats = (c["single_d"][cal].mean(0), c["single_d"][cal].std(0) + 1e-6)

    results = []
    for lo, hi in ((0.5, 0.5), (0.35, 0.65), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)):
        for min_aspect in (0.0, 0.75, 1.25):
            for norm_ in (False, True):
                st = stats if norm_ else None
                s_sc, _ = variant_scores(c["single_d"], c["single_hw"], grid, lo, hi, min_aspect, st)
                m_sc, m_arg = variant_scores(c["mixed_d"], c["mixed_hw"], grid, lo, hi, min_aspect, st)
                fin = np.isfinite(s_sc[cal])
                if fin.mean() < 0.5:   # the variant leaves most crops with no allowed cut
                    continue
                cutoff = float(np.quantile(np.where(fin, s_sc[cal], -np.inf), 1 - FALSE_ALARM))
                flag = m_sc >= cutoff
                err = np.abs(grid[m_arg] - true_b)
                hit = flag & contiguous
                sh = np.where(np.isfinite(s_sc[held]), s_sc[held], -1e9)
                mc = np.where(np.isfinite(m_sc[contiguous]), m_sc[contiguous], -1e9)
                results.append({
                    "cuts": [lo, hi], "min_aspect": min_aspect, "per_cut_z": norm_, "cutoff": cutoff,
                    "false_alarm": float((s_sc[held] >= cutoff).mean()),
                    "auroc_contiguous": float(roc_auc_score(np.r_[np.zeros(len(sh)), np.ones(len(mc))], np.r_[sh, mc])),
                    "detected_word": float(flag[mix == "word"].mean()),
                    "detected_char": float(flag[mix == "char"].mean()),
                    "detected_interleave": float(flag[mix == "interleave"].mean()),
                    "detected_contiguous": float(flag[contiguous].mean()),
                    "boundary_error_median": float(np.nanmedian(err[hit])) if hit.any() else None,
                    "boundary_within_10pct": float((err[hit] <= 0.10).mean()) if hit.any() else None,
                })
    results.sort(key=lambda r: -r["detected_contiguous"])
    out = ROOT / "reports/incr3/homogeneity_tune.json"
    out.write_text(json.dumps({"grid": grid.tolist(), "n_single": n, "n_mixed": len(m_rows),
                               "variants": results}, indent=2))
    for r in results[:8]:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != "cutoff"})
    print(f"-> {out}")


def check():
    rng = np.random.default_rng(0)
    a, b = rng.normal(size=64), rng.normal(size=64)
    noise = lambda: 0.05 * rng.normal(size=(GRID, 64))
    keep = np.ones(GRID, bool)
    one = np.tile(a, (GRID, 1)) + noise()
    two = np.vstack([np.tile(a, (6, 1)), np.tile(b, (10, 1))]) + noise()
    alt = np.vstack([a if i % 2 else b for i in range(GRID)]) + noise()
    d1, _, _, _ = split_columns(one, keep)
    d2, _, c2, b2 = split_columns(two, keep)
    d3, _, c3, _ = split_columns(alt, keep)
    assert d1 < 0.05 < d2 and c2 and b2 == 6, (d1, d2, c2, b2)
    assert d3 > 0.05 and not c3, (d3, c3)
    # Empty columns are skipped, and the boundary is still reported in grid columns.
    keep2 = keep.copy(); keep2[:2] = keep2[-2:] = False
    _, _, c4, b4 = split_columns(two, keep2)
    assert c4 and b4 == 6, (c4, b4)
    assert split_columns(two, np.zeros(GRID, bool))[0] == 0.0
    # Padding undone: a wide crop fills the width, so column 8 of 16 is its middle.
    assert abs(crop_fraction(8, 224, 56) - 0.5) < 1e-9
    assert abs(crop_fraction(4, 112, 224) - 0.0) < 1e-9   # tall crop: column 4 is its left edge
    # search: a fake embedder that "sees" font by pixel value finds the boundary cut.
    class Fake:
        def __call__(self, pieces):
            return F.normalize(torch.stack([torch.tensor([float((p < 100).float().mean()), float((p >= 100).float().mean())])
                                            for p in pieces]), dim=-1)
    img = torch.zeros((20, 100), dtype=torch.uint8); img[:, 40:] = 200    # font A left 40%, font B right
    d = cut_distances(Fake(), [img], "cpu")[0]
    assert CUTS[d.argmax()] == 0.4, (CUTS, d)
    flat = torch.zeros((20, 100), dtype=torch.uint8)
    assert cut_distances(Fake(), [flat], "cpu").max() < 1e-6
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", nargs="?", choices=["cache", "evaluate", "search", "tune"])
    ap.add_argument("--head", default="data/models/head_dinov2_mid_oe.pt")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--final", action="store_true", help="report on the TEST halves (Chapter 5 only)")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.check:
        check()
    elif a.step == "cache":
        cache(a)
    elif a.step == "evaluate":
        evaluate(a)
    elif a.step == "search":
        search(a)
    elif a.step == "tune":
        tune(a)
    else:
        ap.print_help()
