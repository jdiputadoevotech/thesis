"""The deployable recognizer: one file with everything inference needs.

export   builds models/font_recognizer.pt from the trained head and the feature
         caches: head weights, the 80 font prototypes, the threshold tau, and
         the homogeneity check's frozen calibration. Needs the caches; run once.
Recognizer  loads that file and nothing else (DINOv2 itself downloads from the
         Hugging Face Hub), so a fresh clone can recognize fonts. This is what
         the web app (Increment 4) and the real-crop evaluation load.

    .venv/Scripts/python.exe src/model/bundle.py export
    .venv/Scripts/python.exe src/model/bundle.py --check
"""

import argparse
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import torch

from encoder import ROOT, FontEmbedder, Head

BUNDLE = ROOT / "models/font_recognizer.pt"


def export(head_path=ROOT / "data/models/head_dinov2_mid_oe.pt", out=BUNDLE):
    from homogeneity import CHOSEN, FALSE_ALARM, SEARCH_CACHE, calibrated
    from open_set import RECALL, calibrate, decide, embed
    from train_head import prototypes
    ck = torch.load(head_path, map_location="cpu")
    head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512)).eval()
    head.load_state_dict(ck["state_dict"])
    fonts = ck["fonts"]
    fi = {f: i for i, f in enumerate(fonts)}
    rows, z = embed(head, ck["backbone"], "data/corpus")
    y = torch.tensor([fi[r["font_id"]] for r in rows])
    split = np.array([r["split"] for r in rows])
    protos = prototypes(z[split == "train"], y[split == "train"], len(fonts))
    tau = calibrate(decide(z[split == "validation"], protos)[0])

    grid, _, cutoff = calibrated()
    v = np.load(str(SEARCH_CACHE).format(""))
    n = len(v["single_d"])
    cal = np.random.default_rng(0).permutation(n)[: n // 2]
    palette = {r["font_id"]: r for r in csv.DictReader((ROOT / "data/palette.csv").open())}
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()

    bundle = {
        "backbone": ck["backbone"], "d_in": ck["d_in"], "dim": ck.get("dim", 256), "hidden": ck.get("hidden", 512),
        "head_state_dict": ck["state_dict"],
        "fonts": [{"font_id": f, "family": palette[f]["family"], "family_class": palette[f]["family_class"]}
                  for f in fonts],
        "prototypes": protos.float(), "tau": tau, "recall": RECALL,
        "homogeneity": {**CHOSEN, "grid": grid.tolist(), "cutoff": cutoff, "false_alarm": FALSE_ALARM,
                        "mean": v["single_d"][cal].mean(0).tolist(), "std": (v["single_d"][cal].std(0) + 1e-6).tolist()},
        "provenance": {"exported": date.today().isoformat(), "from": str(Path(head_path).relative_to(ROOT).as_posix()),
                       "git_commit": commit, "results": "reports/incr3/FINDINGS.md (Final test results)"},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(bundle, out)
    print(f"-> {out} ({out.stat().st_size / 1e6:.1f} MB): tau {tau:.4f}, homogeneity cutoff {cutoff:.3f}")


class Recognizer:
    """Crop in, verdict out: the Top-K palette fonts with similarities, the
    known/unknown verdict against tau, and the homogeneity check (one split)."""

    def __init__(self, path=BUNDLE, device=None):
        from homogeneity import variant_scores
        b = torch.load(path, map_location="cpu", weights_only=False)
        self.dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
        head = Head(b["d_in"], b["dim"], b["hidden"])
        head.load_state_dict(b["head_state_dict"])
        self.emb = FontEmbedder(b["backbone"], head).eval().to(self.dev)
        self.fonts, self.protos, self.tau = b["fonts"], b["prototypes"], b["tau"]
        h = b["homogeneity"]
        self.grid = np.array(h["grid"])
        stats = (np.array(h["mean"]), np.array(h["std"])) if h["per_cut_z"] else None
        self.h_cut = h["cutoff"]
        self.h_score = lambda d, hw: variant_scores(d, hw, self.grid, h["lo"], h["hi"], h["min_aspect"], stats)
        self.provenance = b["provenance"]

    def embed(self, img):
        with torch.no_grad(), torch.autocast(self.dev, dtype=torch.float16, enabled=self.dev == "cuda"):
            return self.emb([img]).float().cpu()

    def topk(self, img, k=3):
        sims = (self.embed(img) @ self.protos.T)[0]
        v, i = sims.topk(k)
        return [(self.fonts[int(j)], float(s)) for s, j in zip(v, i)]

    def homogeneous(self, img):
        """(True, None) for one typeface, or (False, cut fraction) when flagged."""
        from homogeneity import cut_distances
        d = cut_distances(self.emb, [img], self.dev, self.grid)
        sc, arg = self.h_score(d, np.array([img.shape[:2]]))
        return (True, None) if sc[0] < self.h_cut else (False, float(self.grid[arg[0]]))

    def __call__(self, img, k=3):
        """img: uint8 HxW or HxWx3 tensor. Returns a dict per Section 4.4.2."""
        one, cut = self.homogeneous(img)
        top = self.topk(img, k)
        out = {"topk": top, "verdict": "known" if top[0][1] >= self.tau else "unknown",
               "homogeneous": one, "cut": cut, "halves": None}
        if not one:  # split once; a half still inhomogeneous is mixed typography
            c = int(round(img.shape[1] * cut))
            out["halves"] = []
            for half in (img[:, :c], img[:, c:]):
                h_top = self.topk(half, k)
                verdict = ("mixed" if not self.homogeneous(half)[0]
                           else "known" if h_top[0][1] >= self.tau else "unknown")
                out["halves"].append({"topk": h_top, "verdict": verdict})
        return out


def check():
    """The bundle must reproduce what the feature caches give."""
    from homogeneity import calibrated
    from open_set import calibrate, decide, embed
    from train_head import prototypes
    b = torch.load(BUNDLE, map_location="cpu", weights_only=False)
    ck = torch.load(ROOT / b["provenance"]["from"], map_location="cpu")
    head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512)).eval()
    head.load_state_dict(ck["state_dict"])
    fi = {f: i for i, f in enumerate(ck["fonts"])}
    rows, z = embed(head, ck["backbone"], "data/corpus")
    y = torch.tensor([fi[r["font_id"]] for r in rows])
    split = np.array([r["split"] for r in rows])
    protos = prototypes(z[split == "train"], y[split == "train"], len(fi))
    assert torch.allclose(protos, b["prototypes"]), "prototypes differ"
    assert abs(calibrate(decide(z[split == "validation"], protos)[0]) - b["tau"]) < 1e-9, "tau differs"
    assert abs(calibrated()[2] - b["homogeneity"]["cutoff"]) < 1e-9, "homogeneity cutoff differs"
    assert [f["font_id"] for f in b["fonts"]] == ck["fonts"]
    # A known crop through the Recognizer names the same font as the cached path.
    from encoder import read_crop
    rec = Recognizer()
    i = int(np.flatnonzero(split == "validation")[0])
    cached = ck["fonts"][int((z[i] @ protos.T).argmax())]
    served = rec(read_crop(rows[i]))["topk"][0][0]["font_id"]
    assert served == cached, (served, cached)
    print("ok: bundle matches the caches;", b["provenance"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", nargs="?", choices=["export"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.step == "export":
        export()
    else:
        ap.print_help()
