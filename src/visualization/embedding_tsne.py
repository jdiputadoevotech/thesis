"""Measured embedding space (Increment 2): t-SNE of validation crops, frozen
DINOv2 features vs. the trained metric head, colored by family class.

Unlike Figure 4 (embedding_space.py, a conceptual sketch), every point here is
a real validation crop. Needs data/features/dinov2.npz and
data/models/head_dinov2.pt (src/model/cache_features.py, train_head.py).

    .venv/Scripts/python.exe src/visualization/embedding_tsne.py
"""
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.manifold import TSNE

from _style import COLORS, apply_style, save_figure

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/model"))
from encoder import Head  # noqa: E402

FAMILY_COLORS = {"sans-serif": COLORS["teal"], "serif": COLORS["blue"],
                 "display": COLORS["orange"], "monospace": COLORS["rose"]}
N_POINTS = 4000  # t-SNE cost is quadratic; a seeded subsample reads the same
SEED = 2026


def create_figure():
    apply_style()
    rows = list(csv.DictReader((ROOT / "data/corpus/metadata.csv").open()))
    feats = np.load(ROOT / "data/features/dinov2.npz")["feats"]
    ck = torch.load(ROOT / "data/models/head_dinov2.pt", map_location="cpu")
    head = Head(ck["d_in"])
    head.load_state_dict(ck["state_dict"])

    val = np.flatnonzero([r["split"] == "validation" for r in rows])
    val = np.sort(np.random.default_rng(SEED).choice(val, size=min(N_POINTS, len(val)), replace=False))
    fam = np.array([rows[i]["family_class"] for i in val])
    x = torch.tensor(feats[val]).float()
    with torch.no_grad():
        spaces = [("Frozen DINOv2 features", torch.nn.functional.normalize(x, dim=-1).numpy()),
                  ("Trained metric head $f_\\theta$", head(x).numpy())]

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for ax, (title, z) in zip(axes, spaces):
        xy = TSNE(n_components=2, metric="cosine", init="pca", random_state=SEED).fit_transform(z)
        for f, c in FAMILY_COLORS.items():
            m = fam == f
            ax.scatter(xy[m, 0], xy[m, 1], s=3, color=c, alpha=0.6, linewidths=0, label=f)
        ax.set_title(title)
        ax.set_xticks([]); ax.set_yticks([])
    axes[1].legend(title="Family class", markerscale=4, loc="lower right", frameon=False)
    fig.tight_layout()
    save_figure(fig, "embedding_tsne")


if __name__ == "__main__":
    create_figure()
