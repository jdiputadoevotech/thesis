"""Shared style + drawing helpers for all thesis figures (300 dpi print PNGs)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

DPI = 300
FIGURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "figures"))

COLORS = {
    "ink":       "#1E293B",   # structure, arrows, primary text
    "text":      "#0F172A",
    "muted":     "#64748B",   # secondary labels, frames
    "grid":      "#E2E8F0",
    "teal":      "#0F766E",   # known / accepted / positive
    "blue":      "#2563EB",
    "orange":    "#D97706",   # intermediate ops, position info
    "rose":      "#BE123C",   # rejected / out-of-set / error
    "box":       "#F1F5F9",   # neutral surface
    "teal_bg":   "#E3F2EF",
    "blue_bg":   "#EAF1FE",
    "orange_bg": "#FCF1DF",
    "rose_bg":   "#FBE9ED",
}


def pick_font(*names):
    """Return the first installed font family from names, else a safe default."""
    for n in names:
        try:
            font_manager.findfont(n, fallback_to_default=False)
            return n
        except Exception:
            pass
    return "DejaVu Serif"


def apply_style():
    plt.rcParams.update({
        "figure.dpi": DPI,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "text.color": COLORS["text"],
        "axes.edgecolor": COLORS["muted"],
        "axes.linewidth": 0.8,
        "axes.labelcolor": COLORS["text"],
        "axes.titlecolor": COLORS["text"],
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "grid.color": COLORS["grid"],
        "grid.linewidth": 0.5,
    })


def save_figure(fig, name):
    os.makedirs(FIGURES_DIR, exist_ok=True)
    path = os.path.join(FIGURES_DIR, f"{name}.png")
    fig.patch.set_facecolor("white")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    print(f"Saved {path}")


def draw_box(ax, cx, cy, w, h, title, sub=None, fc=None, ec=None, tc=None,
             fs=10, sub_fs=8.5, lw=1.3):
    """Rounded box centred at (cx, cy) with a bold title and optional muted subtitle."""
    fc = fc or COLORS["box"]
    ec = ec or COLORS["ink"]
    tc = tc or COLORS["ink"]
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.02",
        fc=fc, ec=ec, lw=lw, zorder=3))
    if sub:
        ax.text(cx, cy + 0.06 * h, title, ha="center", va="bottom",
                fontsize=fs, weight="bold", color=tc, zorder=4)
        ax.text(cx, cy - 0.06 * h, sub, ha="center", va="top",
                fontsize=sub_fs, color=COLORS["muted"], zorder=4)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=fs, weight="bold", color=tc, zorder=4)


def draw_arrow(ax, p_from, p_to, color=None, lw=1.4, style="-|>", rad=0.0):
    ax.annotate("", xy=p_to, xytext=p_from, zorder=2,
                arrowprops=dict(arrowstyle=style, color=color or COLORS["ink"],
                                lw=lw, mutation_scale=15, shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}"))
