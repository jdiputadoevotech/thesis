"""Figure 5 — Vision Transformer: patch embedding and self-attention over glyph
patches, shown with an explicit 9x9 attention-weight matrix."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from _style import apply_style, save_figure, draw_arrow, pick_font, COLORS

SERIF = pick_font("Georgia", "Times New Roman")


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(13, 6.9))
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0.3, 8.3)
    ax.set_aspect("equal")
    ax.axis("off")

    # ---------------- Input glyph crop split into 3x3 patches ----------------
    gx, gy, gs = 0.5, 3.2, 2.4
    step = gs / 3
    ax.add_patch(mpatches.Rectangle((gx, gy), gs, gs, fc="white",
                                    ec=COLORS["ink"], lw=1.5, zorder=2))
    ax.text(gx + gs / 2, gy + gs / 2 - 0.05, "f", fontname=SERIF, fontsize=105,
            ha="center", va="center", color=COLORS["ink"], alpha=0.16, zorder=3)
    for i in (1, 2):
        ax.plot([gx + i * step] * 2, [gy, gy + gs], color=COLORS["muted"],
                ls=":", lw=0.8, zorder=4)
        ax.plot([gx, gx + gs], [gy + i * step] * 2, color=COLORS["muted"],
                ls=":", lw=0.8, zorder=4)
    patch_centers = []
    for i in range(9):                      # P1 top-left, row-major
        r, c = divmod(i, 3)
        px = gx + c * step + step / 2
        py = gy + gs - (r * step + step / 2)
        patch_centers.append((px, py))
        ax.text(px, py, f"P{i + 1}", fontsize=8, weight="bold",
                color=COLORS["muted"], ha="center", va="center", zorder=5)
    ax.text(gx + gs / 2, gy - 0.35, "Input glyph crop\nsplit into 3 × 3 patches",
            fontsize=9, weight="bold", ha="center", va="top")

    # ---------------- Patch tokens + position embeddings ----------------------
    tok_x, tok_w, tok_h = 4.35, 0.75, 0.30
    ys = np.linspace(7.3, 1.5, 9)
    for (px, py), y in zip(patch_centers, ys):
        ax.plot([px + 0.25, tok_x], [py, y], color=COLORS["muted"],
                lw=0.7, alpha=0.25, zorder=1)
        ax.add_patch(mpatches.Rectangle((tok_x, y - tok_h / 2), tok_w, tok_h,
                                        fc=COLORS["box"], ec=COLORS["ink"],
                                        lw=0.9, zorder=3))
        ax.add_patch(mpatches.Circle((tok_x + tok_w + 0.35, y), 0.13,
                                     fc=COLORS["orange"], ec="none", zorder=3))
        ax.text(tok_x + tok_w + 0.35, y, "+", fontsize=8, weight="bold",
                color="white", ha="center", va="center", zorder=4)
    ax.text(tok_x + 0.55, 0.95, "Linear projection", fontsize=8.5,
            ha="center", va="top", weight="bold")
    ax.text(tok_x + 0.55, 0.60, "+ position embedding", fontsize=8.5,
            ha="center", va="top", weight="bold", color=COLORS["orange"])

    cy = ys[4]
    draw_arrow(ax, (tok_x + tok_w + 0.65, cy), (6.55, cy), lw=1.6)

    # ---------------- Transformer encoder block -------------------------------
    bx0, bx1, by0, by1 = 6.6, 11.6, 1.3, 7.75
    ax.add_patch(mpatches.FancyBboxPatch(
        (bx0, by0), bx1 - bx0, by1 - by0, boxstyle="round,pad=0.04",
        fc="#FBFCFE", ec=COLORS["teal"], lw=1.6, zorder=2))
    bcx = (bx0 + bx1) / 2
    ax.text(bcx, by1 - 0.35, "Transformer encoder block", fontsize=10.5,
            weight="bold", color=COLORS["teal"], ha="center", zorder=4)
    ax.text(bcx, by1 - 0.72, "each token projects to queries Q, keys K, values V",
            fontsize=8, color=COLORS["muted"], ha="center", zorder=4)

    # 9x9 attention matrix
    rng = np.random.RandomState(3)
    A = rng.rand(9, 9) * 0.22
    A[np.arange(9), np.arange(9)] += 0.42          # self-attention diagonal
    A[4] = [0.85, 0.20, 0.15, 0.25, 0.60, 0.20, 0.15, 0.25, 0.90]  # P5 -> P1, P9
    cell = 0.36
    mx0 = bcx - 9 * cell / 2
    my1 = 6.55
    for r in range(9):
        for c in range(9):
            ax.add_patch(mpatches.Rectangle(
                (mx0 + c * cell, my1 - (r + 1) * cell), cell, cell,
                fc=COLORS["rose"], alpha=min(A[r, c], 1.0) * 0.85,
                ec="white", lw=0.4, zorder=3))
    ax.add_patch(mpatches.Rectangle((mx0, my1 - 9 * cell), 9 * cell, 9 * cell,
                                    fc="none", ec=COLORS["ink"], lw=1.0, zorder=4))
    ax.add_patch(mpatches.Rectangle((mx0, my1 - 5 * cell), 9 * cell, cell,
                                    fc="none", ec=COLORS["teal"], lw=1.7, zorder=5))
    for idx in (0, 4, 8):
        ax.text(mx0 + idx * cell + cell / 2, my1 - 9 * cell - 0.12, f"P{idx + 1}",
                fontsize=6.5, color=COLORS["muted"], ha="center", va="top", zorder=4)
        ax.text(mx0 - 0.12, my1 - idx * cell - cell / 2, f"P{idx + 1}",
                fontsize=6.5, color=COLORS["muted"], ha="right", va="center", zorder=4)
    ax.text(bcx, my1 - 9 * cell - 0.42, "keys (patch index)", fontsize=7.5,
            color=COLORS["muted"], ha="center", va="top", zorder=4)
    ax.text(mx0 - 0.55, my1 - 4.5 * cell, "queries", fontsize=7.5,
            color=COLORS["muted"], ha="center", va="center", rotation=90, zorder=4)
    ax.text(bcx, by0 + 0.42, r"$A = \mathrm{softmax}(QK^{\top}/\sqrt{d_k})$",
            fontsize=10, ha="center", va="center", zorder=4)

    # ---------------- Contextualized output tokens ----------------------------
    out_x = 12.5
    for i, y in enumerate(ys):
        is_p5 = i == 4
        ax.plot([bx1 + 0.06, out_x], [y, y], color=COLORS["muted"],
                lw=0.7, alpha=0.3, zorder=1)
        ax.add_patch(mpatches.Rectangle(
            (out_x, y - tok_h / 2), tok_w, tok_h,
            fc=COLORS["teal"] if is_p5 else COLORS["box"],
            ec=COLORS["teal"] if is_p5 else COLORS["ink"],
            lw=1.4 if is_p5 else 0.9, zorder=3))
    ax.text(out_x + tok_w / 2, 0.95, "Contextualized\noutput embeddings",
            fontsize=8.5, weight="bold", color=COLORS["teal"],
            ha="center", va="top")
    ax.annotate("P5 aggregates stroke\nfeatures from P1 and P9",
                xy=(out_x + tok_w + 0.10, ys[4]), xytext=(13.35, 6.55),
                fontsize=8.5, weight="bold", color=COLORS["teal"],
                ha="left", va="center", zorder=5,
                arrowprops=dict(arrowstyle="->", color=COLORS["teal"], lw=1.2,
                                connectionstyle="arc3,rad=-0.25"))

    ax.set_title("Patch embedding and multi-head self-attention in a Vision Transformer",
                 weight="bold", pad=10)
    save_figure(fig, "vit_attention")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
