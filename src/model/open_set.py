"""Open-set decision for a trained head: prototypes, threshold tau, rejection.

Section 4.4.2 steps 7-8 and 11. Each palette font's prototype is the mean
training embedding (re-normalized). A crop's rejection score is its cosine
similarity to the nearest prototype. tau is the score at which 95% of
validation crops whose font is in the palette are accepted; a crop below tau
gets the "unknown font" verdict. Rejection quality is the share of
unknown-font crops wrongly accepted at that tau: FPR at 95% recall
(Section 4.10.2). AUROC summarizes the same separation across all thresholds.

Model choice uses the unknown-font *validation* fonts only. The test fonts
are reserved for Chapter 5 and need --final to be touched.

    .venv/bin/python src/model/open_set.py                    # the final head
    .venv/bin/python src/model/open_set.py --head data/models/head_dinov2_mid.pt
    .venv/bin/python src/model/open_set.py --check
"""

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

from encoder import ROOT, Head, load_rows
from train_head import FAMILIES, prototypes

RECALL = 0.95


def embed(head, backbone, corpus):
    """Head embeddings for every row of a corpus, from its cached features."""
    rows = load_rows(ROOT / corpus)
    suffix = Path(corpus).name.removeprefix("corpus")
    f = np.load(ROOT / f"data/features/{backbone}{suffix}.npz")
    assert list(f["image_id"]) == [r["image_id"] for r in rows], f"{backbone}{suffix}.npz out of sync"
    with torch.no_grad():
        return rows, head(torch.as_tensor(f["feats"]).float())


def calibrate(known_scores, recall=RECALL):
    """The highest tau that still accepts `recall` of the known crops."""
    return float(np.quantile(known_scores, 1 - recall))


def decide(z, protos):
    """Nearest-prototype index and its cosine similarity (the rejection score)."""
    sims = z @ protos.T
    score, nearest = sims.max(1)
    return score.numpy(), nearest.numpy(), sims


def rates(score, tau):
    return float((score >= tau).mean())


def family_confusion(true_fam, pred_fam, n=4):
    """Rows: true family. Columns: predicted family. Counts of crops."""
    m = np.zeros((n, n), int)
    np.add.at(m, (true_fam, pred_fam), 1)
    return m


def severity_index(z, y_true, y_pred, n_font):
    """Relative severity index of Chen et al. (2026): centroids are the mean
    embedding of each font's evaluated crops; d(i, j) is their cosine
    distance; SWER is the mean of d(y, y_hat) over all predictions (0 when
    correct); the random baseline is the mean of d over all font pairs.
    Pi = SWER / SWER_random. Below 1, errors land on nearer fonts than chance."""
    yt = torch.as_tensor(y_true)
    c = F.normalize(F.one_hot(yt, n_font).T.float() @ z, dim=-1)
    d = (1 - c @ c.T).clamp_min(0).fill_diagonal_(0).numpy()  # d(i, i) = 0 exactly, not ~1e-7
    swer = float(d[y_true, y_pred].mean())
    swer_random = float(d.mean())
    return {"swer": swer, "swer_random": swer_random, "pi": swer / swer_random}


def conformal(sims_cal, y_cal, sims_ev, y_ev, alpha, tier_ev=None, accepted_ev=None):
    """Split-conformal prediction sets. Nonconformity = 1 - cosine similarity to
    the true font's prototype. The set holds every font within the calibrated
    quantile; it contains the true font with probability >= 1 - alpha."""
    s = 1 - sims_cal[np.arange(len(y_cal)), y_cal]
    n = len(s)
    q = float(np.quantile(s, min(1.0, np.ceil((n + 1) * (1 - alpha)) / n), method="higher"))
    sets = (1 - sims_ev) <= q
    hit = sets[np.arange(len(y_ev)), y_ev]
    size = sets.sum(1)
    out = {"alpha": alpha, "threshold": q, "coverage": float(hit.mean()),
           "mean_set_size": float(size.mean()), "median_set_size": float(np.median(size))}
    if tier_ev is not None:
        out["coverage_by_tier"] = {t: float(hit[tier_ev == t].mean()) for t in sorted(set(tier_ev))}
        out["mean_set_size_by_tier"] = {t: float(size[tier_ev == t].mean()) for t in sorted(set(tier_ev))}
    if accepted_ev is not None:
        out["mean_set_size_when_accepted"] = float(size[accepted_ev].mean())
    return out


