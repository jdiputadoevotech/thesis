"""Figure 8 (Ch4) — Conceptual framework: IPO view of the font-identification
system. Input column holds the designer, the GenAI image, and the web-app UI
(the system boundary); the Process column is the backend recognition pipeline,
the off-the-shelf localizer followed by the per-crop model stages; the Output
column holds the verified shortlist / unknown verdict. An enclosed training band
(render -> degrade -> triplet + LoRA-teacher distillation) ends in the trained
model (weights f_theta + threshold tau) the engine loads at startup.
Contrast: faint bands < dimmed support boxes < full-colour element boxes.
Line convention (drawn as an in-figure legend):
  solid arrow  = runtime flow, runs for every uploaded image
  dashed arrow = offline flow, run before deployment (incl. the startup load)
Pure matplotlib: no Graphviz binary required."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, draw_box, draw_arrow, COLORS


def _dashed_arrow(ax, p_from, p_to, color, lw=1.3):
    ax.annotate("", xy=p_to, xytext=p_from, zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=13, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3))))


# Three contrast tiers: faint bands < dimmed support boxes < full element boxes.
DIM = dict(fc="#F2F4F7", ec="#C3CDD9", tc=COLORS["muted"], lw=1.0)  # support
BAND_FC = "#FCFDFE"        # lowest opacity, like the system-architecture bands
CONTAINER_FC = "#FBFCFD"


def _band(ax, x0, y0, x1, y1, label, dashed=False, fc=BAND_FC, label_x=None):
    ls = (0, (5, 3)) if dashed else "solid"
    ax.add_patch(mpatches.Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc,
                                    ec="#CBD5E1", lw=1.1, linestyle=ls,
                                    zorder=0))
    ax.text(label_x if label_x else x0 + 0.3, y1 - 0.4, label, ha="left",
            va="center", fontsize=10.5, weight="bold", color=COLORS["muted"],
            zorder=4)


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(11.4, 10.4))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 14.8)
    ax.axis("off")

    # ---- Enclosed bands ----
    _band(ax, 0.35, 4.2, 4.55, 13.35, "INPUT", label_x=0.75)
    _band(ax, 4.85, 3.0, 11.15, 13.35, "PROCESS")
    _band(ax, 11.45, 4.2, 15.65, 13.35, "OUTPUT")
    _band(ax, 0.35, 0.4, 15.65, 2.7,
          "OFFLINE TRAINING  ·  researchers, before deployment",
          dashed=True, fc="#FBFBF7")

    # ---- INPUT: designer -> image -> web-app UI (system boundary) ----
    draw_box(ax, 2.45, 11.95, 3.4, 0.95, "Graphic designer",
             "needs the font used in an image", sub_fs=8, **DIM)
    draw_box(ax, 2.45, 10.2, 3.4, 0.95, "GenAI image",
             "deformed text · multiple regions", sub_fs=8, **DIM)
    draw_box(ax, 2.45, 8.45, 3.4, 1.0, "Web app UI (frontend)",
             "upload image · display results", fs=9.5, sub_fs=8, **DIM)
    draw_arrow(ax, (2.45, 11.475), (2.45, 10.675), lw=1.5)
    draw_arrow(ax, (2.45, 9.725), (2.45, 8.95), lw=1.5)
    ax.text(2.62, 9.34, "upload", ha="left", va="center", fontsize=7.5,
            color=COLORS["muted"], style="italic", zorder=4)
    draw_arrow(ax, (4.15, 8.7), (5.66, 11.0), lw=1.5)    # UI -> localizer

    # ---- Legend (two line kinds only) ----
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.7, 4.55), 3.55, 2.05, boxstyle="round,pad=0.02", fc="white",
        ec=COLORS["muted"], lw=0.9, zorder=3))
    ax.text(0.95, 6.28, "Legend", ha="left", va="center", fontsize=8.5,
            weight="bold", color=COLORS["ink"], zorder=4)
    ax.annotate("", xy=(1.62, 5.7), xytext=(1.0, 5.7), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=COLORS["ink"], lw=1.4,
                                mutation_scale=14, shrinkA=0, shrinkB=0))
    ax.text(1.78, 5.7, "solid: runtime flow,\nruns per uploaded image",
            ha="left", va="center", fontsize=7.2, color=COLORS["ink"], zorder=4)
    ax.annotate("", xy=(1.62, 4.95), xytext=(1.0, 4.95), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=COLORS["muted"], lw=1.3,
                                mutation_scale=14, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3))))
    ax.text(1.78, 4.95, "dashed: offline flow, before\ndeployment (incl. startup load)",
            ha="left", va="center", fontsize=7.2, color=COLORS["ink"], zorder=4)

    # ---- PROCESS: localizer, then the model stages (no nested containers) ----
    draw_box(ax, 8.0, 11.5, 4.6, 0.95, "Text localization",
             "off-the-shelf · crops each text region", sub_fs=8, **DIM)
    draw_arrow(ax, (8.0, 11.025), (8.0, 10.03), lw=1.5)
    ax.text(8.25, 10.55, "per crop", ha="left", va="center", fontsize=7.5,
            color=COLORS["muted"], style="italic", zorder=4)

    # Preprocessing = support (dim); the three model stages = element (full).
    draw_box(ax, 8.0, 9.6, 4.2, 0.82, "Preprocessing", "224² · normalize",
             fs=9.5, sub_fs=7.5, **DIM)
    for cy, t, s, fc, ec in [
        (8.2, "Frozen ViT (DINOv2)", "self-supervised patch features",
         COLORS["teal_bg"], COLORS["teal"]),
        (6.8, "Metric head  $f_\\theta$  (student)", "font-style embedding",
         COLORS["blue_bg"], COLORS["blue"]),
        (5.4, "Open-set decision + Top-K", "reject unknown · calibrated rank",
         COLORS["orange_bg"], COLORS["orange"]),
    ]:
        draw_box(ax, 8.0, cy, 4.2, 0.82, t, s, fc=fc, ec=ec, tc=ec,
                 fs=9.5, sub_fs=7.5, lw=1.8)
    for y_from, y_to in [(9.19, 8.61), (7.79, 7.21), (6.39, 5.81)]:
        draw_arrow(ax, (8.0, y_from), (8.0, y_to), lw=1.4)

    # ---- OUTPUT: shortlist -> re-render check -> reuse, or unknown ----
    draw_box(ax, 13.55, 11.9, 3.7, 1.0, "Top-K Google Fonts",
             "conformal shortlist per crop", fc=COLORS["teal_bg"],
             ec=COLORS["teal"], tc=COLORS["teal"], lw=1.8)
    draw_box(ax, 13.55, 10.0, 3.7, 1.0, "Re-render check",
             "structural distance vs the crop", fc=COLORS["blue_bg"],
             ec=COLORS["blue"], tc=COLORS["blue"], sub_fs=7.8, lw=1.8)
    draw_box(ax, 13.55, 8.1, 3.7, 1.0, "Free template reuse",
             "rebuild with the matched open font", sub_fs=7.8, **DIM)
    draw_box(ax, 13.55, 5.9, 3.7, 1.0, "Unknown verdict",
             "out-of-palette · rejected", fc=COLORS["rose_bg"],
             ec=COLORS["rose"], tc=COLORS["rose"], lw=1.8)

    # decision -> Top-K (accepted, orthogonal riser) and -> Unknown (rejected)
    ax.plot([10.1, 11.3, 11.3], [5.4, 5.4, 11.9], color=COLORS["teal"],
            lw=1.4, zorder=2)
    draw_arrow(ax, (11.3, 11.9), (11.68, 11.9), lw=1.4, color=COLORS["teal"])
    ax.text(11.15, 8.6, "accepted", ha="right", va="center", fontsize=7.5,
            color=COLORS["teal"], style="italic", rotation=90, zorder=4)
    draw_arrow(ax, (10.1, 5.5), (11.68, 5.95), lw=1.4, color=COLORS["rose"])
    ax.text(10.95, 5.95, "rejected", ha="right", va="center", fontsize=7.5,
            color=COLORS["rose"], style="italic", zorder=4)
    draw_arrow(ax, (13.55, 11.4), (13.55, 10.5), lw=1.4)
    draw_arrow(ax, (13.55, 9.5), (13.55, 8.6), lw=1.4)

    # ---- OFFLINE TRAINING band ----
    # Pipeline steps = support (dim); the trained-model artifact = element (full).
    for cx, t, s in [
        (2.0, "Google Fonts", "50–100 font palette"),
        (4.9, "Synthetic render", "pristine word crops"),
        (7.8, "Degradation  $D$", "warp · blur · kern jitter"),
        (10.7, "Metric-head training", "triplet + LoRA-teacher distill"),
    ]:
        draw_box(ax, cx, 1.35, 2.6, 0.92, t, s, fs=8.6, sub_fs=7.0, **DIM)
    draw_box(ax, 13.6, 1.35, 2.6, 0.92, "Trained model",
             "weights $f_\\theta$ · threshold $\\tau$", fc=COLORS["teal_bg"],
             ec=COLORS["teal"], tc=COLORS["teal"], fs=8.6, sub_fs=7.0, lw=1.8)
    for cx in (3.3, 6.2, 9.1, 12.0):
        _dashed_arrow(ax, (cx, 1.35), (cx + 0.3, 1.35), COLORS["ink"], lw=1.3)

    # trained model -> model stages (startup load)
    _dashed_arrow(ax, (13.6, 1.81), (9.85, 5.0), COLORS["teal"], lw=1.5)
    ax.text(12.1, 3.25, "loads weights $f_\\theta$, $\\tau$ at startup",
            ha="left", va="center", fontsize=7.5, color=COLORS["teal"],
            style="italic", zorder=4)

    ax.text(8.0, 14.35,
            "Conceptual framework of the proposed font-identification system",
            fontsize=12.5, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "conceptual_framework")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
