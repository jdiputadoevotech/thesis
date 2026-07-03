"""Figure 2 — CNN building blocks: conv -> pool -> conv -> pool -> FC -> embedding."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from _style import apply_style, save_figure, draw_arrow, pick_font, COLORS

SERIF = pick_font("Georgia", "Times New Roman")


def stack(ax, cx, cy, size, n, fc, ec, step=0.085):
    """Stack of n offset squares representing a bank of feature maps.
    Returns (front-face centre x, front-face centre y)."""
    for i in range(n):                       # back to front
        off = (n - 1 - i) * step - (n - 1) * step / 2
        ax.add_patch(mpatches.Rectangle(
            (cx - size / 2 - off, cy - size / 2 + off), size, size,
            fc=fc, ec=ec, lw=0.8, zorder=2 + i))
    front = (n - 1) * step / 2
    return cx + front, cy - front


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0.4, 6.4)
    ax.set_aspect("equal")
    ax.axis("off")
    cy = 4.35
    label_y = 1.55

    def label(x, title, sub):
        ax.text(x, label_y, title, fontsize=9, weight="bold", ha="center", va="top")
        ax.text(x, label_y - 0.42, sub, fontsize=8, ha="center", va="top",
                color=COLORS["muted"], linespacing=1.35)

    # --- Input glyph crop -----------------------------------------------------
    in_sz = 2.3
    ax.add_patch(mpatches.Rectangle((0.7, cy - in_sz / 2), in_sz, in_sz,
                                    fc="white", ec=COLORS["ink"], lw=1.4, zorder=2))
    ax.text(0.7 + in_sz / 2, cy - 0.08, "a", fontname=SERIF, fontsize=88,
            ha="center", va="center", color=COLORS["ink"], zorder=3)
    label(0.7 + in_sz / 2, "Input glyph crop", "64 × 64 × 1")

    # 5×5 kernel window inside the crop, label above the box
    kx, ky, ks = 1.05, cy + 0.42, 0.52
    ax.add_patch(mpatches.Rectangle((kx, ky), ks, ks, fc="none",
                                    ec=COLORS["rose"], lw=1.4, zorder=5))
    ax.text(kx + ks / 2, cy + in_sz / 2 + 0.14, "5×5 kernel", fontsize=7.5,
            color=COLORS["rose"], ha="center", va="bottom", weight="bold", zorder=5)

    # --- Conv1 / Pool1 / Conv2 / Pool2 ---------------------------------------
    stack(ax, 4.6, cy, 1.8, 6, COLORS["teal_bg"], COLORS["teal"])
    stack(ax, 7.05, cy, 1.0, 6, COLORS["teal_bg"], COLORS["teal"])
    stack(ax, 9.3, cy, 0.9, 9, COLORS["blue_bg"], COLORS["blue"])
    stack(ax, 11.15, cy, 0.55, 9, COLORS["blue_bg"], COLORS["blue"])
    label(4.6, "Convolution", "60 × 60 × 8\n(5×5 kernels)")
    label(7.05, "Max-pool", "30 × 30 × 8\n(2×2, stride 2)")
    label(9.3, "Convolution", "26 × 26 × 16\n(5×5 kernels)")
    label(11.15, "Max-pool", "13 × 13 × 16\n(2×2, stride 2)")

    # kernel projection lines to a point on the front conv1 map
    tx, ty = 4.35, cy + 0.35
    for corner in [(kx, ky), (kx + ks, ky), (kx, ky + ks), (kx + ks, ky + ks)]:
        ax.plot([corner[0], tx], [corner[1], ty], color=COLORS["rose"],
                lw=0.7, ls=":", alpha=0.8, zorder=8)
    ax.plot(tx, ty, "o", ms=3.5, color=COLORS["rose"], zorder=9)

    # --- Fully connected layer ------------------------------------------------
    fc_x = 12.9
    n_fc = 9
    fc_ys = np.linspace(cy + 1.35, cy - 1.35, n_fc)
    ax.add_patch(mpatches.FancyBboxPatch(
        (fc_x - 0.28, cy - 1.68), 0.56, 3.36, boxstyle="round,pad=0.02",
        fc="white", ec=COLORS["muted"], lw=1.0, zorder=2))
    for y in fc_ys:
        ax.plot(fc_x, y, "o", ms=5.5, mfc=COLORS["box"], mec=COLORS["ink"],
                mew=0.9, zorder=3)
    label(fc_x, "Fully connected", "flatten → dense")

    # --- Embedding vector -----------------------------------------------------
    em_x = 14.5
    n_em = 5
    em_ys = np.linspace(cy + 0.95, cy - 0.95, n_em)
    ax.add_patch(mpatches.FancyBboxPatch(
        (em_x - 0.28, cy - 1.28), 0.56, 2.56, boxstyle="round,pad=0.02",
        fc="white", ec=COLORS["teal"], lw=1.4, zorder=2))
    for y in em_ys:
        ax.plot(em_x, y, "o", ms=5.5, mfc=COLORS["teal"], mec=COLORS["teal"], zorder=3)
    ax.text(em_x, label_y, "Embedding", fontsize=9, weight="bold",
            ha="center", va="top", color=COLORS["teal"])
    ax.text(em_x, label_y - 0.42, "128-D font-style\nmetric space", fontsize=8,
            ha="center", va="top", color=COLORS["muted"], linespacing=1.35)

    # dense connections FC -> embedding
    for y1 in fc_ys:
        for y2 in em_ys:
            ax.plot([fc_x + 0.30, em_x - 0.30], [y1, y2],
                    color=COLORS["teal"], lw=0.4, alpha=0.18, zorder=1)

    # --- Stage arrows (FC -> embedding is carried by the dense fan) -----------
    for x0, x1 in [(3.06, 3.44), (5.78, 6.28), (7.82, 8.48),
                   (10.12, 10.50), (11.83, 12.55)]:
        draw_arrow(ax, (x0, cy), (x1, cy), lw=1.5)

    ax.set_title("Convolutional feature hierarchy for glyph-style encoding",
                 weight="bold", pad=10)
    save_figure(fig, "cnn_block")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
