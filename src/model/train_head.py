"""Train the student metric head f_theta on cached frozen-backbone features.

Two signals at once (Section 4.4.2 step 6): a batch-all triplet loss on the
font labels (Chapter 3, eq. 6; margin 0.2 on unit vectors) over P x K batches,
and relational distillation -- the student's in-batch cosine-similarity rows
are pulled toward the teacher's by KL. The KD term reads no labels.

Evaluation here is separability only (Increment 2): nearest-prototype Top-1/3
by tier and family, family-level accuracy, cosine silhouette. The threshold
tau and FPR@95 belong to Increment 3. The un-headed frozen features are
scored by the same function as the baseline the head must beat.

    .venv/Scripts/python.exe src/model/train_head.py --check
    .venv/Scripts/python.exe src/model/train_head.py --backbone dinov2
    .venv/Scripts/python.exe src/model/train_head.py --backbone dinov2 --folds 5
    .venv/Scripts/python.exe src/model/train_head.py --backbone dinov2 --no-kd
"""

import os

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")  # deterministic cuBLAS

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import silhouette_score
from sklearn.model_selection import StratifiedKFold

from encoder import BACKBONES, ROOT, FontEmbedder, Head, load_rows, read_crop

FAMILIES = ["sans-serif", "serif", "display", "monospace"]


# --- losses ---

def batch_hard_triplet(z, y, margin):
    """For each anchor: its farthest same-font and nearest other-font crop."""
    d = (2 - 2 * z @ z.T).clamp_min(0)  # squared L2 between unit vectors
    same = y[:, None] == y[None, :]
    eye = torch.eye(len(y), dtype=torch.bool, device=z.device)
    pos = d.masked_fill(~same | eye, -1).max(1).values
    neg = d.masked_fill(same, float("inf")).min(1).values
    return F.relu(pos - neg + margin).mean()


def batch_all_triplet(z, y, margin):
    """Every valid (anchor, positive, negative) in the batch, averaged over the
    ones that still violate the margin (Hermans et al., 2017). Harder to
    collapse than batch-hard when the hardest pairs are mostly noise."""
    d = (2 - 2 * z @ z.T).clamp_min(0)
    same = y[:, None] == y[None, :]
    eye = torch.eye(len(y), dtype=torch.bool, device=z.device)
    valid = (same & ~eye)[:, :, None] & ~same[:, None, :]
    loss = F.relu(d[:, :, None] - d[:, None, :] + margin) * valid
    return loss.sum() / ((loss > 1e-12).sum() + 1e-12)


TRIPLET = {"hard": batch_hard_triplet, "all": batch_all_triplet}


def relational_kd(z, t, temp):
    """KL(teacher || student) over each row's similarities to the rest of the
    batch. Diagonal dropped: self-similarity is 1 for both and says nothing."""
    t = F.normalize(t.float(), dim=-1)
    off = ~torch.eye(len(z), dtype=torch.bool, device=z.device)
    s = (z @ z.T)[off].view(len(z), -1) / temp
    st = (t @ t.T)[off].view(len(z), -1) / temp
    return F.kl_div(F.log_softmax(s, 1), F.log_softmax(st, 1), log_target=True, reduction="batchmean")


