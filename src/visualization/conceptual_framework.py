"""Figure 8 (Ch4) — Conceptual framework: IPO view of the font-identification
system and the web app built on top of it. Shows how user, frontend, backend,
ML inference engine, and the offline synthetic-training subsystem interact.
Pure matplotlib: no Graphviz binary required."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, draw_box, draw_arrow, COLORS


def _dashed_arrow(ax, p_from, p_to, color):
    ax.annotate("", xy=p_to, xytext=p_from, zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                                mutation_scale=14, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3))))


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(10.6, 7.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11.6)
    ax.axis("off")

    # ---- Band headers (INPUT / PROCESS / OUTPUT) ----
    for x, label in [(2.5, "INPUT"), (8.0, "PROCESS"), (13.6, "OUTPUT")]:
        ax.text(x, 10.35, label, ha="center", va="center", fontsize=11,
                weight="bold", color=COLORS["muted"], zorder=4)
    for x in (5.15, 10.9):
        ax.plot([x, x], [1.9, 10.15], color=COLORS["grid"], lw=1.0,
                linestyle=(0, (2, 3)), zorder=0)

    # ---- INPUT column ----
    draw_box(ax, 2.5, 9.1, 3.4, 0.95, "Graphic designer",
             "needs a font from an image", fc=COLORS["box"], ec=COLORS["ink"])
    draw_box(ax, 2.5, 7.2, 3.4, 0.95, "GenAI image",
             "hallucinated / deformed text", fc=COLORS["orange_bg"],
             ec=COLORS["orange"], tc=COLORS["orange"])
    draw_arrow(ax, (2.5, 8.625), (2.5, 7.675), lw=1.4)

    # ---- PROCESS column: web + backend + ML engine ----
    draw_box(ax, 8.0, 9.3, 4.6, 0.9, "Web app (frontend)",
             "upload image · view ranked results", fc=COLORS["blue_bg"],
             ec=COLORS["blue"], tc=COLORS["blue"])
    draw_box(ax, 8.0, 7.85, 4.6, 0.9, "Backend API",
             "request routing · inference server", fc=COLORS["blue_bg"],
             ec=COLORS["blue"], tc=COLORS["blue"])

    # ML inference engine container
    ax.add_patch(mpatches.FancyBboxPatch(
        (5.5, 2.55), 5.0, 4.35, boxstyle="round,pad=0.02",
        fc="#F8FAFC", ec=COLORS["teal"], lw=1.3, zorder=1))
    ax.text(8.0, 6.62, "ML inference engine", ha="center", va="center",
            fontsize=9.5, weight="bold", color=COLORS["teal"], zorder=4)
    ml_steps = [
        (5.95, "Preprocessing", "crop → 224² → normalize", COLORS["box"], COLORS["ink"], None),
        (4.95, "Frozen ViT — DINOv2", "self-supervised patch features", COLORS["teal_bg"], COLORS["teal"], None),
        (3.95, "Metric head  $f_\\theta$", "font-style embedding", COLORS["blue_bg"], COLORS["blue"], None),
        (2.95, "Open-set decision + Top-K", "reject unknown · rank palette", COLORS["orange_bg"], COLORS["orange"], None),
    ]
    for cy, t, s, fc, ec, tc in ml_steps:
        draw_box(ax, 8.0, cy, 4.2, 0.8, t, s, fc=fc, ec=ec, tc=tc, fs=9.5, sub_fs=8)

    # vertical process arrows
    draw_arrow(ax, (8.0, 8.85), (8.0, 8.30), lw=1.5)   # frontend -> backend
    draw_arrow(ax, (8.0, 7.40), (8.0, 6.35), lw=1.5)   # backend -> preprocess
    for cy_from, cy_to in [(5.55, 5.35), (4.55, 4.35), (3.55, 3.35)]:
        draw_arrow(ax, (8.0, cy_from), (8.0, cy_to), lw=1.4)

    # input image -> frontend
    draw_arrow(ax, (4.2, 7.2), (5.7, 9.05), lw=1.4)

    # ---- OUTPUT column ----
    draw_box(ax, 13.6, 5.4, 3.8, 0.95, "Top-K Google Fonts",
             "ranked in-palette matches", fc=COLORS["teal_bg"],
             ec=COLORS["teal"], tc=COLORS["teal"])
    draw_box(ax, 13.6, 3.7, 3.8, 0.95, "Unknown verdict",
             "out-of-palette / hallucinated", fc=COLORS["rose_bg"],
             ec=COLORS["rose"], tc=COLORS["rose"])
    draw_box(ax, 13.6, 8.4, 3.8, 0.95, "Free template reuse",
             "reconstruct with open font", fc=COLORS["box"], ec=COLORS["ink"])

    # decision -> outputs
    draw_arrow(ax, (10.1, 3.15), (11.7, 5.15), lw=1.4, color=COLORS["teal"])
    draw_arrow(ax, (10.1, 2.85), (11.7, 3.7), lw=1.4, color=COLORS["rose"])
    # shortlist -> template reuse -> back to designer (feedback)
    draw_arrow(ax, (13.6, 5.875), (13.6, 7.925), lw=1.4)
    _dashed_arrow(ax, (13.6, 8.875), (4.0, 9.35), COLORS["muted"])
    ax.text(8.7, 9.72, "results returned to user", ha="center", va="bottom",
            fontsize=8, color=COLORS["muted"], style="italic")

    # ---- Offline training subsystem (bottom band) ----
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.4, 0.35), 15.2, 1.35, boxstyle="round,pad=0.02",
        fc="#FBFBF7", ec=COLORS["muted"], lw=1.0, linestyle=(0, (3, 2)), zorder=0))
    ax.text(0.75, 1.5, "Offline training (researchers)", ha="left", va="center",
            fontsize=8.5, weight="bold", color=COLORS["muted"], zorder=4)
    train = [
        (2.9, "Google Fonts", "50–100 palette"),
        (6.2, "Synthetic render", "pristine word crops"),
        (9.5, "Degradation  $D$", "warp · blur · kern jitter"),
        (12.8, "Triplet training", "learn $f_\\theta$"),
    ]
    for cx, t, s in train:
        draw_box(ax, cx, 0.92, 2.9, 0.72, t, s, fc=COLORS["box"],
                 ec=COLORS["ink"], fs=9, sub_fs=7.5)
    for cx in (4.35, 7.65, 10.95):
        draw_arrow(ax, (cx, 0.92), (cx + 0.9, 0.92), lw=1.3)
    # trained weights feed the frozen encoder + head (dashed up)
    _dashed_arrow(ax, (12.8, 1.28), (9.2, 3.55), COLORS["teal"])
    ax.text(13.35, 2.05, "trained weights", ha="left", va="center",
            fontsize=7.5, color=COLORS["teal"], style="italic")

    ax.text(8.0, 11.25, "Conceptual framework of the proposed font-identification system",
            fontsize=12.5, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "conceptual_framework")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
