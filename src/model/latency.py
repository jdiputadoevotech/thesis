"""Per-crop inference latency of trained heads (Section 4.10.2, Table 5).

Times the served path, FontEmbedder: preprocessing, frozen backbone, head,
one crop at a time, the way the demo serves a request. Run on the machine
that will serve the demo. Reports the median over N crops after a warm-up,
on GPU (synchronized) and on CPU, plus the backbone's parameter count.

    .venv/Scripts/python.exe src/model/latency.py data/models/head_bb_dinov2.pt data/models/head_bb_siglip.pt
"""

import argparse
import json
import platform
import sys
import time

import numpy as np
import torch

from encoder import ROOT, FontEmbedder, load_rows, read_crop


def time_one(emb, crops, dev, warmup=5):
    emb = emb.to(dev)
    times = []
    for i, c in enumerate(crops):
        if dev == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        emb([c])
        if dev == "cuda":
            torch.cuda.synchronize()
        if i >= warmup:
            times.append((time.perf_counter() - t0) * 1000)
    return float(np.median(times))


def main(args):
    rows = [r for r in load_rows() if r["split"] == "validation"]
    rows = [rows[i] for i in np.random.default_rng(0).choice(len(rows), args.n + 5, replace=False)]
    crops = [read_crop(r) for r in rows]
    out = {"machine": {"cpu": platform.processor(), "torch": torch.__version__,
                       "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                       "cpu_threads": torch.get_num_threads()},
           "n": args.n, "heads": {}}
    for h in args.heads:
        emb = FontEmbedder.load(ROOT / h)
        params = sum(p.numel() for p in emb.backbone.parameters())
        res = {"backbone": emb.name, "backbone_params_m": round(params / 1e6, 1)}
        if torch.cuda.is_available():
            res["gpu_ms"] = time_one(emb, crops, "cuda")
        res["cpu_ms"] = time_one(emb, crops[: args.n_cpu + 5], "cpu")
        out["heads"][h] = res
        print(h, res, file=sys.stderr)
        del emb
        torch.cuda.empty_cache()
    path = ROOT / "reports/incr3/latency.json"
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("heads", nargs="+")
    ap.add_argument("--n", type=int, default=50, help="crops timed on GPU")
    ap.add_argument("--n-cpu", type=int, default=20, help="crops timed on CPU (slower)")
    main(ap.parse_args())
