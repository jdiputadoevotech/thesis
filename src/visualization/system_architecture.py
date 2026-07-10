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
            fontsize=8.5, weight="bold", color=COLORS["muted"], zorder=4)


def _dashed_arrow(ax, p_from, p_to, color):
    ax.annotate("", xy=p_to, xytext=p_from, zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2,
                                mutation_scale=13, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3))))


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(10.6, 9.2))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 13.2)
    ax.axis("off")

    _band(ax, 11.7, 12.8, "USER")
    _band(ax, 9.9, 11.4, "CLIENT")
    _band(ax, 8.0, 9.5, "API")
    _band(ax, 2.55, 7.55, "INFERENCE")
    _band(ax, 0.4, 2.4, "RESOURCES")

    # USER
    draw_box(ax, 8.0, 12.25, 4.0, 0.8, "Graphic designer",
             "uploads a GenAI image", fc=COLORS["box"], ec=COLORS["ink"], fs=10, sub_fs=8)

    # CLIENT
    draw_box(ax, 8.0, 10.65, 6.6, 1.05, "React frontend (browser)",
             "image upload · Top-K results gallery with font previews",
             fc=COLORS["blue_bg"], ec=COLORS["blue"], tc=COLORS["blue"], fs=10.5, sub_fs=8.5)

    # API
    draw_box(ax, 8.0, 8.75, 6.6, 1.05, "FastAPI backend  (Docker)",
             "REST endpoint /predict · orchestrates inference · loads weights at startup",
             fc=COLORS["blue_bg"], ec=COLORS["blue"], tc=COLORS["blue"], fs=10.5, sub_fs=8.5)

    # INFERENCE container
    ax.add_patch(mpatches.FancyBboxPatch(
        (4.5, 2.72), 7.0, 4.55, boxstyle="round,pad=0.02",
        fc="#F5FAF9", ec=COLORS["teal"], lw=1.4, zorder=1))
    ax.text(8.0, 7.0, "PyTorch inference service", ha="center", va="center",
            fontsize=10, weight="bold", color=COLORS["teal"], zorder=4)
    steps = [
        (6.45, "Text localization", "off-the-shelf · crop each region", COLORS["box"], COLORS["muted"]),
        (5.60, "Preprocessing", "224² · normalize", COLORS["box"], COLORS["ink"]),
        (4.75, "Frozen DINOv2 encoder", "self-supervised patch features", COLORS["teal_bg"], COLORS["teal"]),
        (3.90, "Metric head  $f_\\theta$", "font-style embedding", COLORS["blue_bg"], COLORS["blue"]),
        (3.15, "Open-set decision + Top-K", "reject unknown · rank palette", COLORS["orange_bg"], COLORS["orange"]),
    ]
    for cy, t, s, fc, ec in steps:
        draw_box(ax, 8.0, cy, 5.6, 0.62, t, s, fc=fc, ec=ec, tc=ec, fs=9.5, sub_fs=7.5)
    for a, b in [(6.14, 5.91), (5.29, 5.06), (4.44, 4.21), (3.59, 3.46)]:
        draw_arrow(ax, (8.0, a), (8.0, b), lw=1.3)

    # RESOURCES
    draw_box(ax, 3.4, 1.45, 4.2, 1.0, "Model store",
             "HuggingFace Hub: DINOv2 + baseline weights", fc=COLORS["box"],
             ec=COLORS["ink"], fs=9.5, sub_fs=7.8)
    draw_box(ax, 8.0, 1.45, 3.8, 1.0, "Trained weights",
             "metric head $f_\\theta$ (offline)", fc=COLORS["teal_bg"],
             ec=COLORS["teal"], tc=COLORS["teal"], fs=9.5, sub_fs=7.8)
    draw_box(ax, 12.6, 1.45, 4.2, 1.0, "Font assets",
             "Google Fonts: palette + preview rendering", fc=COLORS["box"],
             ec=COLORS["ink"], fs=9.5, sub_fs=7.8)

    # ---- main request path (down) ----
    draw_arrow(ax, (8.0, 11.85), (8.0, 11.20), lw=1.6)          # user -> client
    ax.text(7.75, 11.52, "image", ha="right", va="center", fontsize=7.5,
            color=COLORS["muted"], style="italic")
    draw_arrow(ax, (7.3, 10.12), (7.3, 9.30), lw=1.6)           # client -> api (request)
    ax.text(7.05, 9.7, "POST", ha="right", va="center", fontsize=7.5,
            color=COLORS["muted"], style="italic")
    draw_arrow(ax, (8.0, 8.22), (8.0, 7.32), lw=1.6)            # api -> inference

    # ---- return path (up, right side) ----
    ax.plot([10.8, 12.6, 12.6], [3.15, 3.15, 9.9], color=COLORS["teal"], lw=1.4, zorder=1)
    draw_arrow(ax, (12.6, 9.9), (9.3, 10.12), lw=1.4, color=COLORS["teal"])
    ax.text(12.8, 6.6, "Top-K fonts / unknown\n+ rendered previews", ha="left",
            va="center", fontsize=7.5, color=COLORS["teal"], style="italic")

    # ---- resource feeds (dashed up into inference) ----
    _dashed_arrow(ax, (3.4, 1.90), (5.5, 4.55), COLORS["muted"])   # HF backbone -> encoder
    _dashed_arrow(ax, (8.0, 1.90), (8.0, 2.78), COLORS["teal"])    # trained head -> engine
    _dashed_arrow(ax, (12.6, 1.90), (10.7, 3.10), COLORS["muted"]) # fonts -> re-render/preview

    ax.text(8.0, 13.0, "System architecture of the font-identification web application",
            fontsize=12.5, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "system_architecture")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
