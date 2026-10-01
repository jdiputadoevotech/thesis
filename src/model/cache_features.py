"""Run a frozen encoder over the whole corpus once and cache its features.

The backbone never trains and every crop carries one fixed deformation
(Section 4.3.2), so its output per crop is a constant: computing it once lets
the metric head train on vectors instead of re-running the ViT every epoch.
The cached value is exactly features(Preprocess(crop)), the same path
FontEmbedder.forward() takes at serving time.

    .venv/Scripts/python.exe src/model/cache_features.py --backbone dinov2
    .venv/Scripts/python.exe src/model/cache_features.py --teacher data/models/teacher10
    .venv/Scripts/python.exe src/model/cache_features.py --backbone dinov2 --limit 256 --out /tmp/f.npz
    .venv/Scripts/python.exe src/model/cache_features.py --backbone dinov2_mid --corpus data/corpus_unknown

Other corpora (the unknown fonts, the mixed-font stressor set) cache to
data/features/<backbone>_<corpus suffix>.npz, e.g. dinov2_mid_unknown.npz.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

from encoder import BACKBONES, ROOT, Crops, Preprocess, collate, features, load_backbone, load_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", choices=BACKBONES, default="dinov2")
    ap.add_argument("--teacher", type=Path, help="cache the LoRA teacher's embedding instead")
    ap.add_argument("--limit", type=int, help="first N rows only (smoke runs)")
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--corpus", type=Path, default=ROOT / "data/corpus")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    rows = load_rows(args.corpus)[:args.limit]
    suffix = args.corpus.name.removeprefix("corpus")  # "" for the main corpus, "_unknown", ...
    if args.teacher:
        from train_teacher import load_teacher
        teacher = load_teacher(args.teacher).to(dev).eval()
        prep, encode = teacher.prep, teacher.embed
        out = args.out or ROOT / f"data/features/{args.teacher.name}{suffix}.npz"
    else:
        prep = Preprocess(args.backbone).to(dev)
        model = load_backbone(args.backbone).to(dev)
        encode = lambda x: features(args.backbone, model, x)
        out = args.out or ROOT / f"data/features/{args.backbone}{suffix}.npz"

    loader = torch.utils.data.DataLoader(Crops(rows), batch_size=args.batch, num_workers=args.workers,
                                         collate_fn=collate)
    feats = []
    with torch.no_grad(), torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
        for i, (imgs, _) in enumerate(loader):
            feats.append(encode(prep(imgs)).float().cpu().numpy().astype(np.float16))
            if i % 50 == 0:
                print(f"{i * args.batch}/{len(rows)}", file=sys.stderr)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, image_id=np.array([r["image_id"] for r in rows]), feats=np.concatenate(feats))
    print(f"{len(rows)} x {feats[0].shape[1]} -> {out}")


if __name__ == "__main__":
    main()
