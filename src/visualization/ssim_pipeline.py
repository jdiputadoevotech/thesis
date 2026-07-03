"""Figure 6 — Re-render-and-compare: SSIM between the degraded input crop and a
pristine re-rendering of the predicted font."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from _style import apply_style, save_figure, pick_font, COLORS

SERIF = pick_font("Georgia", "Times New Roman")


def render_char(ch, fontsize=100):
    fig = plt.figure(figsize=(2, 2), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(0.5, 0.5, ch, fontname=SERIF, fontsize=fontsize,
            ha="center", va="center", color="black")
    fig.canvas.draw()
    img = np.asarray(fig.canvas.buffer_rgba())[:, :, 0].astype(float)
    plt.close(fig)
    return 1.0 - img / 255.0


def warp(img, alpha=15, sigma=4, seed=42):
    rs = np.random.RandomState(seed)
    dx = gaussian_filter(rs.rand(*img.shape) * 2 - 1, sigma, mode="constant") * alpha
    dy = gaussian_filter(rs.rand(*img.shape) * 2 - 1, sigma, mode="constant") * alpha
    x, y = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0]))
    idx = (y + dy).reshape(-1, 1), (x + dx).reshape(-1, 1)
    return np.clip(map_coordinates(img, idx, order=1).reshape(img.shape), 0, 1)


def create_figure():
    apply_style()
    pristine = render_char("a")
    degraded = gaussian_filter(warp(pristine), 0.8)
    degraded = np.clip(degraded + np.random.RandomState(42).normal(0, 0.03, degraded.shape), 0, 1)
    diff = np.abs(pristine - degraded)

    fig = plt.figure(figsize=(12, 4.4))
    ax1 = fig.add_axes([0.045, 0.16, 0.195, 0.60])
    ax2 = fig.add_axes([0.325, 0.16, 0.195, 0.60])
    ax3 = fig.add_axes([0.605, 0.16, 0.195, 0.60])
    ax4 = fig.add_axes([0.845, 0.18, 0.135, 0.56])

    panels = [
        (ax1, 1.0 - degraded, "gray", r"Input crop  $\tilde{x}$", "GenAI-hallucinated glyph", COLORS["rose"]),
        (ax2, 1.0 - pristine, "gray", r"Template  $x$", "re-rendered prediction", COLORS["teal"]),
        (ax3, diff, "Reds", "Structural error map", r"$|x - \tilde{x}|$ per pixel", COLORS["muted"]),
    ]
    for axp, img, cmap, title, sub, edge in panels:
        axp.imshow(img, cmap=cmap, vmin=0, vmax=1 if cmap == "gray" else 0.9)
        axp.set_xticks([])
        axp.set_yticks([])
        for s in axp.spines.values():
            s.set_color(edge)
            s.set_linewidth(1.6)
        axp.text(0.5, 1.155, title, transform=axp.transAxes, fontsize=10,
                 weight="bold", ha="center", va="bottom")
        axp.text(0.5, 1.05, sub, transform=axp.transAxes, fontsize=8.5,
                 ha="center", va="bottom", color=COLORS["muted"])

    # ---- SSIM score card -----------------------------------------------------
    ax4.axis("off")
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.add_patch(mpatches.FancyBboxPatch((0.03, 0.02), 0.94, 0.96,
                                          boxstyle="round,pad=0.03",
                                          fc=COLORS["box"], ec=COLORS["teal"], lw=1.5))
    ax4.text(0.5, 0.86, "SSIM score", fontsize=11, weight="bold", ha="center")
    ax4.text(0.5, 0.60, "0.742", fontsize=27, weight="bold", ha="center",
             color=COLORS["teal"])
    ax4.plot([0.18, 0.82], [0.47, 0.47], color=COLORS["grid"], lw=1)
    ax4.text(0.5, 0.40, "luminance   0.981\ncontrast      0.912\nstructure    0.828",
             fontsize=8.5, ha="center", va="top", color=COLORS["muted"], linespacing=1.6)
    ax4.text(0.5, 0.07, "(illustrative values)", fontsize=7, style="italic",
             ha="center", color=COLORS["muted"])

    # ---- Flow arrows (figure coordinates, from realized axes positions) ------
    fig.canvas.draw()
    p1, p2, p3, p4 = (a.get_position() for a in (ax1, ax2, ax3, ax4))
    ymid = (p1.y0 + p1.y1) / 2

    def harrow(x0, x1, y, color=COLORS["ink"]):
        fig.add_artist(mpatches.FancyArrowPatch(
            (x0, y), (x1, y), transform=fig.transFigure, arrowstyle="-|>",
            mutation_scale=15, color=color, lw=1.5))

    harrow(p1.x1 + 0.008, p2.x0 - 0.008, ymid)
    fig.text((p1.x1 + p2.x0) / 2, ymid + 0.045, "predict font,\nre-render",
             fontsize=8.5, weight="bold", ha="center", va="bottom")
    fig.text((p1.x1 + p2.x0) / 2, ymid - 0.045, "“Georgia”", fontsize=8.5,
             weight="bold", color=COLORS["teal"], ha="center", va="top")

    harrow(p2.x1 + 0.008, p3.x0 - 0.008, ymid)
    fig.text((p2.x1 + p3.x0) / 2, ymid + 0.045, "compare", fontsize=8.5,
             weight="bold", ha="center", va="bottom")

    harrow(p3.x1 + 0.008, p4.x0 - 0.008, ymid)

    # curved arrow: input crop feeds the comparison directly
    fig.add_artist(mpatches.FancyArrowPatch(
        (p1.x0 + 0.55 * p1.width, p1.y0 - 0.02), ((p3.x0 + p3.x1) / 2, p3.y0 - 0.02),
        transform=fig.transFigure, arrowstyle="-|>", mutation_scale=13,
        color=COLORS["muted"], lw=1.2, connectionstyle="arc3,rad=-0.12"))
    fig.text((p1.x1 + p3.x0) / 2 + 0.02, p1.y0 - 0.115,
             r"SSIM$(\tilde{x},\, x)$ over local windows", fontsize=8.5,
             color=COLORS["muted"], ha="center")

    fig.suptitle("Re-render-and-compare evaluation via structural similarity (SSIM)",
                 fontsize=12.5, weight="bold", y=0.97)
    save_figure(fig, "ssim_pipeline")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
