"""Figure 10 (Ch4 §4.6) — Iterative-incremental development model.
Four increments, each running the same Analyze -> Design -> Build -> Evaluate
cycle and adding a working slice to a cumulative system.
Pure matplotlib: no Graphviz binary required."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, draw_box, draw_arrow, COLORS


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(11.0, 7.2))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10.4)
    ax.axis("off")

    increments = [
        (2.6, "Increment 1", "Synthetic data pipeline", "labeled degraded crops"),
        (6.4, "Increment 2", "Metric embedding", "frozen encoder + head $f_\\theta$"),
        (10.2, "Increment 3", "Open-set + evaluation", "Top-K, rejection, metrics"),
        (14.0, "Increment 4", "Web application", "FastAPI + React demo"),
    ]
    phases = [
        (7.55, "Analyze", COLORS["blue_bg"], COLORS["blue"]),
        (6.85, "Design", COLORS["blue_bg"], COLORS["blue"]),
        (6.15, "Build", COLORS["teal_bg"], COLORS["teal"]),
        (5.45, "Evaluate", COLORS["orange_bg"], COLORS["orange"]),
    ]

    for cx, name, what, deliver in increments:
        # header
        draw_box(ax, cx, 9.0, 3.25, 0.9, name, what, fc=COLORS["ink"],
                 ec=COLORS["ink"], tc="white", fs=10.5, sub_fs=8.2)
        ax.texts[-2].set_color("white")  # title white on dark header
        ax.texts[-1].set_color("#CBD5E1")  # subtitle light on dark header
        # phase cells
        for py, plabel, fc, ec in phases:
            draw_box(ax, cx, py, 2.95, 0.6, plabel, None, fc=fc, ec=ec, tc=ec, fs=9.5)
        for a, b in [(7.25, 7.15), (6.55, 6.45), (5.85, 5.75)]:
            draw_arrow(ax, (cx, a), (cx, b), lw=1.2)
        # refine loop (evaluate -> analyze)
        ax.annotate("", xy=(cx - 1.62, 7.55), xytext=(cx - 1.62, 5.45), zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color=COLORS["muted"], lw=1.1,
                                    mutation_scale=12, connectionstyle="arc3,rad=-0.45",
                                    linestyle=(0, (3, 2))))
        ax.text(cx - 2.05, 6.5, "refine", rotation=90, ha="center", va="center",
                fontsize=7, color=COLORS["muted"], style="italic")
        # deliverable
        draw_arrow(ax, (cx, 5.15), (cx, 4.55), lw=1.3)
        draw_box(ax, cx, 4.1, 3.25, 0.85, "Deliverable", deliver,
                 fc=COLORS["box"], ec=COLORS["muted"], fs=9, sub_fs=8)

    # increment-to-increment progression (builds on previous)
    for cx in (2.6, 6.4, 10.2):
        draw_arrow(ax, (cx + 1.63, 9.0), (cx + 3.8 - 1.63, 9.0), lw=1.5, color=COLORS["teal"])

    # cumulative system band
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.9, 2.35), 14.2, 0.95, boxstyle="round,pad=0.02",
        fc=COLORS["teal_bg"], ec=COLORS["teal"], lw=1.2, zorder=1))
    ax.text(8.0, 2.83, "Cumulative working system  (each increment integrates into the last)",
            ha="center", va="center", fontsize=9.5, weight="bold", color=COLORS["teal"], zorder=4)
    for cx in (2.6, 6.4, 10.2, 14.0):
        draw_arrow(ax, (cx, 3.68), (cx, 3.34), lw=1.2, color=COLORS["teal"])

    ax.text(8.0, 10.15,
            "Iterative-incremental development model",
            fontsize=12.5, weight="bold", ha="center", color=COLORS["ink"])
    ax.text(8.0, 1.75,
            "Each increment runs the full Analyze - Design - Build - Evaluate cycle; evaluation feeds the next iteration.",
            fontsize=8.5, ha="center", color=COLORS["muted"], style="italic")

    save_figure(fig, "sdlc_model")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
