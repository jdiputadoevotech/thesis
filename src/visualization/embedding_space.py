"""Figure 4 — Open-set metric embedding space: known-font clusters with
distance-threshold acceptance regions and open-space rejection."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from _style import apply_style, save_figure, COLORS


def create_figure():
    apply_style()
    rng = np.random.RandomState(11)

    clusters = [
        ("Roboto (sans-serif)", (1.5, 2.2), COLORS["teal"], "o"),
        ("Garamond (serif)", (4.2, 1.2), COLORS["blue"], "s"),
        ("Consolas (monospace)", (2.3, -1.2), COLORS["orange"], "^"),
    ]
    R = 0.85  # acceptance radius (threshold theta)

    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    ax.set_aspect("equal")

    for name, (mx, my), c, marker in clusters:
        pts = rng.normal([mx, my], 0.26, size=(24, 2))
        ax.scatter(pts[:, 0], pts[:, 1], marker=marker, s=48, facecolor=c,
                   edgecolor="white", linewidth=0.7, alpha=0.9, zorder=3, label=name)
        ax.add_patch(mpatches.Circle((mx, my), R, fc=c, ec=c, alpha=0.07, zorder=1))
        ax.add_patch(mpatches.Circle((mx, my), R, fc="none", ec=c, ls="--",
                                     lw=1.2, alpha=0.8, zorder=2))
        ax.text(mx, my - R - 0.13, r"$d \leq \theta$", fontsize=9, weight="bold",
                color=c, ha="center", va="top")

    # In-palette warped query: lands inside the Roboto acceptance region
    qx, qy = 1.95, 1.75
    ax.scatter([qx], [qy], marker="*", s=340, facecolor=COLORS["teal"],
               edgecolor=COLORS["ink"], linewidth=1.1, zorder=5,
               label="Warped in-palette query")
    ax.annotate("Degraded in-palette query\naccepted → matched to Roboto",
                xy=(qx + 0.10, qy - 0.02), xytext=(0.15, 3.45),
                fontsize=9, weight="bold", color=COLORS["teal"], ha="left", va="top",
                arrowprops=dict(arrowstyle="->", color=COLORS["teal"], lw=1.3,
                                connectionstyle="arc3,rad=-0.2"))

    # Out-of-palette hallucinated crop: far from every prototype
    hx, hy = 4.55, -1.05
    ax.scatter([hx], [hy], marker="X", s=240, facecolor=COLORS["rose"],
               edgecolor=COLORS["ink"], linewidth=1.1, zorder=5,
               label="Hallucinated crop (unknown)")
    ax.annotate("Hallucinated crop\n" + r"$d > \theta$ everywhere → rejected",
                xy=(hx + 0.02, hy - 0.22), xytext=(5.0, -2.15),
                fontsize=9, weight="bold", color=COLORS["rose"], ha="center", va="top",
                arrowprops=dict(arrowstyle="->", color=COLORS["rose"], lw=1.3,
                                connectionstyle="arc3,rad=0.15"))

    ax.text(2.65, 0.45, "open space\n(no acceptance region)", fontsize=9,
            style="italic", color=COLORS["muted"], ha="center")

    ax.set_xlim(-0.3, 6.0)
    ax.set_ylim(-3.0, 3.8)
    ax.set_xlabel("Embedding dimension 1")
    ax.set_ylabel("Embedding dimension 2")
    ax.set_title("Open-set recognition in the learned metric space",
                 weight="bold", pad=12)
    ax.grid(True, alpha=0.55)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", frameon=True, framealpha=0.95,
              edgecolor=COLORS["grid"], fontsize=8.5)

    save_figure(fig, "embedding_space")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
