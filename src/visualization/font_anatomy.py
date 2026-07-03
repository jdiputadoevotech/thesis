"""Figure 1 — Typographic anatomy: font metrics (measured, not eyeballed) and the
four structural families (serif / sans-serif / display / monospace)."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.font_manager import FontProperties
from _style import apply_style, save_figure, pick_font, COLORS

SERIF = pick_font("Georgia", "Times New Roman")


def glyph(ax, ch, x, size, fp, color):
    """Draw glyph outline at baseline y=0 and return its extents (data units)."""
    tp = TextPath((0, 0), ch, size=size, prop=fp)
    tr = mtransforms.Affine2D().translate(x, 0) + ax.transData
    ax.add_patch(PathPatch(tp, transform=tr, fc=color, ec="none", zorder=3))
    return tp.get_extents()


def create_figure():
    apply_style()
    fig = plt.figure(figsize=(12, 5.9))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.5], hspace=0.12,
                          wspace=0.16, left=0.03, right=0.985, top=0.90, bottom=0.05)

    # ---------------- Top: font metrics measured from real glyph outlines ----
    ax = fig.add_subplot(gs[0, :])
    ax.set_xlim(0, 11.5)
    ax.set_aspect("equal")
    ax.set_anchor("S")          # hug the bottom row — no dead band between panels
    ax.axis("off")
    fp = FontProperties(family=SERIF)
    S = 1.5  # em size in data units

    e_H = glyph(ax, "H", 2.9, S, fp, COLORS["ink"])
    e_h = glyph(ax, "h", 4.8, S, fp, COLORS["ink"])
    e_x = glyph(ax, "x", 6.5, S, fp, COLORS["ink"])
    e_p = glyph(ax, "p", 8.1, S, fp, COLORS["ink"])
    cap, asc, xh, desc = e_H.ymax, e_h.ymax, e_x.ymax, e_p.ymin
    ax.set_ylim(desc - 0.28, asc + 0.30)

    # Guide lines at the exact measured heights
    for y, c, ls, lw in [(cap, COLORS["muted"], "--", 0.9),
                         (xh, COLORS["teal"], "--", 1.1),
                         (0.0, COLORS["ink"], "-", 1.3),
                         (desc, COLORS["muted"], "--", 0.9)]:
        ax.axhline(y, color=c, linestyle=ls, linewidth=lw, zorder=1)
    for y, label, c in [(cap, "Cap height", COLORS["muted"]),
                        (xh, "Mean line (x-height)", COLORS["teal"]),
                        (0.0, "Baseline", COLORS["ink"]),
                        (desc, "Descender line", COLORS["muted"])]:
        ax.text(0.12, y + 0.05, label, fontsize=8.5, weight="bold", color=c, va="bottom")

    def dim(x, y0, y1, label, color, label_dy=0.0):
        ax.annotate("", xy=(x, y1), xytext=(x, y0),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.3))
        ax.text(x + 0.14, (y0 + y1) / 2 + label_dy, label, fontsize=8.5,
                weight="bold", color=color, va="center")

    dim(4.8 + e_h.xmax + 0.28, xh, asc, "Ascender", COLORS["blue"])
    dim(6.5 + e_x.xmax + 0.28, 0, xh, "x-height", COLORS["teal"])
    dim(8.1 + e_p.xmax + 0.28, 0, desc, "Descender", COLORS["rose"])
    ax.set_title("Typographic reference lines and vertical font metrics",
                 weight="bold", pad=12)

    # ---------------- Bottom: the four structural families --------------------
    families = [
        ("Serif", pick_font("Times New Roman"), COLORS["teal"],
         "Bracketed terminals,\nhigh stroke contrast",
         [("Serif\nterminal", (0.30, -0.40), (0.66, -0.72), COLORS["rose"]),
          ("Enclosed\ncounter", (-0.03, -0.04), (-0.62, 0.52), COLORS["blue"])]),
        ("Sans-serif", pick_font("Arial"), COLORS["blue"],
         "Clean terminals,\nuniform stroke width",
         [("Clean\nterminal", (0.33, -0.36), (0.66, -0.70), COLORS["teal"]),
          ("Uniform\nstroke", (-0.29, 0.02), (-0.64, 0.52), COLORS["muted"])]),
        ("Display", pick_font("Impact"), COLORS["orange"],
         "Heavy weight,\ncompressed counters",
         [("Heavy\nstem", (-0.19, -0.08), (-0.64, 0.52), COLORS["orange"]),
          ("Compressed\ncounter", (-0.02, 0.16), (0.56, 0.58), COLORS["rose"])]),
        ("Monospace", pick_font("Courier New"), COLORS["muted"],
         "Fixed advance width,\nconstant spacing", []),
    ]

    for i, (name, font, _accent, desc_txt, callouts) in enumerate(families):
        axf = fig.add_subplot(gs[1, i])
        axf.set_xlim(-1, 1)
        axf.set_ylim(-1.35, 1.15)
        axf.set_aspect("equal")
        axf.set_anchor("N")
        axf.axis("off")

        axf.add_patch(mpatches.FancyBboxPatch(
            (-0.92, -0.92), 1.84, 1.84, boxstyle="round,pad=0.03",
            fc=COLORS["box"], ec=COLORS["muted"], lw=0.9, zorder=1))
        axf.text(0, 0.73, name, fontsize=11.5, weight="bold",
                 ha="center", color=COLORS["ink"], zorder=4)
        axf.text(0, -1.06, desc_txt, fontsize=8, ha="center", va="top",
                 color=COLORS["muted"], linespacing=1.35)
        axf.text(0, -0.18, "e", fontname=font, fontsize=95, ha="center",
                 va="center", color=COLORS["ink"], zorder=2)

        for label, tip, txt, c in callouts:
            axf.annotate(label, xy=tip, xytext=txt, fontsize=7.2, weight="bold",
                         color=c, ha="center", va="center", zorder=5,
                         arrowprops=dict(arrowstyle="->", color=c, lw=1.0,
                                         shrinkA=8, shrinkB=2))
        if name == "Monospace":
            for xv in (-0.58, 0.58):
                axf.plot([xv, xv], [-0.88, 0.55], color=COLORS["teal"],
                         linestyle=":", lw=1.1, zorder=2)
            axf.annotate("", xy=(0.58, 0.44), xytext=(-0.58, 0.44),
                         arrowprops=dict(arrowstyle="<->", color=COLORS["teal"], lw=1.0))
            axf.text(0, 0.34, "fixed advance", fontsize=7.2, weight="bold",
                     ha="center", va="top", color=COLORS["teal"])

    save_figure(fig, "font_anatomy")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
