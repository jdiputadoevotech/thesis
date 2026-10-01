"""Closed-set baselines on the synthetic validation data (Section 4.10.2).

  storia  Storia-AI Google Font Classifier: EfficientNet-B3, 3,473 font files
          (storia/font-classify-onnx; Jiang et al., 2025, use it as their
          reference embedding). Preprocessing copied from its train.py:
          cut to <= 1024 px, resize the long side to the model size, pad white.
  chen    Chen et al. (2026), DINOv2 + LoRA merged, 394 weight variants of 32
          families (dchen0/font_classifier_v4). Preprocessing copied from its
          font_classifier_with_preprocessing.py: pad black to square,
          bilinear 224, ImageNet normalization.

Both name fonts at the family level here: a variant's score is folded into
its family by the maximum. Each is scored two ways:
  own catalogue   the baseline's native task, over all its families
  palette only    restricted to our palette families it knows, the same
                  closed-set question our head answers
A closed-set model has no "unknown" verdict, so on unknown fonts its FPR is
100% by construction. What is measured there is whether its own, larger
catalogue already contains and names the font (Storia covers all 20).

Chen et al. cover only 17 of the 80 palette families, so their rows use the
crops of those 17 only, and our head is scored on the same crops.

    .venv/bin/python src/model/baselines.py
"""

import argparse
import csv
import json
import re
import sys

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from encoder import ROOT, Head, load_rows

norm = lambda s: re.sub(r"[\s_\-]", "", s).lower()


def family_of_font_id(font_id):
    return norm(font_id.rsplit("-", 1)[0])


def fold(probs, class_families, families):
    """(N, classes) -> (N, families): each family scores its best variant."""
    out = np.full((probs.shape[0], len(families)), -np.inf, np.float32)
    col = {f: j for j, f in enumerate(families)}
    for c, f in enumerate(class_families):
        if f in col:
            out[:, col[f]] = np.maximum(out[:, col[f]], probs[:, c])
    return out


def topk(scores, truth_idx, k):
    order = np.argsort(-scores, 1)[:, :k]
    return float((order == truth_idx[:, None]).any(1).mean())