def main(args):
    ck = torch.load(ROOT / args.head, map_location="cpu")
    head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512)).eval()
    head.load_state_dict(ck["state_dict"])
    backbone, fonts = ck["backbone"], ck["fonts"]
    fi = {f: i for i, f in enumerate(fonts)}

    rows, z = embed(head, backbone, "data/corpus")
    y = torch.tensor([fi[r["font_id"]] for r in rows])
    split = np.array([r["split"] for r in rows])
    protos = prototypes(z[split == "train"], y[split == "train"], len(fonts))

    # tau is always calibrated on validation; --final then scores the test partition
    # and the test unknown fonts with that fixed tau.
    tau = calibrate(decide(z[split == "validation"], protos)[0])
    eval_split = "test" if args.final else "validation"
    known = split == eval_split
    k_score, k_near, k_sims = decide(z[known], protos)
    k_true = y[known].numpy()
    urows, uz = embed(head, backbone, "data/corpus_unknown")
    keep = np.array([r["split"] == eval_split for r in urows])
    urows = [r for r, k in zip(urows, keep) if k]
    u_score, u_near, _ = decide(uz[torch.from_numpy(keep)], protos)

    accepted = u_score >= tau
    fam_of = {r["font_id"]: r["family_class"] for r in rows}
    k_tier = np.array([r["tier"] for r, k in zip(rows, known) if k])
    k_acc = k_score >= tau
    top3 = (k_sims.topk(3, 1).indices.numpy() == k_true[:, None]).any(1)

    result = {
        "head": args.head, "backbone": backbone, "unknown_split": eval_split, "recall_target": RECALL,
        "tau": tau,
        "fpr_at_95": rates(u_score, tau),
        "auroc": float(roc_auc_score(np.r_[np.ones(len(k_score)), np.zeros(len(u_score))],
                                     np.r_[k_score, u_score])),
        "known": {
            "n": int(known.sum()),
            "top1": float((k_near == k_true).mean()),
            "top3": float(top3.mean()),
            "accepted": float(k_acc.mean()),
            # Accuracy among the crops the system names a font for: what a user sees.
            "top1_when_accepted": float((k_near == k_true)[k_acc].mean()),
            "accepted_by_tier": {t: float(k_acc[k_tier == t].mean()) for t in sorted(set(k_tier))},
        },
        "unknown": {
            "n": int(len(u_score)),
            "fonts": sorted({r["font_id"] for r in urows}),
            "accepted_by_tier": {t: rates(u_score[[r["tier"] == t for r in urows]], tau)
                                 for t in sorted({r["tier"] for r in urows})},
            "accepted_by_family": {c: rates(u_score[[r["family_class"] == c for r in urows]], tau)
                                   for c in FAMILIES if any(r["family_class"] == c for r in urows)},
        },
        "per_unknown_font": {},
    }
    # Error analysis on the known crops (Section 4.10.2): where do errors land?
    fam_idx = np.array([FAMILIES.index(fam_of[f]) for f in fonts])
    result["family_confusion"] = {
        "labels": FAMILIES,
        "counts": family_confusion(fam_idx[k_true], fam_idx[k_near]).tolist(),
    }
    result["severity_index"] = severity_index(z[known], k_true, k_near, len(fonts))
    # Calibrated Top-K: conformal prediction sets, calibrated on one half of the
    # known crops and checked on the other (Ding et al., 2025; Shi et al., 2024).
    half = np.random.default_rng(0).permutation(len(k_true)) < len(k_true) // 2
    sims = k_sims.numpy()
    result["conformal"] = {
        str(a): conformal(sims[half], k_true[half], sims[~half], k_true[~half], a,
                          k_tier[~half], k_acc[~half]) for a in (0.05, 0.10)}
    for font in result["unknown"]["fonts"]:
        m = np.array([r["font_id"] == font for r in urows])
        named = Counter(fonts[i] for i in u_near[m & accepted]).most_common(3)
        result["per_unknown_font"][font] = {
            "family": next(r["family_class"] for r in urows if r["font_id"] == font),
            "accepted": rates(u_score[m], tau),
            # When it is wrongly accepted, which palette fonts does it get mistaken for?
            "mistaken_for": [{"font": f, "family": fam_of[f], "n": n} for f, n in named],
        }

    out = ROOT / args.out if args.out else ROOT / f"reports/incr3/open_set_{backbone}{'_final' if args.final else ''}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in ("backbone", "tau", "fpr_at_95", "auroc")}
                     | {"known_top1": result["known"]["top1"], "top1_when_accepted": result["known"]["top1_when_accepted"],
                        "unknown_accepted_by_tier": result["unknown"]["accepted_by_tier"]}, indent=2))


