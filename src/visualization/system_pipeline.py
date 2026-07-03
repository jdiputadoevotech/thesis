"""Figure 7 — End-to-end open-set font identification pipeline (flowchart).
Pure matplotlib: no Graphviz binary required."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, draw_box, draw_arrow, COLORS


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(8.2, 10.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.6, 12.4)
    ax.axis("off")

    W, H = 5.2, 0.95
    steps = [
        (11.45, "Input generative AI image", "contains probabilistically deformed text",
         COLORS["box"], COLORS["ink"], None),
        (10.05, "Text localization & cropping", "isolate text bounding boxes from context",
         COLORS["blue_bg"], COLORS["blue"], None),
        (8.65, "Isolated text crop", "hallucinated glyphs, deformed kerning",
         COLORS["box"], COLORS["ink"], None),
        (7.25, "Frozen ViT encoder (DINOv2)", "self-supervised visual features",
         COLORS["teal_bg"], COLORS["teal"], None),
        (5.85, "Metric projection head  $f_\\theta$", "triplet-trained font-style embedding",
         COLORS["blue_bg"], COLORS["blue"], None),
    ]
    for cy, title, sub, fc, ec, tc in steps:
        draw_box(ax, 5, cy, W, H, title, sub, fc=fc, ec=ec, tc=tc)
    for cy_from, cy_to in [(10.975, 10.525), (9.575, 9.125), (8.175, 7.725),
                           (6.775, 6.325), (5.375, 4.93)]:
        draw_arrow(ax, (5, cy_from), (5, cy_to), lw=1.5)

    # Decision diamond
    dcx, dcy, dw, dh = 5, 4.05, 3.9, 1.75
    ax.add_patch(mpatches.Polygon(
        [(dcx - dw / 2, dcy), (dcx, dcy + dh / 2), (dcx + dw / 2, dcy), (dcx, dcy - dh / 2)],
        fc=COLORS["orange_bg"], ec=COLORS["orange"], lw=1.5, zorder=3))
    ax.text(dcx, dcy, "Open-set decision\n$d(z,\\, \\mathrm{prototypes})$",
            fontsize=9.5, weight="bold", ha="center", va="center", zorder=4)

    # Branches
    tip_y = dcy - dh / 2
    elbow_y = 2.72
    for bx in (2.5, 7.5):
        ax.plot([5, 5], [tip_y, elbow_y], color=COLORS["ink"], lw=1.4, zorder=1)
        ax.plot([5, bx], [elbow_y, elbow_y], color=COLORS["ink"], lw=1.4, zorder=1)
        draw_arrow(ax, (bx, elbow_y), (bx, 2.28), lw=1.4)
    ax.text(3.55, 2.80, r"$d > \theta$", fontsize=9.5, weight="bold",
            ha="center", va="bottom", color=COLORS["rose"])
    ax.text(6.45, 2.80, r"$d \leq \theta$", fontsize=9.5, weight="bold",
            ha="center", va="bottom", color=COLORS["teal"])

    draw_box(ax, 2.5, 1.8, 4.0, H, "Rejected as unknown",
             "out-of-palette / hallucinated style",
             fc=COLORS["rose_bg"], ec=COLORS["rose"], tc=COLORS["rose"])
    draw_box(ax, 7.5, 1.8, 4.0, H, "Top-K font shortlist",
             "ranked in-palette Google Fonts",
             fc=COLORS["teal_bg"], ec=COLORS["teal"], tc=COLORS["teal"])

    ax.text(5, 12.15, "End-to-end open-set font identification pipeline",
            fontsize=13, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "system_pipeline")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