def pk_batches(y, idx, p, k, rng):
    """One epoch of P fonts x K crops batches drawn from idx."""
    by_font = defaultdict(list)
    for i in idx:
        by_font[int(y[i])].append(i)
    fonts = np.array(sorted(by_font))
    for _ in range(len(idx) // (p * k)):
        chosen = rng.choice(fonts, size=p, replace=False)
        yield np.concatenate([rng.choice(by_font[f], size=k, replace=False) for f in chosen])


# --- evaluation ---

def prototypes(z, y, n_font):
    """Per-font mean embedding, re-normalized. One-hot matmul rather than
    index_add_, which uses CUDA atomics and breaks deterministic mode."""
    return F.normalize(F.one_hot(y, n_font).T.float() @ z, dim=-1)


@torch.no_grad()
def evaluate(zt, yt, ze, ye, fam, tier):
    """Nearest-prototype separability. zt/ze are unit vectors; fam maps a font
    index to its family; tier is the eval crops' severity tier."""
    protos = prototypes(zt, yt, int(fam.shape[0]))
    rank = (ze @ protos.T).argsort(1, descending=True)
    top1 = rank[:, 0] == ye
    top3 = (rank[:, :3] == ye[:, None]).any(1)
    fam_hit = fam[rank[:, 0]] == fam[ye]
    out = {"top1": top1.float().mean().item(), "top3": top3.float().mean().item(),
           "family_acc": fam_hit.float().mean().item()}
    for t in sorted(set(tier)):
        m = torch.tensor([x == t for x in tier], device=ze.device)
        out[f"top1_{t}"] = top1[m].float().mean().item()
    for i, f in enumerate(FAMILIES):
        m = fam[ye] == i
        if m.any():
            out[f"top1_{f}"] = top1[m].float().mean().item()
    zn, yn = ze.cpu().numpy(), ye.cpu().numpy()
    out["silhouette_font"] = float(silhouette_score(zn, yn, metric="cosine"))
    out["silhouette_family"] = float(silhouette_score(zn, fam[ye].cpu().numpy(), metric="cosine"))
    return out


# --- training ---

def fit(X, T, y, train_idx, sel_idx, fam, tier, args, dev):
    """Train one head. With sel_idx, keep the epoch with the best selection
    Top-1; without (CV folds), train the fixed epoch count and keep the last."""
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    head = Head(X.shape[1], args.dim, args.hidden).to(dev)
    opt = torch.optim.AdamW(head.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)
    tr = torch.as_tensor(train_idx, device=dev)
    best, best_state, log = -1.0, None, []
    for ep in range(args.epochs):
        head.train()
        tot = defaultdict(float)
        nb = 0
        for b in pk_batches(y.cpu().numpy(), train_idx, args.p, args.k, rng):
            b = torch.as_tensor(b, device=dev)
            z = head(X[b])
            trip = TRIPLET[args.mining](z, y[b], args.margin)
            kd = relational_kd(z, T[b], args.temp) if args.kd > 0 else torch.zeros((), device=dev)
            loss = trip + args.kd * kd
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            tot["triplet"] += trip.item(); tot["kd"] += kd.item(); nb += 1
        sched.step()
        entry = {"epoch": ep, **{k: v / nb for k, v in tot.items()}}
        if sel_idx is not None:
            head.eval()
            with torch.no_grad():
                sel = torch.as_tensor(sel_idx, device=dev)
                m = evaluate_fast(head(X[tr]), y[tr], head(X[sel]), y[sel], fam.shape[0])
            entry["sel_top1"] = m
            if m > best:
                best, best_state = m, {k: v.clone() for k, v in head.state_dict().items()}
        log.append(entry)
        print(json.dumps(entry), file=sys.stderr)
    if best_state is not None:
        head.load_state_dict(best_state)
    return head.eval(), log


@torch.no_grad()
def evaluate_fast(zt, yt, ze, ye, n_font):
    return ((ze @ prototypes(zt, yt, n_font).T).argmax(1) == ye).float().mean().item()


TEACHER_CACHE = ROOT / "data/features/teacher.npz"


def load(backbone, need_teacher, teacher_cache=TEACHER_CACHE):
    rows = load_rows()
    ids = [r["image_id"] for r in rows]
    f = np.load(ROOT / f"data/features/{backbone}.npz")
    assert list(f["image_id"]) == ids, "feature cache out of sync with metadata.csv; re-run cache_features.py"
    T = None
    if need_teacher:
        t = np.load(teacher_cache)
        assert list(t["image_id"]) == ids, "teacher cache out of sync; re-run cache_features.py --teacher"
        T = t["feats"]
    return rows, f["feats"], T


def setup(backbone, need_teacher, dev, teacher_cache=TEACHER_CACHE):
    """Cached features, labels and splits on `dev`; shared with sweep.py."""
    rows, X, T = load(backbone, need_teacher, teacher_cache)
    fonts = sorted({r["font_id"] for r in rows})
    fi = {f: i for i, f in enumerate(fonts)}
    fam_of = {r["font_id"]: FAMILIES.index(r["family_class"]) for r in rows}
    split = np.array([r["split"] for r in rows])
    return SimpleNamespace(
        rows=rows, fonts=fonts, tier=[r["tier"] for r in rows],
        X=torch.as_tensor(X, device=dev).float(),
        T=torch.as_tensor(T, device=dev) if T is not None else torch.zeros(len(rows), 1, device=dev),
        y=torch.tensor([fi[r["font_id"]] for r in rows], device=dev),
        fam=torch.tensor([fam_of[f] for f in fonts], device=dev),
        train_idx=np.flatnonzero(split == "train"), val_idx=np.flatnonzero(split == "validation"))


def main(args):
    torch.use_deterministic_algorithms(True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    d = setup(args.backbone, args.kd > 0, dev, args.teacher_cache)
    rows, fonts, tier, X, T, y, fam = d.rows, d.fonts, d.tier, d.X, d.T, d.y, d.fam
    train_idx, val_idx = d.train_idx, d.val_idx

    def score(z, tr, ev):
        return evaluate(z[tr], y[tr], z[ev], y[ev], fam, [tier[i] for i in ev])

    tag = args.backbone + ("" if args.kd > 0 else "_nokd")
    hp = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items() if k != "check"}
    out = ROOT / "reports/incr2"
    out.mkdir(parents=True, exist_ok=True)

    if args.folds:
        pool = np.concatenate([train_idx, val_idx])
        strata = [f"{rows[i]['font_id']}|{tier[i]}" for i in pool]
        folds = []
        for k, (a, b) in enumerate(StratifiedKFold(args.folds, shuffle=True, random_state=args.seed)
                                   .split(pool, strata)):
            print(f"fold {k + 1}/{args.folds}", file=sys.stderr)
            head, _ = fit(X, T, y, pool[a], None, fam, tier, args, dev)
            with torch.no_grad():
                folds.append(score(head(X), pool[a], pool[b]))
        keys = folds[0].keys()
        summary = {k: {"mean": float(np.mean([f[k] for f in folds])), "std": float(np.std([f[k] for f in folds]))}
                   for k in keys}
        (out / f"{tag}_cv.json").write_text(json.dumps({"folds": folds, "summary": summary, "hparams": hp}, indent=2))
        print(json.dumps({k: f"{v['mean']:.4f} +/- {v['std']:.4f}" for k, v in summary.items()}, indent=2))
        return

    head, log = fit(X, T, y, train_idx, val_idx, fam, tier, args, dev)
    with torch.no_grad():
        result = {"head": score(head(X), train_idx, val_idx),
                  "frozen_baseline": score(F.normalize(X, dim=-1), train_idx, val_idx),
                  "log": log, "hparams": hp}
    (out / f"{tag}.json").write_text(json.dumps(result, indent=2))
    ckpt = ROOT / f"data/models/head_{tag}.pt"
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"backbone": args.backbone, "d_in": X.shape[1], "dim": args.dim, "hidden": args.hidden,
                "state_dict": head.state_dict(),
                "fonts": fonts, "hparams": hp}, ckpt)
    print(json.dumps({"head": result["head"], "frozen_baseline": result["frozen_baseline"]}, indent=2))