def check():
    # tau keeps 95% of known scores at or above it.
    s = np.linspace(0, 1, 1001)
    tau = calibrate(s)
    assert abs((s >= tau).mean() - 0.95) < 0.002, (s >= tau).mean()
    # Clusters far apart: unknowns near no prototype are all rejected...
    torch.manual_seed(0)
    c = F.normalize(torch.randn(5, 16), dim=-1)
    known = F.normalize(c.repeat_interleave(50, 0) + 0.05 * torch.randn(250, 16), dim=-1)
    protos = prototypes(known, torch.arange(5).repeat_interleave(50), 5)
    ks, kn, _ = decide(known, protos)
    assert (kn == np.repeat(np.arange(5), 50)).all()
    tau = calibrate(ks)
    far = F.normalize(-c.sum(0, keepdim=True) + 0.05 * torch.randn(100, 16), dim=-1)
    assert rates(decide(far, protos)[0], tau) == 0.0
    # ...while "unknowns" drawn from the known clusters are accepted about as often as knowns.
    same = F.normalize(c.repeat_interleave(20, 0) + 0.05 * torch.randn(100, 16), dim=-1)
    assert rates(decide(same, protos)[0], tau) > 0.8
    # Family confusion counts land in the right cells.
    m = family_confusion(np.array([0, 0, 1, 3]), np.array([0, 1, 1, 3]))
    assert m[0, 0] == 1 and m[0, 1] == 1 and m[1, 1] == 1 and m[3, 3] == 1 and m.sum() == 4
    # Severity: no errors -> 0; errors onto the nearest font cost less than errors onto the farthest.
    yk = np.repeat(np.arange(5), 50)
    assert severity_index(known, yk, yk, 5)["pi"] == 0.0
    d = 1 - c @ c.T
    near, far = d.clone().fill_diagonal_(9).argmin(1).numpy(), d.argmax(1).numpy()
    assert severity_index(known, yk, near[yk], 5)["pi"] < severity_index(known, yk, far[yk], 5)["pi"]
    # Conformal coverage meets 1 - alpha on exchangeable data.
    sims = (known @ protos.T).numpy()
    perm = np.random.default_rng(1).permutation(250)
    cal, ev = perm[:125], perm[125:]
    for a in (0.05, 0.2):
        cov = conformal(sims[cal], yk[cal], sims[ev], yk[ev], a)["coverage"]
        assert cov >= 1 - a - 0.05, (a, cov)
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--head", default="data/models/head_dinov2_mid_oe.pt")
    ap.add_argument("--final", action="store_true", help="score the TEST unknown fonts (Chapter 5 only)")
    ap.add_argument("--out")
    a = ap.parse_args()
    check() if a.check else main(a)
