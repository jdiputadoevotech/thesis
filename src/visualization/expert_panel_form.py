"""Expert-panel rating form — platform-neutral wireframe for the human-proxy
consensus instrument of Ch4 §4.2.3. Two screens: (A) the instructions page shown
once, and (B) the per-crop rating item repeated for each of the [N = 100] real
generative text crops. Layout only: any standard web-form service can host it.
Same house style as app_wireframe.py; pure matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, COLORS


def rrect(ax, x, y, w, h, fc, ec, lw=1.2, dashed=False, z=2, pad=0.02):
    ls = (0, (5, 3)) if dashed else "solid"
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad={pad}", fc=fc, ec=ec, lw=lw,
        linestyle=ls, zorder=z))


def rect(ax, x, y, w, h, fc, ec, lw=1.0, z=2):
    ax.add_patch(mpatches.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw,
                                    zorder=z))


def score_bar(ax, x, y, w, frac, color):
    rect(ax, x, y, w, 0.16, "#EDF1F6", COLORS["grid"], lw=0.6, z=3)
    rect(ax, x, y, w * frac, 0.16, color, color, lw=0, z=4)


def chrome(ax, x0, x1, y1, url):
    """Browser top bar with traffic lights and a URL pill."""
    rect(ax, x0, y1 - 0.9, x1 - x0, 0.9, "#F1F5F9", COLORS["muted"], lw=1.0)
    for i, c in enumerate(["#E76F6F", "#E7C36F", "#7FC98A"]):
        ax.add_patch(mpatches.Circle((x0 + 0.5 + i * 0.4, y1 - 0.45), 0.11,
                                     fc=c, ec="none", zorder=3))
    rrect(ax, x0 + 2.2, y1 - 0.72, x1 - x0 - 3.2, 0.5, "white",
          COLORS["grid"], lw=0.9, z=2)
    ax.text(x0 + 2.5, y1 - 0.47, url, ha="left", va="center", fontsize=8,
            color=COLORS["muted"], zorder=4)


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(13.0, 6.8))
    ax.set_xlim(0, 32)
    ax.set_ylim(4.0, 20.4)
    ax.axis("off")

    ink, muted, blue, teal, rose = (COLORS["ink"], COLORS["muted"],
                                    COLORS["blue"], COLORS["teal"],
                                    COLORS["rose"])

    ax.text(16.0, 19.85, "Expert-panel rating form — platform-neutral layout",
            ha="center", va="center", fontsize=12, weight="bold", color=ink)

    ax.text(0.6, 18.85, "A · Instructions — shown once, before the first item",
            ha="left", va="center", fontsize=9.5, weight="bold", color=muted)
    ax.text(16.6, 18.85, "B · Rating item — repeated for each of the 100 crops",
            ha="left", va="center", fontsize=9.5, weight="bold", color=muted)

    # ================= PANEL A — instructions =================
    rrect(ax, 0.6, 4.6, 14.8, 13.7, "white", muted, lw=1.4, z=1, pad=0.03)
    chrome(ax, 0.6, 15.4, 18.3, "font-rating-exercise  ·  Welcome")

    ax.text(8.0, 16.55, "Expert Panel Rating Exercise", ha="center",
            va="center", fontsize=12, weight="bold", color=ink, zorder=4)
    ax.text(8.0, 16.0, "Ground-truth labels for AI-generated text crops · 100 items",
            ha="center", va="center", fontsize=8.5, color=muted,
            style="italic", zorder=4)

    ax.text(1.4, 15.1, "What you will do", ha="left", va="center",
            fontsize=9.5, weight="bold", color=blue, zorder=4)
    for y, t in [
        (14.45, "You will rate 100 short text crops taken from AI-generated images."),
        (13.8, "For each crop, pick the closest font from the Google Fonts palette,"),
        (13.15, "or mark it “Unknown / hallucinated” if no palette font matches."),
    ]:
        ax.text(1.7, y, t, ha="left", va="center", fontsize=8.5, color=ink,
                zorder=4)

    ax.text(1.4, 12.25, "Ground rules", ha="left", va="center", fontsize=9.5,
            weight="bold", color=blue, zorder=4)
    for y, t in [
        (11.6, "Work independently — please do not discuss items with the other raters."),
        (10.95, "Self-paced — pause and resume at any time; there is no time limit."),
        (10.3, "You will never see the model's predictions or another rater's answers."),
    ]:
        ax.text(1.7, y, t, ha="left", va="center", fontsize=8.5, color=ink,
                zorder=4)

    rrect(ax, 1.4, 7.9, 13.2, 1.7, COLORS["blue_bg"], blue, lw=1.1, z=2)
    ax.text(1.75, 9.15, "Palette reference sheet", ha="left", va="center",
            fontsize=9, weight="bold", color=blue, zorder=4)
    ax.text(1.75, 8.7, "Every palette font rendered as a labeled specimen sheet.",
            ha="left", va="center", fontsize=8, color=ink, zorder=4)
    ax.text(1.75, 8.3, "Keep it open beside the form while you rate.",
            ha="left", va="center", fontsize=8, color=ink, zorder=4)

    rrect(ax, 5.1, 6.1, 5.8, 0.9, teal, teal, lw=1.2, z=3)
    ax.text(8.0, 6.55, "Begin — Item 1 of 100  →", ha="center",
            va="center", fontsize=9.5, weight="bold", color="white", zorder=4)
    ax.text(8.0, 5.4, "Starting the form records your agreement to take part as an expert rater.",
            ha="center", va="center", fontsize=7.3, color=muted,
            style="italic", zorder=4)

    # ================= PANEL B — rating item =================
    rrect(ax, 16.6, 4.6, 14.8, 13.7, "white", muted, lw=1.4, z=1, pad=0.03)
    chrome(ax, 16.6, 31.4, 18.3, "font-rating-exercise  ·  Item 12 of 100")

    ax.text(17.4, 16.75, "Item 12 of 100", ha="left", va="center", fontsize=9,
            weight="bold", color=ink, zorder=4)
    score_bar(ax, 21.4, 16.65, 9.2, 0.12, teal)

    # the crop under judgment
    rect(ax, 17.4, 12.5, 6.0, 3.6, "#EEF2F6", muted, lw=1.1, z=2)
    ax.text(17.7, 15.7, "AI-generated text crop", ha="left", va="center",
            fontsize=7.5, color=muted, style="italic", zorder=4)
    ax.text(20.4, 14.1, "OPEM  DAILY", ha="center", va="center", fontsize=14,
            weight="bold", color=ink, rotation=1.5, zorder=4)

    # palette reference sheet, kept beside the crop
    rrect(ax, 24.0, 12.5, 6.6, 3.6, "#FBFCFD", COLORS["grid"], lw=1.0, z=2)
    ax.text(24.35, 15.75, "Palette reference sheet (excerpt)", ha="left",
            va="center", fontsize=8, weight="bold", color=muted, zorder=4)
    for y, name in [(15.25, "Montserrat"), (14.8, "Lora"),
                    (14.35, "Playfair Display"), (13.9, "Space Mono")]:
        ax.text(24.35, y, name, ha="left", va="center", fontsize=8,
                weight="bold", color=ink, zorder=4)
        ax.text(27.9, y, "Aa Bb Cc 0123", ha="left", va="center", fontsize=8,
                color=muted, style="italic", zorder=4)
    ax.text(24.35, 13.25, "… one labeled specimen per palette font,\ngrouped by family class",
            ha="left", va="top", fontsize=7, color=muted, style="italic",
            zorder=4)

    ax.text(17.4, 11.7, "Which palette font is the closest match to this crop?",
            ha="left", va="center", fontsize=9.5, weight="bold", color=ink,
            zorder=4)
    ax.text(30.6, 11.7, "* required", ha="right", va="center", fontsize=7.5,
            color=rose, zorder=4)

    rrect(ax, 17.4, 10.45, 9.0, 0.8, "white", muted, lw=1.0, z=2)
    ax.text(17.75, 10.85, "Type to search the palette fonts…", ha="left",
            va="center", fontsize=8.5, color=muted, zorder=4)
    ax.plot(26.0, 10.85, marker="v", markersize=4, color=muted, zorder=4)

    ax.text(24.0, 9.95, "— or —", ha="center", va="center", fontsize=7.5,
            color=muted, zorder=4)

    ax.plot(17.75, 9.35, marker="o", markersize=9, mfc="white", mec=rose,
            mew=1.4, zorder=4)
    ax.text(18.2, 9.35, "Unknown / hallucinated — no palette font matches this crop",
            ha="left", va="center", fontsize=9, weight="bold", color=rose,
            zorder=4)
    ax.text(18.2, 8.8, "Choose this when the lettering is too deformed, or the font is clearly outside the palette.",
            ha="left", va="center", fontsize=7.3, color=muted, zorder=4)

    rrect(ax, 17.4, 6.6, 3.0, 0.9, "white", muted, lw=1.1, z=3)
    ax.text(18.9, 7.05, "←  Back", ha="center", va="center", fontsize=9,
            weight="bold", color=muted, zorder=4)
    rrect(ax, 26.4, 6.6, 4.2, 0.9, teal, teal, lw=1.2, z=3)
    ax.text(28.5, 7.05, "Save & next  →", ha="center", va="center",
            fontsize=9.5, weight="bold", color="white", zorder=4)

    ax.text(17.4, 5.6, "Each answer saves on “Save & next”; you may close the tab and resume where you left off.",
            ha="left", va="center", fontsize=7.3, color=muted, style="italic",
            zorder=4)

    save_figure(fig, "expert_panel_form")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