def check():
    torch.manual_seed(0)
    # Two tight, far-apart clusters: no violation. Labels swapped: every anchor violates.
    c = F.normalize(torch.tensor([[1.0, 0.0], [0.0, 1.0]]), dim=-1)
    z = F.normalize(c.repeat_interleave(4, 0) + 0.01 * torch.randn(8, 2), dim=-1)
    y = torch.arange(2).repeat_interleave(4)
    assert batch_hard_triplet(z, y, 0.2).item() == 0.0
    assert batch_hard_triplet(z, y.roll(1), 0.2).item() > 0.0
    assert batch_all_triplet(z, y, 0.2).item() == 0.0 and batch_all_triplet(z, y.roll(1), 0.2).item() > 0.0
    t = torch.randn(8, 16)
    assert abs(relational_kd(F.normalize(t, dim=-1), t, 0.1).item()) < 1e-6, "KD not 0 when student = teacher"
    assert relational_kd(z, t, 0.1).item() > 0.0
    yy = np.repeat(np.arange(10), 20)
    for b in pk_batches(yy, np.arange(200), 5, 4, np.random.default_rng(0)):
        fonts, counts = np.unique(yy[b], return_counts=True)
        assert len(fonts) == 5 and (counts == 4).all()
    fam = torch.tensor([0, 1])
    m = evaluate(z, y, z, y, fam, ["pristine"] * 8)
    assert m["top1"] == 1.0 and m["family_acc"] == 1.0 and m["silhouette_font"] > 0.9, m

    # Train/serve skew (Section 4.10.1): the served FontEmbedder on raw PNGs
    # must reproduce head(cached feature). Runs once a head has been trained.
    ckpt = ROOT / "data/models/head_dinov2.pt"
    if ckpt.exists():
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        rows, X, _ = load("dinov2", False)
        val = [i for i, r in enumerate(rows) if r["split"] == "validation"][:20]
        emb = FontEmbedder.load(ckpt).to(dev)
        with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
            served = emb([read_crop(rows[i]) for i in val]).float()
        cached = emb.head(torch.as_tensor(X[val], device=dev))
        cos = (served * cached).sum(1)
        assert cos.min() > 0.999, f"train/serve skew: min cosine {cos.min():.5f}"
        print(f"skew test ok (min cosine {cos.min():.5f} over {len(val)} crops)")
    else:
        print("skew test skipped: no trained head yet")
    print("ok")


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--backbone", choices=BACKBONES, default="dinov2")
    ap.add_argument("--folds", type=int, default=0, help="stratified k-fold on train+val (Section 4.3.2)")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--p", type=int, default=32, help="fonts per batch")
    ap.add_argument("--k", type=int, default=4, help="crops per font per batch")
    ap.add_argument("--margin", type=float, default=0.2)
    ap.add_argument("--dim", type=int, default=256, help="embedding dimension")
    ap.add_argument("--hidden", type=int, default=512)
    ap.add_argument("--mining", choices=["hard", "all"], default="all",
                    help="batch-hard collapsed to a point on this corpus (loss pinned at the margin)")
    ap.add_argument("--kd", type=float, default=1.0, help="KD weight lambda; 0 = triplet only")
    ap.add_argument("--no-kd", dest="kd", action="store_const", const=0.0)
    ap.add_argument("--temp", type=float, default=0.1, help="KD softmax temperature")
    ap.add_argument("--teacher-cache", type=Path, default=TEACHER_CACHE)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=2026)
    return ap


if __name__ == "__main__":
    a = parser().parse_args()
    check() if a.check else main(a)
