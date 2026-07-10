"""Figure 11 (Ch4 §4.9.1) — Project schedule as a weekly-cell Gantt grid.
7 months (Jun–Dec 2026) x 4 weeks = 28 week columns; tasks grouped into
Writing / Development / Closeout with subtasks. Highlighted cells mark active weeks.
Pure matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from _style import apply_style, save_figure, COLORS

MONTHS = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NWEEKS = len(MONTHS) * 4  # 28
TODAY = 4 + 1.4           # Jul, ~1.4 weeks in (Jul 10)

FILL = {"done": COLORS["teal_bg"], "active": COLORS["orange_bg"], "planned": COLORS["blue_bg"]}
EDGE = {"done": COLORS["teal"], "active": COLORS["orange"], "planned": COLORS["blue"]}

# rows top -> bottom. ('group', label) or ('task', label, (col_start, col_end_inclusive), status)
ROWS = [
    ("group", "WRITING"),
    ("task", "Ch. 2  Review of Related Literature", (0, 2), "done"),
    ("task", "Ch. 3  Technical Background", (1, 5), "done"),
    ("task", "Ch. 4  Methodology", (4, 7), "active"),
    ("task", "Ch. 5  Results and Discussion", (17, 21), "planned"),
    ("task", "Ch. 6  Summary and Conclusions", (21, 24), "planned"),
    ("group", "DEVELOPMENT"),
    ("task", "Inc 1   Palette curation + rendering", (5, 7), "planned"),
    ("task", "Inc 1   Degradation operator D", (7, 9), "planned"),
    ("task", "Inc 2   Frozen encoder + metric head", (9, 11), "planned"),
    ("task", "Inc 2   Triplet training + distillation", (11, 13), "planned"),
    ("task", "Inc 3   Open-set rejection + Top-K", (13, 15), "planned"),
    ("task", "Inc 3   Evaluation + human panel", (15, 18), "planned"),
    ("task", "Inc 4   Backend + inference API", (17, 19), "planned"),
    ("task", "Inc 4   Frontend + Docker deploy", (19, 21), "planned"),
    ("group", "CLOSEOUT"),
    ("task", "Revisions and final defense", (24, 27), "planned"),
]


def create_figure():
    apply_style()
    R = len(ROWS)
    fig, ax = plt.subplots(figsize=(13.2, 7.4))
    ax.set_xlim(-9.2, NWEEKS + 0.3)
    ax.set_ylim(-1.4, R + 1.6)
    ax.axis("off")

    def ybase(idx):
        return R - 1 - idx

    # grid: week columns
    for c in range(NWEEKS + 1):
        lw = 1.4 if c % 4 == 0 else 0.5
        col = COLORS["muted"] if c % 4 == 0 else COLORS["grid"]
        ax.plot([c, c], [0, R], color=col, lw=lw, zorder=1)
    for r in range(R + 1):
        ax.plot([0, NWEEKS], [r, r], color=COLORS["grid"], lw=0.5, zorder=1)

    # month + week headers
    for i, mon in enumerate(MONTHS):
        ax.text(i * 4 + 2, R + 0.85, mon, ha="center", va="center", fontsize=10.5,
                weight="bold", color=COLORS["muted"])
        for w in range(4):
            ax.text(i * 4 + w + 0.5, R + 0.3, str(w + 1), ha="center", va="center",
                    fontsize=6.5, color=COLORS["muted"])
    ax.text(-4.6, R + 0.55, "Week of month", ha="center", va="center", fontsize=7.5,
            color=COLORS["muted"], style="italic")

    # rows
    for idx, row in enumerate(ROWS):
        yb = ybase(idx)
        if row[0] == "group":
            ax.add_patch(mpatches.Rectangle((-9.2, yb), 9.2 + NWEEKS, 1,
                         fc="#EEF2F6", ec="none", zorder=2))
            ax.plot([0, NWEEKS], [yb, yb], color=COLORS["muted"], lw=0.6, zorder=2)
            ax.plot([0, NWEEKS], [yb + 1, yb + 1], color=COLORS["muted"], lw=0.6, zorder=2)
            ax.text(-9.0, yb + 0.5, row[1], ha="left", va="center", fontsize=9.5,
                    weight="bold", color=COLORS["ink"], zorder=4)
        else:
            _, label, (a, b), status = row
            ax.text(-8.7, yb + 0.5, label, ha="left", va="center", fontsize=8.5,
                    color=COLORS["ink"], zorder=4)
            for c in range(a, b + 1):
                ax.add_patch(mpatches.Rectangle((c + 0.08, yb + 0.12), 0.84, 0.76,
                             fc=FILL[status], ec=EDGE[status], lw=1.0, zorder=3))

    # today marker
    ax.plot([TODAY, TODAY], [0, R + 0.15], color=COLORS["rose"], lw=1.7,
            linestyle=(0, (4, 2)), zorder=5)
    ax.text(TODAY, -0.35, "today (Jul 10)", ha="center", va="center", fontsize=8,
            weight="bold", color=COLORS["rose"])

    # legend
    handles = [mpatches.Patch(fc=FILL[k], ec=EDGE[k], lw=1.1, label=v)
               for k, v in [("done", "completed"), ("active", "in progress"), ("planned", "planned")]]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.135, -0.16),
              frameon=False, fontsize=8.5, handlelength=1.3, ncol=3, columnspacing=1.2)

    ax.text((NWEEKS - 9.2) / 2, R + 1.35,
            "Project schedule and timeline (June to December 2026)",
            fontsize=12.5, weight="bold", ha="center", color=COLORS["ink"])

    save_figure(fig, "gantt_timeline")
    plt.close(fig)


if __name__ == "__main__":
    create_figure()
