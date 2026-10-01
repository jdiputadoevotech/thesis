"""Re-render check: score a prediction by re-rendering the predicted font and
comparing it with the input crop (Section 4.10.2, verification of prediction).

The crop's text, line breaks and alignment are drawn from its seed before the
font is ever used (render_corpus.render_one), so the re-render reproduces the
exact layout, set clean in the predicted font. Both images are reduced to an
ink map (distance from the background, 0-1), so colour and polarity do not
matter. Four scores, higher = more similar except MSE:

  ssim      classic SSIM (Wang et al., 2004): 11x11 Gaussian window, sigma
            1.5, C1 = 0.01^2, C2 = 0.03^2; the re-render is resized to the crop
  mse       mean squared error on the same pair
  dssim     DeepSSIM (Zhang et al., 2024, eq. 8-10): Gram matrix of VGG16
            conv5_1 features, SSIM-style covariance ratio averaged over 4x4
            windows of the Gram matrices
  dssim_lite  DeepSSIM-Lite: the same ratio computed once, globally

Our implementation choices where the arXiv v1 paper is silent: features are
taken after conv5_1's ReLU; the Gram matrix is divided by the feature map's
h*w so images of different sizes compare; 4x4 windows do not overlap;
xi = 1e-6; images thinner than 64 px are scaled up (keeping aspect) so
VGG's pooling does not reduce them to nothing; ImageNet normalization on the ink map replicated to 3 channels.
The paper's "attention calibration" step is named but not specified in v1,
so it is not implemented.

Two questions are scored on known validation crops:
  verification  does the score separate correct from wrong predictions (AUROC)?
  robustness    re-rendering the TRUE font: does the score hold up as the
                crop's deformation grows, or does it collapse like pixel SSIM?

    .venv/bin/python src/model/rerender.py
    .venv/bin/python src/model/rerender.py --check
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageFont
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/data"))
from render_corpus import EM, TIERS, TIER_WEIGHTS, crop_to_ink, sample_text, typeset  # noqa: E402

from encoder import Head, read_crop  # noqa: E402

XI = 1e-6
MIN_SIDE = 64  # VGG16 halves the image 4 times before conv5_1; thinner inputs are scaled up
IMAGENET = (torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1), torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))


def layout(seed):
    """The crop's lines and alignment, replaying render_one's draws up to the font."""
    rng = np.random.default_rng(seed)
    tier = str(rng.choice(list(TIERS), p=TIER_WEIGHTS))
    if TIERS[tier][1] > 0:
        rng.uniform(*TIERS[tier], 3)
    words, lines = sample_text(rng)
    align = str(rng.choice(["left", "center", "right"]))
    return " ".join(words), lines, align


def rerender(ttf, lines, align):
    """Clean ink map (0-1) of the lines set in a font."""
    font = ImageFont.truetype(str(ROOT / ttf), EM)
    mask = crop_to_ink(typeset(font, lines, align, 0.0, np.random.default_rng(0)))
    return mask.astype(np.float32) / 255.0


def ink_map(img):
    """Distance from the background (border median), scaled to 0-1."""
    a = np.asarray(img, np.float32)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    d = np.abs(a - np.median(border))
    return d / max(float(d.max()), 1e-6)


def ssim(a, b):
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    blur = lambda x: cv2.GaussianBlur(x, (11, 11), 1.5)
    mu_a, mu_b = blur(a), blur(b)
    va, vb, cab = blur(a * a) - mu_a ** 2, blur(b * b) - mu_b ** 2, blur(a * b) - mu_a * mu_b
    s = ((2 * mu_a * mu_b + c1) * (2 * cab + c2)) / ((mu_a ** 2 + mu_b ** 2 + c1) * (va + vb + c2))
    return float(s.mean())


class DeepSSIM:
    def __init__(self, dev):
        from torchvision.models import VGG16_Weights, vgg16
        self.net = vgg16(weights=VGG16_Weights.IMAGENET1K_V1).features[:26].to(dev).eval()  # through relu5_1
        self.dev = dev

    @torch.no_grad()
    def gram(self, ink):
        x = torch.as_tensor(ink, device=self.dev)[None, None]
        if min(x.shape[-2:]) < MIN_SIDE:  # a thin word crop would pool to nothing in VGG
            x = F.interpolate(x, scale_factor=MIN_SIDE / min(x.shape[-2:]), mode="bilinear", align_corners=False)
        x = x.expand(1, 3, -1, -1)
        x = (x - IMAGENET[0].to(self.dev)) / IMAGENET[1].to(self.dev)
        f = self.net(x)[0].flatten(1)                                    # (512, h*w)
        return (f @ f.T) / f.shape[1]                                    # (512, 512)

    @staticmethod
    def score(gx, gy, window=None):
        """SSIM-style covariance ratio of two Gram matrices (eq. 10). window=None
        is DeepSSIM-Lite (one global window); window=4 averages 4x4 windows."""
        if window is None:
            x, y = gx.flatten() - gx.mean(), gy.flatten() - gy.mean()
            cov, vx, vy = (x * y).mean(), (x * x).mean(), (y * y).mean()
            return float((2 * cov + XI) / (vx + vy + XI))
        p = lambda t: F.avg_pool2d(t[None, None], window)[0, 0]
        mx, my = p(gx), p(gy)
        cov = p(gx * gy) - mx * my
        vx, vy = p(gx * gx) - mx ** 2, p(gy * gy) - my ** 2
        return float(((2 * cov + XI) / (vx + vy + XI)).mean())


def compare(crop_ink, ref_ink, deep):
    ref = cv2.resize(ref_ink, crop_ink.shape[::-1], interpolation=cv2.INTER_AREA)
    gx, gy = deep.gram(crop_ink), deep.gram(ref_ink)
    return {"ssim": ssim(crop_ink, ref), "mse": float(((crop_ink - ref) ** 2).mean()),
            "dssim": deep.score(gx, gy, 4), "dssim_lite": deep.score(gx, gy)}


def main(args):
    from open_set import decide, embed
    from train_head import prototypes

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    ck = torch.load(ROOT / args.head, map_location="cpu")
    head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512)).eval()
    head.load_state_dict(ck["state_dict"])
    fonts = ck["fonts"]
    fi = {f: i for i, f in enumerate(fonts)}
    ttf = {r["font_id"]: r["ttf_path"] for r in csv.DictReader((ROOT / "data/palette.csv").open())}

    rows, z = embed(head, ck["backbone"], "data/corpus")
    y = torch.tensor([fi[r["font_id"]] for r in rows])
    split = np.array([r["split"] for r in rows])
    protos = prototypes(z[split == "train"], y[split == "train"], len(fonts))
    val = np.flatnonzero(split == "validation")
    val = np.sort(np.random.default_rng(0).choice(val, size=min(args.n, len(val)), replace=False))
    _, pred, _ = decide(z[val], protos)

    deep = DeepSSIM(dev)
    out = []
    for n, (i, p) in enumerate(zip(val, pred)):
        r = rows[i]
        text, lines, align = layout(int(r["seed"]))
        assert text == r["word_text"], (r["image_id"], text, r["word_text"])
        crop = ink_map(Image.open(ROOT / r["image_path"].replace("\\", "/")))
        s_pred = compare(crop, rerender(ttf[fonts[p]], lines, align), deep)
        s_true = s_pred if fonts[p] == r["font_id"] else compare(crop, rerender(ttf[r["font_id"]], lines, align), deep)
        out.append({"correct": fonts[p] == r["font_id"], "tier": r["tier"], "pred": s_pred, "true": s_true})
        if n % 500 == 0:
            print(f"{n}/{len(val)}", file=sys.stderr)

    metrics = ("ssim", "mse", "dssim", "dssim_lite")
    correct = np.array([o["correct"] for o in out])
    tier = np.array([o["tier"] for o in out])
    report = {"head": args.head, "n": len(out), "top1": float(correct.mean()), "verification_auroc": {},
              "true_font_by_tier": {}, "correct_vs_wrong_mean": {}}
    for m in metrics:
        sign = -1 if m == "mse" else 1
        sp = np.array([o["pred"][m] for o in out])
        st = np.array([o["true"][m] for o in out])
        report["verification_auroc"][m] = float(roc_auc_score(correct, sign * sp))
        report["correct_vs_wrong_mean"][m] = {"correct": float(sp[correct].mean()), "wrong": float(sp[~correct].mean())}
        report["true_font_by_tier"][m] = {t: float(st[tier == t].mean()) for t in TIERS}
    path = ROOT / "reports/incr3/rerender.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ("n", "top1", "verification_auroc", "true_font_by_tier")}, indent=2))


def check():
    import render_corpus
    font = ImageFont.truetype(str(ROOT / "data/fonts/Roboto-400.ttf"), EM)
    for seed in range(30):  # layout() replays render_one exactly
        assert layout(seed)[0] == render_corpus.render_one(font, seed)[1]["word_text"], seed
    a = rerender("data/fonts/Roboto-400.ttf", ["Hamburg"], "left")
    assert abs(ssim(a, a) - 1) < 1e-6
    # A colour-inverted crop gives the same ink map.
    img = (np.random.default_rng(0).random((40, 120)) > 0.8) * 200 + 30
    assert np.allclose(ink_map(img.astype(np.uint8)), ink_map((255 - img).astype(np.uint8)))
    deep = DeepSSIM("cpu")
    g = deep.gram(a)
    assert abs(deep.score(g, g) - 1) < 1e-5 and abs(deep.score(g, g, 4) - 1) < 1e-5
    b = rerender("data/fonts/AbrilFatface-400.ttf", ["Hamburg"], "left")
    same, other = compare(a, a, deep), compare(a, b, deep)
    assert all(same[m] > other[m] for m in ("ssim", "dssim", "dssim_lite")), (same, other)
    thin = np.zeros((14, 220), np.float32); thin[4:10, 10:200] = 1  # a 14-px-tall crop must not crash VGG
    assert deep.gram(thin).shape == (512, 512)
    print("ok", {m: round(other[m], 3) for m in other})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--head", default="data/models/head_dinov2_mid_oe.pt")
    ap.add_argument("--n", type=int, default=3000, help="validation crops to score")
    a = ap.parse_args()
    check() if a.check else main(a)
