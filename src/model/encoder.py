"""The served recognizer: preprocessing, frozen backbone, metric head f_theta.

Preprocessing lives inside forward() so the corpus PNG at training time and the
localizer's crop at serving time pass through one code path (Section 4.3.2).
Backbones are swappable by name so the comparison of Section 4.10.2 re-runs
the same recipe with only the encoder changed.

    .venv/Scripts/python.exe src/model/encoder.py --check
"""

import argparse
import csv
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SIZE = 224
IMAGENET = ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))

# name -> (checkpoint, normalization). SigLIP was pretrained on [-1, 1] inputs;
# feeding it ImageNet statistics would handicap it in the comparison.
BACKBONES = {
    "dinov2": ("facebook/dinov2-base", IMAGENET),
    "siglip": ("google/siglip-base-patch16-224", ((0.5,) * 3, (0.5,) * 3)),
    "vit": ("google/vit-base-patch16-224", ((0.5,) * 3, (0.5,) * 3)),
    "convnext": ("facebook/convnext-tiny-224", IMAGENET),
    "dinov2_last4": ("facebook/dinov2-base", IMAGENET),
    "dinov2_mid": ("facebook/dinov2-base", IMAGENET),
}

# Multi-layer variants of the same frozen DINOv2: which of its 12 blocks feed
# the head. last4 mirrors DINOv2's own linear evaluation (Oquab et al., 2024);
# mid spreads across depth, on the premise that letterform style sits in
# middle layers rather than the semantic last one.
LAYERS = {"dinov2_last4": (9, 10, 11, 12), "dinov2_mid": (3, 6, 9, 12)}


class Preprocess(nn.Module):
    """uint8 crops (HxW or HxWx3, any size) -> normalized 3x224x224 batch.
    Square-pad with the crop's border median (its background), resize,
    grayscale, replicate to three channels, normalize (Section 4.4.2)."""

    def __init__(self, backbone="dinov2"):
        super().__init__()
        mean, std = BACKBONES[backbone][1]
        self.register_buffer("mean", torch.tensor(mean).view(1, 3, 1, 1))
        self.register_buffer("std", torch.tensor(std).view(1, 3, 1, 1))

    def one(self, img):
        x = img.to(self.mean.device, torch.float32)
        if x.ndim == 3:  # RGB -> luminance, same weights as the renderer
            x = x[..., 0] * 0.299 + x[..., 1] * 0.587 + x[..., 2] * 0.114
        h, w = x.shape
        border = torch.cat([x[0], x[-1], x[:, 0], x[:, -1]])
        side = max(h, w)
        top, left = (side - h) // 2, (side - w) // 2
        sq = torch.full((side, side), float(border.median()), device=x.device)
        sq[top:top + h, left:left + w] = x
        return F.interpolate(sq[None, None], size=(SIZE, SIZE), mode="bilinear",
                             antialias=True, align_corners=False)[0]

    def forward(self, imgs):
        x = torch.stack([self.one(i) for i in imgs]) / 255.0
        return (x.expand(-1, 3, -1, -1) - self.mean) / self.std


def load_backbone(name):
    from transformers import AutoModel, SiglipVisionModel
    ckpt = BACKBONES[name][0]
    model = SiglipVisionModel.from_pretrained(ckpt) if name == "siglip" else AutoModel.from_pretrained(ckpt)
    return model.eval().requires_grad_(False)


def features(name, model, x):
    """[CLS || mean patch] for the ViTs (SigLIP has no CLS: its pooled token
    stands in), pooled map for ConvNeXt, which has no patch tokens. Multi-layer
    variants concatenate that summary per layer, each through the final
    LayerNorm so every layer sits on the scale the last one is read at."""
    if name in LAYERS:
        hs = model(pixel_values=x, output_hidden_states=True).hidden_states
        return torch.cat([torch.cat([h[:, 0], h[:, 1:].mean(1)], 1)
                          for h in (model.layernorm(hs[i]) for i in LAYERS[name])], 1)
    out = model(pixel_values=x)
    if name == "convnext":
        return out.pooler_output
    h = out.last_hidden_state
    if name == "siglip":
        return torch.cat([out.pooler_output, h.mean(1)], 1)
    return torch.cat([h[:, 0], h[:, 1:].mean(1)], 1)


class Head(nn.Module):
    """f_theta: frozen-backbone features -> 256-d unit-norm font embedding."""

    def __init__(self, d_in, d_out=256, d_hidden=512):
        super().__init__()
        self.net = nn.Sequential(nn.LayerNorm(d_in), nn.Linear(d_in, d_hidden),
                                 nn.GELU(), nn.Linear(d_hidden, d_out))

    def forward(self, f):
        return F.normalize(self.net(f.float()), dim=-1)


class FontEmbedder(nn.Module):
    """What Increments 3 and 4 load: raw crops in, font embeddings out."""

    def __init__(self, backbone, head):
        super().__init__()
        self.name = backbone
        self.prep = Preprocess(backbone)
        self.backbone = load_backbone(backbone)
        self.head = head

    @classmethod
    def load(cls, path):
        ck = torch.load(path, map_location="cpu")
        head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512))
        head.load_state_dict(ck["state_dict"])
        return cls(ck["backbone"], head).eval()

    @torch.no_grad()
    def forward(self, imgs):
        return self.head(features(self.name, self.backbone, self.prep(imgs)))


# --- corpus access, shared by the training scripts ---

def load_rows(corpus=ROOT / "data/corpus"):
    return list(csv.DictReader((corpus / "metadata.csv").open()))


def read_crop(row):
    # Paths were written on Windows; normalize so the corpus also loads on POSIX.
    return torch.from_numpy(np.array(Image.open(ROOT / row["image_path"].replace("\\", "/"))))


class Crops(torch.utils.data.Dataset):
    def __init__(self, rows, labels=None):
        self.rows, self.labels = rows, labels

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return read_crop(self.rows[i]), (self.labels[i] if self.labels is not None else i)


def collate(batch):
    imgs, ys = zip(*batch)
    return list(imgs), torch.tensor(ys)


def check():
    prep = Preprocess()
    img = torch.full((40, 200), 30, dtype=torch.uint8)
    img[10:30, 20:180] = 220  # a wide ink bar on a dark background
    a, b = prep([img]), prep([img])
    assert a.shape == (1, 3, SIZE, SIZE) and torch.equal(a, b), "not deterministic"
    gray = a[0, 0] * IMAGENET[1][0] + IMAGENET[0][0]
    rows = (gray > 0.5).any(1).nonzero()
    cols = (gray > 0.5).any(0).nonzero()
    bar_h, bar_w = rows.max() - rows.min() + 1, cols.max() - cols.min() + 1
    assert abs(bar_w / bar_h - 8.0) < 0.6, f"aspect distorted: {bar_w}/{bar_h}"
    assert abs(float(gray[0, 0]) - 30 / 255) < 1e-3, "pad did not match background"
    rgb = torch.stack([img] * 3, -1)
    assert torch.allclose(prep([rgb]), a, atol=1e-5), "RGB and L inputs disagree"
    z = Head(1536)(torch.randn(5, 1536))
    assert z.shape == (5, 256) and torch.allclose(z.norm(dim=1), torch.ones(5), atol=1e-5)
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    if ap.parse_args().check:
        check()
