"""Figure 8 (Ch4 §4.4.2) — Conceptual framework of the font-identification
system, drawn as three horizontal bands rather than an input-process-output
grid:

  BEFORE DEPLOYMENT  (dashed)  palette -> render -> degrade -> teacher
                               -> student -> trained model (f_theta, tau)
  AT USE             (solid)   AI image -> localize (one box per word) ->
                               per crop: prepare -> frozen ViT (+ homogeneity
                               check) -> student head -> match test ->
                               Top-K shortlist, "unknown font", or
                               "mixed typography"
  HOW WE MEASURE IT  (dashed)  Top-K accuracy, re-render check, human panel
                               — researcher instruments, never user-facing

Layout: the trained model sits directly above the runtime metric head so the
startup hand-off is a single vertical dashed drop; the offline pipeline row is
centred on the teacher/student fork; the re-render check is aligned under the
Top-K shortlist it consumes.
Contrast: faint bands < dimmed support boxes < full-colour element boxes.
Line convention (drawn as an in-figure legend):
  solid arrow  = runs for every uploaded image
  dashed arrow = researcher-side, outside the per-image path
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


def _band(ax, x0, y0, x1, y1, label, dashed=False, fc="#FCFDFE"):
    ls = (0, (5, 3)) if dashed else "solid"
    ax.add_patch(mpatches.Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc,
                                    ec="#CBD5E1", lw=1.1, linestyle=ls,
                                    zorder=0))
    ax.text(x0 + 0.35, y1 - 0.28, label, ha="left", va="center", fontsize=10,
            weight="bold", color=COLORS["muted"], zorder=4)


def create_figure():
    apply_style()
    fig, ax = plt.subplots(figsize=(12.6, 9.7))
    ax.set_xlim(0, 19.4)
    ax.set_ylim(0, 14.9)
    ax.axis("off")

    _band(ax, 0.4, 9.95, 19.0, 14.3,
          "BEFORE DEPLOYMENT   ·   built once by the researchers",
          dashed=True, fc="#FBFBF7")
    _band(ax, 0.4, 3.55, 19.0, 9.7,
          "AT USE   ·   runs for every uploaded image")
    _band(ax, 0.4, 0.4, 19.0, 3.3,
          "HOW WE MEASURE IT   ·   researcher instruments, never shown to the user",
          dashed=True, fc="#FBFBF7")

    # ================= BAND 1 — offline preparation =================
    # Pipeline row, centred on the teacher/student fork midpoint.
    for cx, t, s in [
        (2.7, "Google Fonts palette", "50–100 typefaces\n4 family classes"),
        (6.4, "Render pristine words", "clean text crops\nfont of each is known"),
        (10.1, "Degradation  $D$", "warp · blur · noise · kerning jitter\n"
         "corpus keeps both the pristine\ncrops and their degraded copies"),
    ]:
        draw_box(ax, cx, 12.5, 3.4, 1.35, t, s, fs=9.5, sub_fs=7.2, **DIM)
    for x0, x1 in [(4.4, 4.7), (8.1, 8.4)]:
        draw_arrow(ax, (x0, 12.5), (x1, 12.5), lw=1.4)

    # the full corpus — pristine renders AND their degraded look-alikes —
    # feeds both the teacher and the student
    ax.plot([11.8, 13.15], [12.5, 12.5], color=COLORS["ink"], lw=1.4,
            zorder=2)
    ax.plot([13.15, 13.15], [11.5, 13.45], color=COLORS["ink"], lw=1.4,
            zorder=2)
    draw_arrow(ax, (13.15, 13.45), (13.4, 13.45), lw=1.4)
    draw_arrow(ax, (13.15, 11.5), (13.4, 11.5), lw=1.4)

    draw_box(ax, 15.9, 13.45, 5.0, 1.15, "Teacher model",
             "DINOv2 + LoRA, trained with font labels\n"
             "offline only — never runs at use time",
             fc=COLORS["orange_bg"], ec=COLORS["orange"], tc=COLORS["orange"],
             fs=10, sub_fs=7.2, lw=1.8)
    draw_box(ax, 15.9, 11.5, 5.0, 1.4, "Student metric head  $f_\\theta$",
             "the model that actually ships\n"
             "learns from font labels (triplet loss)\n"
             "and from the teacher (distillation)",
             fc=COLORS["blue_bg"], ec=COLORS["blue"], tc=COLORS["blue"],
             fs=10, sub_fs=7.2, lw=1.8)
    draw_arrow(ax, (15.9, 12.875), (15.9, 12.2), lw=1.5)
    ax.text(16.15, 12.55, "hands over its judgments\n(no labels needed)",
            ha="left", va="center", fontsize=6.8, color=COLORS["muted"],
            style="italic", zorder=4)

    # Trained model, aligned above the runtime metric head for a straight drop.
    draw_box(ax, 11.2, 10.5, 3.6, 0.9, "Trained model",
             "weights $f_\\theta$ · prototypes · threshold $\\tau$",
             fc=COLORS["teal_bg"], ec=COLORS["teal"], tc=COLORS["teal"],
             fs=10, sub_fs=7.2, lw=1.8)
    ax.plot([15.9, 15.9], [10.8, 10.5], color=COLORS["ink"], lw=1.4,
            zorder=2)
    ax.plot([15.9, 13.2], [10.5, 10.5], color=COLORS["ink"], lw=1.4,
            zorder=2)
    draw_arrow(ax, (13.2, 10.5), (13.0, 10.5), lw=1.4)

    # startup hand-off: the only link between the offline and runtime paths
    _dashed_arrow(ax, (11.2, 10.05), (11.2, 7.325), COLORS["teal"], lw=1.6)
    ax.text(11.45, 8.6, "loaded once at startup",
            ha="left", va="center", fontsize=7.5, color=COLORS["teal"],
            style="italic", zorder=4)

    # ================= BAND 2 — the per-image path =================
    draw_box(ax, 3.45, 8.55, 5.6, 0.95, "AI-generated image",
             "output of DALL·E / Midjourney / Stable Diffusion\n"
             "contains rendered text with warped, uneven glyphs",
             fs=10, sub_fs=7.2, **DIM)
    draw_box(ax, 8.9, 8.55, 4.2, 0.95, "Text localization",
             "off-the-shelf detector\none bounding box per word",
             fs=10, sub_fs=7.2, **DIM)
    draw_arrow(ax, (6.25, 8.55), (6.8, 8.55), lw=1.5)

    ax.plot([8.9, 8.9, 2.7], [8.075, 7.7, 7.7], color=COLORS["ink"],
            lw=1.5, zorder=2)
    draw_arrow(ax, (2.7, 7.7), (2.7, 7.325), lw=1.5)
    ax.text(5.8, 7.76, "one crop per word · each crop handled on its own",
            ha="center", va="bottom", fontsize=7.5, color=COLORS["muted"],
            style="italic", zorder=4)

    draw_box(ax, 2.7, 6.55, 4.1, 1.55, "Image preparation",
             "square-pad, resize to 224 × 224\nconvert to grayscale\nnormalize",
             fs=10, sub_fs=7.0, **DIM)
    draw_box(ax, 7.4, 6.55, 4.1, 1.55, "Frozen ViT encoder",
             "DINOv2, self-supervised · frozen\n"
             "patch tokens drive the\none-font homogeneity check",
             fc=COLORS["teal_bg"], ec=COLORS["teal"], tc=COLORS["teal"],
             fs=10, sub_fs=7.0, lw=1.8)
    draw_box(ax, 12.1, 6.55, 4.1, 1.55, "Metric head  $f_\\theta$",
             "the trained student\nturns the crop into a\nfont-style fingerprint",
             fc=COLORS["blue_bg"], ec=COLORS["blue"], tc=COLORS["blue"],
             fs=10, sub_fs=7.0, lw=1.8)
    draw_box(ax, 16.8, 6.55, 4.1, 1.55, "Match test",
             "is the closest font in the\npalette similar enough\n"
             "(within threshold $\\tau$)?",
             fc=COLORS["orange_bg"], ec=COLORS["orange"], tc=COLORS["orange"],
             fs=10, sub_fs=7.0, lw=1.8)
    for x0, x1 in [(4.75, 5.35), (9.45, 10.05), (14.15, 14.75)]:
        draw_arrow(ax, (x0, 6.55), (x1, 6.55), lw=1.5)

    # three verdicts, each drawn under the stage that produces it: the
    # homogeneity check exits at the encoder, the match test forks below it
    draw_arrow(ax, (7.4, 5.775), (7.4, 5.0), lw=1.5, color=COLORS["orange"])
    ax.text(7.6, 5.39, "patch tokens disagree — split once;\n"
            "a half that stays mixed exits here", ha="left", va="center",
            fontsize=7.0, color=COLORS["orange"], style="italic", zorder=4)

    ax.plot([15.5, 15.5, 12.2], [5.775, 5.35, 5.35], color=COLORS["teal"],
            lw=1.5, zorder=2)
    draw_arrow(ax, (12.2, 5.35), (12.2, 5.0), lw=1.5, color=COLORS["teal"])
    ax.text(12.5, 5.42, "yes — close enough", ha="left", va="bottom",
            fontsize=7.5, color=COLORS["teal"], style="italic", zorder=4)
    draw_arrow(ax, (18.0, 5.775), (18.0, 5.0), lw=1.5, color=COLORS["rose"])
    ax.text(18.15, 5.4, "no", ha="left", va="center", fontsize=7.5,
            color=COLORS["rose"], style="italic", zorder=4)

    draw_box(ax, 7.4, 4.55, 4.2, 0.9, "Mixed typography",
             "more than one typeface in one crop —\n"
             "no single font is assigned",
             fc=COLORS["orange_bg"], ec=COLORS["orange"], tc=COLORS["orange"],
             fs=10, sub_fs=7.0, lw=1.8)
    draw_box(ax, 12.2, 4.55, 4.2, 0.9, "Top-K Google Fonts shortlist",
             "ranked open-source candidates\none shortlist per word crop",
             fc=COLORS["teal_bg"], ec=COLORS["teal"], tc=COLORS["teal"],
             fs=10, sub_fs=7.0, lw=1.8)
    draw_box(ax, 16.9, 4.55, 4.2, 0.9, "Unknown font",
             "outside the palette, or too deformed\n"
             "to match — no font is guessed",
             fc=COLORS["rose_bg"], ec=COLORS["rose"], tc=COLORS["rose"],
             fs=10, sub_fs=7.0, lw=1.8)

    # ---- Legend (two line kinds only), in the free lower-left corner ----
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.55, 3.75), 4.4, 1.45, boxstyle="round,pad=0.02", fc="white",
        ec=COLORS["muted"], lw=0.9, zorder=3))
    ax.text(0.8, 4.97, "Legend", ha="left", va="center", fontsize=8.5,
            weight="bold", color=COLORS["ink"], zorder=4)
    ax.annotate("", xy=(1.52, 4.5), xytext=(0.85, 4.5), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=COLORS["ink"], lw=1.5,
                                mutation_scale=14, shrinkA=0, shrinkB=0))
    ax.text(1.7, 4.5, "solid: every uploaded image",
            ha="left", va="center", fontsize=7.2, color=COLORS["ink"], zorder=4)
    ax.annotate("", xy=(1.52, 4.05), xytext=(0.85, 4.05), zorder=5,
                arrowprops=dict(arrowstyle="-|>", color=COLORS["muted"], lw=1.4,
                                mutation_scale=14, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3))))
    ax.text(1.7, 4.05, "dashed: researcher-side,\noutside the per-image path",
            ha="left", va="center", fontsize=7.2, color=COLORS["ink"], zorder=4)

    # ================= BAND 3 — evaluation =================
    for cx, t, s in [
        (3.5, "Top-K accuracy",
         "how often the true font appears\nin the shortlist (Top-1, Top-3)"),
        (9.5, "Re-render check",
         "re-render the predicted font with the same word,\n"
         "then score how closely its shape matches the crop"),
        (16.1, "Human-proxy panel",
         "three typographers label the same crops\n"
         "by consensus, as the accuracy floor"),
    ]:
        draw_box(ax, cx, 1.55, 5.6, 1.15, t, s, fs=9.5, sub_fs=7.0, **DIM)
    _dashed_arrow(ax, (12.2, 4.1), (10.5, 3.3), COLORS["muted"], lw=1.3)
    _dashed_arrow(ax, (16.9, 4.1), (16.9, 3.3), COLORS["muted"], lw=1.3)

    ax.text(9.7, 14.62,
            "Conceptual framework of the proposed font-identification system",
            fontsize=13, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "conceptual_framework")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
