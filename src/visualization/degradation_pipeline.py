"""Figure 3 — Synthetic degradation pipeline:
clean render -> elastic warp -> blur + noise -> kerning jitter (cumulative)."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from _style import apply_style, save_figure, pick_font, COLORS

SERIF = pick_font("Georgia", "Times New Roman")


def render_word(text, offsets=None, fontsize=46):
    """Rasterize a word to a [0,1] ink array (1 = ink)."""
    fig = plt.figure(figsize=(4, 1.15), dpi=110, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    offsets = offsets or [0.0] * len(text)
    xs = np.linspace(0.14, 0.86, len(text))
    for x, dx, ch in zip(xs, offsets, text):
        ax.text(x + dx, 0.48, ch, fontname=SERIF, fontsize=fontsize,
                ha="center", va="center", color="black")
    fig.canvas.draw()
    img = np.asarray(fig.canvas.buffer_rgba())[:, :, 0].astype(float)
    plt.close(fig)
    return 1.0 - img / 255.0


def elastic_warp(img, alpha=13, sigma=3, seed=42):
    rs = np.random.RandomState(seed)
    dx = gaussian_filter(rs.rand(*img.shape) * 2 - 1, sigma, mode="constant") * alpha
    dy = gaussian_filter(rs.rand(*img.shape) * 2 - 1, sigma, mode="constant") * alpha
    x, y = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0]))
    idx = (y + dy).reshape(-1, 1), (x + dx).reshape(-1, 1)
    return np.clip(map_coordinates(img, idx, order=1).reshape(img.shape), 0, 1)


def blur_noise(img, sigma=1.1, noise=0.07, seed=7):
    rs = np.random.RandomState(seed)
    return np.clip(gaussian_filter(img, sigma) + rs.normal(0, noise, img.shape), 0, 1)


def create_figure():
    apply_style()
    word = "Style"
    clean = render_word(word)
    warped = elastic_warp(clean)
    noisy = blur_noise(warped)
    jittered = blur_noise(elastic_warp(
        render_word(word, offsets=[-0.03, -0.05, 0.04, -0.01, 0.05])))

    stages = [
        ("1 · Clean render", clean, "Pristine vector rasterization"),
        ("2 · + Elastic warp", warped, "Probabilistic glyph deformation"),
        ("3 · + Blur & noise", noisy, "Gaussian blur, sensor noise"),
        ("4 · + Kerning jitter", jittered, "Per-character tracking offsets"),
    ]

    # vertical stack: reads top-to-bottom so the figure stays legible at
    # single-column width in the paper
    fig, axes = plt.subplots(4, 1, figsize=(5.6, 10.4))
    fig.subplots_adjust(left=0.06, right=0.94, top=0.955, bottom=0.015,
                        hspace=0.62)

    for axp, (title, img, sub) in zip(axes, stages):
        axp.imshow(1.0 - img, cmap="gray", vmin=0, vmax=1)
        axp.set_title(title, fontsize=11.5, weight="bold", pad=6)
        axp.set_xticks([])
        axp.set_yticks([])
        for s in axp.spines.values():
            s.set_color(COLORS["muted"])
            s.set_linewidth(0.9)
        axp.text(0.5, -0.10, sub, transform=axp.transAxes, fontsize=9.5,
                 ha="center", va="top", color=COLORS["muted"])

    # flow arrows between panels, pointing down (figure coordinates)
    for a, b in zip(axes[:-1], axes[1:]):
        pa, pb = a.get_position(), b.get_position()
        x = (pa.x0 + pa.x1) / 2
        fig.add_artist(mpatches.FancyArrowPatch(
            (x, pa.y0 - 0.030), (x, pb.y1 + 0.036),
            transform=fig.transFigure, arrowstyle="-|>", mutation_scale=16,
            color=COLORS["ink"], lw=1.6))

    save_figure(fig, "degradation_pipeline")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
