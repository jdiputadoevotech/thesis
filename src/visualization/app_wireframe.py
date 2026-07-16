"""SRS wireframe — single-page web app, three stacked zones: Input -> Processing -> Results.
Low-fidelity UI mockup for chapters/04-methodology/srs/SRS.md.
Pure matplotlib boxes (same house style as the other thesis figures)."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, COLORS


def rrect(ax, x, y, w, h, fc, ec, lw=1.2, dashed=False, z=2, pad=0.02):
    ls = (0, (5, 3)) if dashed else "solid"
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad={pad}", fc=fc, ec=ec, lw=lw,
        linestyle=ls, zorder=z))


def rect(ax, x, y, w, h, fc, ec, lw=1.0, z=2, dashed=False):
    ls = (0, (4, 3)) if dashed else "solid"
    ax.add_patch(mpatches.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw,
                                    linestyle=ls, zorder=z))


def band(ax, y0, y1, label):
    ax.text(0.55, (y0 + y1) / 2, label, ha="center", va="center", rotation=90,
            fontsize=8.5, weight="bold", color=COLORS["muted"], zorder=5)


def score_bar(ax, x, y, w, frac, color):
    rect(ax, x, y, w, 0.16, "#EDF1F6", COLORS["grid"], lw=0.6, z=3)
    rect(ax, x, y, w * frac, 0.16, color, color, lw=0, z=4)


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(9.4, 13.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 26)
    ax.axis("off")

    ink, muted, blue, teal, orange, rose = (COLORS["ink"], COLORS["muted"],
        COLORS["blue"], COLORS["teal"], COLORS["orange"], COLORS["rose"])

    # ---- browser chrome ----
    rrect(ax, 1.1, 0.6, 14.4, 24.7, "white", muted, lw=1.4, z=1, pad=0.03)
    rect(ax, 1.1, 24.2, 14.4, 1.1, "#F1F5F9", muted, lw=1.0, z=1)
    for i, c in enumerate(["#E76F6F", "#E7C36F", "#7FC98A"]):
        ax.add_patch(mpatches.Circle((1.6 + i * 0.4, 24.75), 0.11, fc=c, ec="none", zorder=3))
    rrect(ax, 3.4, 24.45, 9.5, 0.6, "white", COLORS["grid"], lw=0.9, z=2, pad=0.02)
    ax.text(3.7, 24.75, "localhost:8000  ·  FontID", ha="left", va="center",
            fontsize=8, color=muted, zorder=4)

    # ---- app header ----
    ax.text(8.3, 23.4, "FontID — Typographic-Hallucination Font Matcher",
            ha="center", va="center", fontsize=12.5, weight="bold", color=ink, zorder=4)
    ax.text(8.3, 22.85, "Recover the closest open-source Google Font from AI-generated text",
            ha="center", va="center", fontsize=8.5, color=muted, style="italic", zorder=4)

    # zone bands (left rail)
    band(ax, 17.6, 22.3, "1 · INPUT")
    band(ax, 11.9, 17.2, "2 · PROCESSING")
    band(ax, 1.2, 11.4, "3 · RESULTS")

    # ============ ZONE 1 — INPUT ============
    ax.text(1.7, 22.0, "1  Upload", ha="left", va="center", fontsize=10.5,
            weight="bold", color=blue, zorder=4)
    # dropzone
    rrect(ax, 1.7, 18.9, 13.0, 2.55, COLORS["blue_bg"], blue, lw=1.3, dashed=True, z=2)
    ax.plot(8.2, 20.55, marker="^", markersize=15, color=blue, zorder=4)
    ax.text(8.2, 19.75, "Drag & drop a GenAI screenshot / poster   —   or click to browse",
            ha="center", va="center", fontsize=9.5, color=ink, zorder=4)
    ax.text(8.2, 19.32, "PNG · JPG · WEBP   ·   up to 10 MB",
            ha="center", va="center", fontsize=7.8, color=muted, zorder=4)
    # sample row + primary button
    ax.text(1.7, 18.35, "Try a sample:", ha="left", va="center", fontsize=8, color=muted, zorder=4)
    for i in range(3):
        rect(ax, 3.9 + i * 1.0, 17.95, 0.8, 0.72, "#E9EEF4", muted, lw=0.8, z=3)
    rrect(ax, 11.3, 17.85, 3.4, 0.9, teal, teal, lw=1.2, z=3)
    ax.text(13.0, 18.3, "Identify Fonts  →", ha="center", va="center",
            fontsize=10, weight="bold", color="white", zorder=4)

    # ============ ZONE 2 — PROCESSING ============
    ax.text(1.7, 16.9, "2  Processing", ha="left", va="center", fontsize=10.5,
            weight="bold", color=orange, zorder=4)
    # image preview with detected regions
    rect(ax, 1.7, 12.2, 6.4, 4.35, "#EEF2F6", muted, lw=1.1, z=2)
    ax.text(4.9, 16.25, "uploaded image", ha="center", va="center",
            fontsize=7.5, color=muted, style="italic", zorder=4)
    rect(ax, 2.5, 14.7, 4.0, 0.85, "none", orange, lw=1.4, dashed=True, z=4)
    ax.text(2.55, 15.75, "region 1", ha="left", va="center", fontsize=7, color=orange, zorder=5)
    rect(ax, 3.0, 12.9, 2.7, 0.7, "none", orange, lw=1.4, dashed=True, z=4)
    ax.text(3.05, 13.75, "region 2", ha="left", va="center", fontsize=7, color=orange, zorder=5)
    # pipeline status checklist
    rrect(ax, 8.6, 12.2, 6.1, 4.35, "#FBFCFD", COLORS["grid"], lw=1.0, z=2)
    ax.text(8.95, 16.15, "Pipeline", ha="left", va="center", fontsize=8.5,
            weight="bold", color=muted, zorder=4)
    steps = [
        ("●", "Text localization  ·  2 regions found", teal, 15.55),
        ("●", "Preprocess  ·  square-pad → 224² → normalize", teal, 15.05),
        ("●", "DINOv2 encoder  ·  extract embedding", orange, 14.55),
        ("○", "Metric head + open-set match  ·  rank palette", muted, 14.05),
    ]
    for mark, label, col, yy in steps:
        ax.text(8.95, yy, mark, ha="left", va="center", fontsize=9, weight="bold",
                color=col, zorder=4)
        ax.text(9.35, yy, label, ha="left", va="center", fontsize=8, color=ink, zorder=4)
    score_bar(ax, 8.95, 12.75, 5.4, 0.62, orange)
    ax.text(8.95, 12.45, "processing… 62%", ha="left", va="center", fontsize=7.5,
            color=muted, zorder=4)

    # ============ ZONE 3 — RESULTS ============
    ax.text(1.7, 11.05, "3  Results — Top-K font shortlist per detected text",
            ha="left", va="center", fontsize=10.5, weight="bold", color=teal, zorder=4)

    def result_card(y0, crop_label, accept, rows):
        h = 4.15
        rrect(ax, 1.7, y0, 13.0, h, "white", COLORS["grid"], lw=1.1, z=2)
        # crop thumbnail
        rect(ax, 2.1, y0 + h - 1.9, 2.7, 1.4, "#EEF2F6", muted, lw=1.0, z=3)
        ax.text(3.45, y0 + h - 1.2, "text crop", ha="center", va="center",
                fontsize=7, color=muted, style="italic", zorder=4)
        ax.text(2.1, y0 + h - 2.25, crop_label, ha="left", va="center",
                fontsize=8.5, weight="bold", color=ink, zorder=4)
        # accept / reject badge
        bc = teal if accept else rose
        btxt = "KNOWN — in palette" if accept else "UNKNOWN — out of palette"
        rrect(ax, 2.1, y0 + 0.35, 2.9, 0.55, COLORS["teal_bg"] if accept else COLORS["rose_bg"],
              bc, lw=1.0, z=3)
        ax.text(3.55, y0 + 0.625, btxt, ha="center", va="center", fontsize=6.8,
                weight="bold", color=bc, zorder=4)
        # Top-K rows
        rx, ry = 5.4, y0 + h - 0.75
        ax.text(rx, ry + 0.35, "Top-3 candidates", ha="left", va="center",
                fontsize=7.5, weight="bold", color=muted, zorder=4)
        for rank, (name, prev, frac) in enumerate(rows, 1):
            col = ink if accept else muted
            ax.text(rx, ry, f"#{rank}", ha="left", va="center", fontsize=8.5,
                    weight="bold", color=col, zorder=4)
            ax.text(rx + 0.55, ry, name, ha="left", va="center", fontsize=8.5,
                    weight="bold", color=col, zorder=4)
            ax.text(rx + 0.55, ry - 0.3, prev, ha="left", va="center", fontsize=7.5,
                    color=muted, style="italic", zorder=4)
            score_bar(ax, rx + 6.7, ry - 0.05, 2.0, frac, teal if accept else muted)
            ax.text(rx + 8.85, ry - 0.02, f"{frac:.2f}", ha="left", va="center",
                    fontsize=7.5, color=col, zorder=4)
            ry -= 1.0

    # accepted example
    result_card(6.55, "Region 1 · “SUMMER SALE”", True, [
        ("Montserrat Bold", "SUMMER SALE", 0.94),
        ("Poppins SemiBold", "SUMMER SALE", 0.89),
        ("Raleway Bold", "SUMMER SALE", 0.85),
    ])
    # rejected example (open-set)
    result_card(1.35, "Region 2 · “get 50% off”", False, [
        ("Pacifico", "get 50% off", 0.41),
        ("Lobster", "get 50% off", 0.38),
        ("Satisfy", "get 50% off", 0.36),
    ])
    ax.text(5.4, 1.7, "max similarity 0.41 < τ  →  rejected as out-of-palette (open-set)",
            ha="left", va="center", fontsize=7, color=rose, style="italic", zorder=4)

    save_figure(fig, "app_wireframe")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
