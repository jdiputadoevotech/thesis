"""One-knob-at-a-time sweep of the metric head around its defaults.

Each run changes exactly one setting from train_head.py's defaults, so each
row reads as that knob's effect on validation Top-1. Cached features make a
run ~2 min. Selection is on the validation split only: the test split stays
untouched for Chapter 5. Results are written after every run, so a crash
keeps what finished.

    .venv/Scripts/python.exe src/model/sweep.py
    .venv/Scripts/python.exe src/model/sweep.py --out reports/incr2/sweep_teacher10.json
"""

import os

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import argparse
import json
import sys
import time
from pathlib import Path

import torch

from train_head import ROOT, TEACHER_CACHE, evaluate, fit, parser, setup

SWEEP = [
    {},  # the current defaults, as the reference row
    {"kd": 0.5}, {"kd": 2.0}, {"kd": 4.0},
    {"temp": 0.05}, {"temp": 0.2},
    {"lr": 5e-4}, {"lr": 2e-3},
    {"margin": 0.1}, {"margin": 0.4},
    {"dim": 128}, {"dim": 512, "hidden": 1024},
    {"p": 16, "k": 8}, {"p": 64, "k": 2},
    {"epochs": 120},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "reports/incr2/sweep.json")
    ap.add_argument("--teacher-cache", type=Path, default=TEACHER_CACHE)
    cli = ap.parse_args()
    out = cli.out
    torch.use_deterministic_algorithms(True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    base = parser().parse_args([])
    base.teacher_cache = cli.teacher_cache
    d = setup(base.backbone, True, dev, cli.teacher_cache)
    tr, va = d.train_idx, d.val_idx
    results = []
    for change in SWEEP:
        args = argparse.Namespace(**{**vars(base), **change})
        t0 = time.time()
        head, log = fit(d.X, d.T, d.y, tr, va, d.fam, d.tier, args, dev)
        with torch.no_grad():
            z = head(d.X)
            m = evaluate(z[tr], d.y[tr], z[va], d.y[va], d.fam, [d.tier[i] for i in va])
        best = max(log, key=lambda e: e["sel_top1"])["epoch"]
        results.append({"change": change or "defaults", "best_epoch": best,
                        "minutes": round((time.time() - t0) / 60, 1), **m})
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"defaults": vars(base), "runs": results}, indent=2, default=str))
        print(f"{json.dumps(change or 'defaults'):32} top1 {m['top1']:.4f}  top3 {m['top3']:.4f}  "
              f"family {m['family_acc']:.4f}  severe {m['top1_severe']:.4f}  best ep {best}", flush=True)


if __name__ == "__main__":
    main()