class Storia:
    def __init__(self):
        import onnxruntime as ort
        import yaml
        from huggingface_hub import hf_hub_download
        cfg = yaml.safe_load(open(hf_hub_download("storia/font-classify-onnx", "model_config.yaml")))
        self.size = cfg["size"]
        self.classes = [norm(re.split(r"[-\[]", c)[0]) for c in cfg["classnames"]]
        self.sess = ort.InferenceSession(hf_hub_download("storia/font-classify-onnx", "model.onnx"),
                                         providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

    def prep(self, img):
        import cv2
        a = np.array(img.convert("RGB"))[:1024, :1024]
        r = self.size / max(a.shape[:2])
        a = cv2.resize(a, (int(a.shape[1] * r), int(a.shape[0] * r)))
        dh, dw = self.size - a.shape[0], self.size - a.shape[1]
        a = cv2.copyMakeBorder(a, dh // 2, dh - dh // 2, dw // 2, dw - dw // 2, cv2.BORDER_CONSTANT,
                               value=(255, 255, 255))
        a = (a / 255.0 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        return a.transpose(2, 0, 1).astype(np.float32)

    def probs(self, imgs):
        logits = self.sess.run(None, {"input": np.stack([self.prep(i) for i in imgs])})[0]
        return torch.softmax(torch.as_tensor(logits), 1).numpy()


class Chen:
    def __init__(self, dev):
        from transformers import Dinov2ForImageClassification
        self.model = Dinov2ForImageClassification.from_pretrained("dchen0/font_classifier_v4").to(dev).eval()
        labels = self.model.config.id2label
        self.classes = [norm(labels[i].split("_")[0]) for i in range(len(labels))]
        self.dev = dev
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=dev).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=dev).view(1, 3, 1, 1)

    @torch.no_grad()
    def probs(self, imgs):
        batch = []
        for img in imgs:
            x = torch.as_tensor(np.array(img.convert("RGB")), device=self.dev).permute(2, 0, 1)[None].float() / 255
            h, w = x.shape[-2:]
            s = max(h, w)
            x = F.pad(x, ((s - w) // 2, s - w - (s - w) // 2, (s - h) // 2, s - h - (s - h) // 2), value=0)
            batch.append(F.interpolate(x, size=(224, 224), mode="bilinear", align_corners=False))
        x = (torch.cat(batch) - self.mean) / self.std
        return torch.softmax(self.model(pixel_values=x).logits, 1).cpu().numpy()


def run(model, rows, bs=32):
    out = []
    for i in range(0, len(rows), bs):
        imgs = [Image.open(ROOT / r["image_path"].replace("\\", "/")) for r in rows[i:i + bs]]
        out.append(model.probs(imgs))
        if (i // bs) % 50 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)
    return np.concatenate(out)


def score(probs, model, rows, families):
    s = fold(probs, model.classes, families)
    idx = {f: j for j, f in enumerate(families)}
    truth = np.array([idx[family_of_font_id(r["font_id"])] for r in rows])
    return {"n": len(rows), "top1": topk(s, truth, 1), "top3": topk(s, truth, 3)}


def head_scores(rows_subset, families, args):
    """Our final head on the same crops, nearest prototype among `families`."""
    from open_set import embed
    from train_head import prototypes
    ck = torch.load(ROOT / args.head, map_location="cpu")
    head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512)).eval()
    head.load_state_dict(ck["state_dict"])
    fi = {f: i for i, f in enumerate(ck["fonts"])}
    rows, z = embed(head, ck["backbone"], "data/corpus")
    y = torch.tensor([fi[r["font_id"]] for r in rows])
    tr = torch.tensor([r["split"] == "train" for r in rows])
    protos = prototypes(z[tr], y[tr], len(fi))
    keep = [fi[f] for f in ck["fonts"] if family_of_font_id(f) in families]
    pos = {r["image_id"]: k for k, r in enumerate(rows)}
    zs = z[[pos[r["image_id"]] for r in rows_subset]]
    sims = (zs @ protos[keep].T).numpy()
    kfam = [family_of_font_id(ck["fonts"][i]) for i in keep]
    truth = np.array([kfam.index(family_of_font_id(r["font_id"])) for r in rows_subset])
    return {"n": len(rows_subset), "top1": topk(sims, truth, 1), "top3": topk(sims, truth, 3)}


def main(args):
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    split = "test" if args.final else "validation"
    known = [r for r in load_rows() if r["split"] == split]
    unknown = [r for r in load_rows(ROOT / "data/corpus_unknown") if r["split"] == split]
    if args.limit:
        rng = np.random.default_rng(0)
        known = [known[i] for i in sorted(rng.choice(len(known), args.limit, replace=False))]
        unknown = [unknown[i] for i in sorted(rng.choice(len(unknown), args.limit, replace=False))]
    palette = sorted({family_of_font_id(r["font_id"]) for r in load_rows() if r["split"] == "train"})
    report = {"split": split}

    st = Storia()
    own = sorted(set(st.classes))
    assert set(palette) <= set(own), set(palette) - set(own)
    p_known, p_unknown = run(st, known), run(st, unknown)
    report["storia"] = {
        "catalogue_families": len(own),
        "known_own_catalogue": score(p_known, st, known, own),
        "known_palette_only": score(p_known, st, known, palette),
        "unknown_own_catalogue": score(p_unknown, st, unknown, own),
    }
    print("storia", json.dumps(report["storia"]))

    ch = Chen(dev)
    chen_own = sorted(set(ch.classes))
    shared = [f for f in palette if f in chen_own]
    sub = [r for r in known if family_of_font_id(r["font_id"]) in shared]
    p_sub = run(ch, sub)
    report["chen"] = {
        "catalogue_families": len(chen_own), "shared_palette_families": shared,
        "known_own_catalogue": score(p_sub, ch, sub, chen_own),
        "known_shared_only": score(p_sub, ch, sub, shared),
        "storia_same_crops_shared_only": score(run(st, sub), st, sub, shared),
        "ours_same_crops_shared_only": head_scores(sub, shared, args),
    }
    print("chen", json.dumps(report["chen"]))
    report["ours_palette"] = head_scores(known, palette, args)
    out = ROOT / f"reports/incr3/baselines{'_final' if args.final else ''}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default="data/models/head_dinov2_mid_oe.pt")
    ap.add_argument("--limit", type=int, help="random N crops per set (smoke runs)")
    ap.add_argument("--final", action="store_true", help="score the TEST partition (Chapter 5 only)")
    main(ap.parse_args())
