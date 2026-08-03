"""Figure 9 (Ch4 §4.5.2) — System architecture of the font-identification web app.
Layered view: user, React client, FastAPI backend, PyTorch inference service,
and the model/asset resources, plus the offline training that produces weights.
Pure matplotlib: no Graphviz binary required."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, draw_box, draw_arrow, COLORS


def _band(ax, y0, y1, label):
    ax.add_patch(mpatches.Rectangle((0.3, y0), 15.4, y1 - y0, fc="#FBFCFD",
                                     ec=COLORS["grid"], lw=1.0, zorder=0))
    ax.text(0.6, (y0 + y1) / 2, label, ha="left", va="center", rotation=90,
            fontsize=9.5, weight="bold", color=COLORS["muted"], zorder=4)


def _dashed_line(ax, xs, ys, color):
    ax.plot(xs, ys, color=color, lw=1.2, linestyle=(0, (4, 3)), zorder=1)


def _dashed_arrow(ax, p_from, p_to, color):
    ax.annotate("", xy=p_to, xytext=p_from, zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2,
                                mutation_scale=13, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3))))


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(10.6, 9.9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 14.6)
    ax.axis("off")

    _band(ax, 12.95, 14.05, "USER")
    _band(ax, 11.05, 12.55, "CLIENT")
    _band(ax, 9.0, 10.6, "API")
    _band(ax, 2.7, 8.55, "INFERENCE")
    _band(ax, 0.35, 2.45, "RESOURCES")

    # USER
    draw_box(ax, 8.0, 13.5, 4.6, 0.85, "Graphic designer",
             "uploads a GenAI image", fc=COLORS["box"], ec=COLORS["ink"],
             fs=11, sub_fs=8.8)

    # CLIENT
    draw_box(ax, 8.0, 11.8, 7.4, 1.2, "React frontend (browser)",
             "image upload · Top-K results gallery with font previews",
             fc=COLORS["blue_bg"], ec=COLORS["blue"], tc=COLORS["blue"],
             fs=11.5, sub_fs=9)

    # API
    draw_box(ax, 8.0, 9.8, 7.4, 1.3, "FastAPI backend  (Docker)",
             "REST endpoint /predict · orchestrates inference\n"
             "loads model weights once at startup",
             fc=COLORS["blue_bg"], ec=COLORS["blue"], tc=COLORS["blue"],
             fs=11.5, sub_fs=9)

    # INFERENCE container
    ax.add_patch(mpatches.FancyBboxPatch(
        (4.4, 2.9), 7.2, 5.35, boxstyle="round,pad=0.02",
        fc="#F5FAF9", ec=COLORS["teal"], lw=1.4, zorder=1))
    ax.text(8.0, 7.95, "PyTorch inference service", ha="center", va="center",
            fontsize=11, weight="bold", color=COLORS["teal"], zorder=4)
    steps = [
        (7.3, "Text localization", "off-the-shelf · crop each region", COLORS["box"], COLORS["muted"]),
        (6.35, "Preprocessing", "224² · normalize", COLORS["box"], COLORS["ink"]),
        (5.4, "Frozen DINOv2 encoder", "self-supervised patch features", COLORS["teal_bg"], COLORS["teal"]),
        (4.45, "Metric head  $f_\\theta$", "font-style embedding", COLORS["blue_bg"], COLORS["blue"]),
        (3.5, "Open-set decision + Top-K", "reject unknown · rank palette", COLORS["orange_bg"], COLORS["orange"]),
    ]
    for cy, t, s, fc, ec in steps:
        draw_box(ax, 8.0, cy, 5.9, 0.74, t, s, fc=fc, ec=ec, tc=ec,
                 fs=10.5, sub_fs=8.2)
    for a, b in [(6.93, 6.72), (5.98, 5.77), (5.03, 4.82), (4.08, 3.87)]:
        draw_arrow(ax, (8.0, a), (8.0, b), lw=1.3)

    # RESOURCES
    draw_box(ax, 3.5, 1.4, 4.4, 1.1, "Model store",
             "HuggingFace Hub:\nDINOv2 + baseline weights", fc=COLORS["box"],
             ec=COLORS["ink"], fs=10.5, sub_fs=8.3)
    draw_box(ax, 8.0, 1.4, 3.9, 1.1, "Trained weights",
             "metric head $f_\\theta$\n(trained offline)", fc=COLORS["teal_bg"],
             ec=COLORS["teal"], tc=COLORS["teal"], fs=10.5, sub_fs=8.3)
    draw_box(ax, 13.2, 1.4, 4.7, 1.1, "Font assets",
             "Google Fonts:\npalette + preview rendering", fc=COLORS["box"],
             ec=COLORS["ink"], fs=10.5, sub_fs=8.3)

    # ---- main request path (straight down the spine) ----
    draw_arrow(ax, (8.0, 13.075), (8.0, 12.4), lw=1.6)      # user -> client
    ax.text(7.75, 12.74, "image", ha="right", va="center", fontsize=8.5,
            color=COLORS["muted"], style="italic")
    draw_arrow(ax, (7.3, 11.2), (7.3, 10.45), lw=1.6)       # client -> api
    ax.text(7.05, 10.82, "POST", ha="right", va="center", fontsize=8.5,
            color=COLORS["muted"], style="italic")
    draw_arrow(ax, (8.0, 9.15), (8.0, 8.25), lw=1.6)        # api -> inference

    # ---- return path: right, up, left back into the client (elbows only) ----
    ax.plot([10.95, 13.6, 13.6], [3.5, 3.5, 11.8], color=COLORS["teal"],
            lw=1.4, zorder=1)
    draw_arrow(ax, (13.6, 11.8), (11.7, 11.8), lw=1.4, color=COLORS["teal"])
    ax.text(13.8, 7.0, "Top-K fonts / unknown\n+ rendered previews", ha="left",
            va="center", fontsize=8.5, color=COLORS["teal"], style="italic")

    # ---- resource feeds (dashed, elbows only) ----
    _dashed_line(ax, [3.5, 3.5], [1.95, 5.4], COLORS["muted"])
    _dashed_arrow(ax, (3.5, 5.4), (5.05, 5.4), COLORS["muted"])    # HF -> encoder
    _dashed_arrow(ax, (8.0, 1.95), (8.0, 2.9), COLORS["teal"])     # head weights
    _dashed_line(ax, [13.2, 13.2, 10.3], [1.95, 2.65, 2.65], COLORS["muted"])
    _dashed_arrow(ax, (10.3, 2.65), (10.3, 3.13), COLORS["muted"]) # fonts -> Top-K
    ax.text(8.0, 14.35,
            "System architecture of the font-identification web application",
            fontsize=13, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "system_architecture")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
