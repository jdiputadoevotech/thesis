"""Proposal-defense timeline banners (2 slides) — milestone-strip style.

Renders `proposal-presentation/slides/assets/timeline_1.png` and `timeline_2.png`.
Data is the signed Schedule of Deliverables (`Gantt Chart Final T7.xlsx`); increment
subtask names match the published ROWS list in `gantt_timeline.py` so the deck and
Chapter 4 agree. Pure matplotlib.

Run from this directory:  python presentation_timeline.py
"""
import os
import textwrap
from datetime import date

import matplotlib.pyplot as plt
from _style import apply_style, pick_font, COLORS

OUT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "proposal-presentation", "slides", "assets"))

CREAM = "#F5F1E8"
SPINE = "#BFB9AF"
INK = "#26221D"
MUTED = "#8A837A"

# decorative dot colours, cycled per event (reference image uses varied hues)
DOTS = ["#C0392B", "#3B7EA1", "#E08A1E", "#4A9D5B", "#8E5AA8",
        "#2E9199", "#D4A32C", "#5B6B7C", "#B0555F", "#3F7F6B"]

WRITE_BAND = "#B9CFE4"   # top lane  — writing track
DEV_BAND = "#B4D6BC"     # bottom lane — development / closeout track
BAND_TEXT = "#3D4A44"

# ── geometry (y in axis units; ylim is ±1.5) ────────────────────────────────
# The bar is three fused strips: writing lane, a centre gutter the dots sit in,
# and the development lane. The gutter is what keeps a dot off the lane labels.
LANE_Y = 0.083           # lane centre offset from the spine centre (lanes abut the gutter)
LANE_LW = 11             # lane thickness in points
GUTTER_LW = 9            # centre strip thickness in points
SPINE_HALF = 0.135       # outer edge of the fused bar
TIERS = (0.34, 0.92)     # stem-top heights, tier 0 and tier 1
H_DATE, H_TITLE, H_SUB = 0.090, 0.124, 0.090   # text line advances
WRAP = 22                # title wrap width in characters

FS_DATE, FS_TITLE, FS_SUB, FS_BAND = 8.0, 10.0, 8.0, 7.0


def ev(d, datestr, title, sub, force_side=None, emphasis=False, tentative=False):
    """`d` always anchors the dot; `tentative` events show a month-level label,
    a dashed stem and a hollow dot because the exact day is not yet fixed."""
    return dict(x=d, datestr=datestr, title=title, sub=sub,
                force_side=force_side, emphasis=emphasis, tentative=tentative)


SLIDES = [
    dict(
        name="timeline_1",
        start=date(2026, 6, 8), end=date(2026, 8, 12),
        bands=[
            (+1, date(2026, 6, 15), date(2026, 7, 23), "Writing — Ch. 2, Ch. 3, Bibliography, Ch. 4, Ch. 1", WRITE_BAND),
            (-1, date(2026, 7, 1), date(2026, 8, 5), "Preparation — environment, corpus, tooling", DEV_BAND),
        ],
        marker=dict(x=date(2026, 8, 3), text="We are here"),
        events=[
            ev(date(2026, 6, 15), "3rd Week of June", "Ch. 2 — Related Literature", "Writing begins · JD"),
            ev(date(2026, 6, 26), "Jun 26", "Signed Schedule of Deliverables", "Both"),
            ev(date(2026, 7, 1), "Jul 1", "Preparation begins", "Environment, corpus, tooling · JD"),
            ev(date(2026, 7, 3), "Jul 3", "Ch. 2, Ch. 3, Bibliography submitted", "JD"),
            ev(date(2026, 7, 9), "Jul 9–10", "Objectives / SOP", "Ch. 4 Methodology submitted · MC"),
            ev(date(2026, 7, 16), "Jul 16–17", "Appendices, CV · Ch. 1", "SRS, instrument, Abstract · Both"),
            ev(date(2026, 7, 23), "Jul 23–27", "Proposal packet submitted", "Draft, agreement letter, 3 copies"),
            ev(date(2026, 8, 3), "Aug 3–5", "Thesis Proposal Defense", "Both", force_side=-1, emphasis=True),
        ],
    ),
    dict(
        name="timeline_2",
        start=date(2026, 8, 5), end=date(2027, 1, 8),
        bands=[
            (+1, date(2026, 10, 2), date(2026, 11, 30), "Writing — Ch. 5 and Ch. 6", WRITE_BAND),
            (-1, date(2026, 8, 6), date(2026, 8, 26), "Increment 1", DEV_BAND),
            (-1, date(2026, 8, 27), date(2026, 9, 16), "Increment 2", DEV_BAND),
            (-1, date(2026, 9, 10), date(2026, 10, 1), "Increment 3", DEV_BAND),
            (-1, date(2026, 10, 2), date(2026, 10, 25), "Increment 4", DEV_BAND),
            (-1, date(2026, 12, 1), date(2026, 12, 20), "Closeout", DEV_BAND),
        ],
        marker=None,
        events=[
            ev(date(2026, 8, 6), "Aug 6", "Increment 1 begins", "Palette + rendering · JD"),
            ev(date(2026, 8, 10), "Aug 10–14", "Rubrics and revised document", "Compliance form · Both"),
            ev(date(2026, 8, 27), "Aug 27", "Increment 2 begins", "Encoder + metric head · JD"),
            ev(date(2026, 9, 10), "Sep 10", "Increment 3 begins", "Open-set rejection + Top-K"),
            ev(date(2026, 10, 1), "Oct 1", "Evaluation + human panel", "Increment 3 complete · Both"),
            ev(date(2026, 10, 2), "Oct 2", "Increment 4 and Ch. 5 begin", "Backend + inference API · MC"),
            ev(date(2026, 10, 13), "Mid-October", "Conference", "Both", tentative=True),
            ev(date(2026, 10, 25), "Oct 25", "Increment 4 complete", "Frontend + Docker · MC"),
            # December is one block: no day is fixed yet, so closeout, the hardbound
            # copy and the defense ride a single marker instead of three fake dates.
            ev(date(2026, 12, 12), "December", "Closeout and Final Defense",
               "Testing, revision, hardbound copy · Both", emphasis=True, tentative=True),
        ],
    ),
]

FIG_W, FIG_H = 13.2, 5.0
AX_RECT = (0.018, 0.02, 0.964, 0.96)   # left, bottom, width, height (figure fraction)
Y_SPAN = 3.0


def _assign(events, span_days):
    """Side (+1 above / -1 below) and tier per event; greedy, shortest free tier.

    Label x-extents are estimated from character counts and must not collide
    within a (side, tier) slot — the mid-July cluster is 7 days apart and the
    labels are ~9 days wide, so this is what keeps the banner readable.
    """
    ax_w_in = FIG_W * AX_RECT[2]
    days_per_in = span_days / ax_w_in

    # dots one day apart merge into a blob at this scale — nudge them to at least
    # one dot-width of clear air. The label still carries the true date.
    min_sep = 1.35 * (11 / 72.0) * days_per_in
    for prev, e in zip(events, events[1:]):
        e["x_days"] = max(e["x_days"], prev["x_days"] + min_sep)

    placed = {}   # (side, tier) -> list of (lo, hi)
    for i, e in enumerate(events):
        lines = textwrap.wrap(e["title"], WRAP) or [""]
        e["lines"] = lines
        n_chars = max([len(s) for s in lines] + [len(e["datestr"]), len(e["sub"]) * 8 // 10])
        w_in = n_chars * 0.55 * FS_TITLE / 72.0
        e["w_days"] = w_in * days_per_in

        side = e["force_side"] or (1 if i % 2 == 0 else -1)
        # right-align labels that would overflow the right edge
        e["align"] = "right" if e["x_days"] + e["w_days"] > span_days else "left"
        lo = e["x_days"] - e["w_days"] if e["align"] == "right" else e["x_days"]
        hi = lo + e["w_days"]

        for tier in range(len(TIERS)):
            slot = placed.setdefault((side, tier), [])
            if all(hi + 1.5 < a or lo - 1.5 > b for a, b in slot):
                slot.append((lo, hi))
                e["side"], e["tier"], e["extent"] = side, tier, (lo, hi)
                break
        else:                                  # both tiers busy — flip sides
            side = -side
            for tier in range(len(TIERS)):
                slot = placed.setdefault((side, tier), [])
                if all(hi + 1.5 < a or lo - 1.5 > b for a, b in slot):
                    slot.append((lo, hi))
                    e["side"], e["tier"], e["extent"] = side, tier, (lo, hi)
                    break
            else:
                slot = placed.setdefault((side, len(TIERS) - 1), [])
                slot.append((lo, hi))
                e["side"], e["tier"], e["extent"] = side, len(TIERS) - 1, (lo, hi)
    return events


def build(slide, font):
    span = (slide["end"] - slide["start"]).days
    for e in slide["events"]:
        e["x_days"] = (e["x"] - slide["start"]).days
    events = _assign(slide["events"], span)

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes(AX_RECT)
    ax.set_xlim(-span * 0.012, span * 1.012)   # inset so the bar's round caps show
    ax.set_ylim(-Y_SPAN / 2, Y_SPAN / 2)
    ax.axis("off")
    ax.set_facecolor(CREAM)

    # fused spine — grey base (two lanes + gutter), then coloured track bands
    ax.plot([0, span], [0, 0], color=SPINE, lw=GUTTER_LW,
            solid_capstyle="round", zorder=2)
    for s in (+1, -1):
        ax.plot([0, span], [s * LANE_Y] * 2, color=SPINE, lw=LANE_LW,
                solid_capstyle="round", zorder=2)
    for lane, d0, d1, label, colour in slide["bands"]:
        a = (d0 - slide["start"]).days
        b = (d1 - slide["start"]).days
        ax.plot([a, b], [lane * LANE_Y] * 2, color=colour, lw=LANE_LW,
                solid_capstyle="round", zorder=3)
        if b - a > span * 0.06:
            ax.text((a + b) / 2, lane * LANE_Y, label, ha="center", va="center",
                    fontsize=FS_BAND, color=BAND_TEXT, family=font, zorder=4)

    for i, e in enumerate(events):
        colour = COLORS["rose"] if e["emphasis"] else DOTS[i % len(DOTS)]
        s, x = e["side"], e["x_days"]
        top = TIERS[e["tier"]]

        ax.plot([x, x], [s * SPINE_HALF, s * top], color=colour, lw=1.6,
                ls=(0, (2.5, 2)) if e["tentative"] else "-",
                solid_capstyle="butt", zorder=5)
        ax.plot([x], [0], marker="o", ms=14 if e["emphasis"] else 11,
                color=CREAM if e["tentative"] else colour,
                markeredgecolor=colour, markeredgewidth=2.2 if e["tentative"] else 0,
                zorder=6, clip_on=False)

        ha = e["align"]
        block = H_DATE + len(e["lines"]) * H_TITLE + H_SUB
        y = s * top + (block if s > 0 else 0)      # y of the topmost text line
        ax.text(x, y, e["datestr"], ha=ha, va="top", fontsize=FS_DATE,
                color=MUTED, family=font, zorder=6)
        y -= H_DATE
        for line in e["lines"]:
            ax.text(x, y, line, ha=ha, va="top",
                    fontsize=FS_TITLE + (0.8 if e["emphasis"] else 0),
                    color=COLORS["rose"] if e["emphasis"] else INK,
                    weight="bold", family=font, zorder=6)
            y -= H_TITLE
        ax.text(x, y, e["sub"], ha=ha, va="top", fontsize=FS_SUB,
                color=MUTED, family=font, zorder=6)

    m = slide["marker"]
    if m:
        mx = (m["x"] - slide["start"]).days
        ax.annotate("", xy=(mx, SPINE_HALF + 0.02), xytext=(mx, 0.60),
                    arrowprops=dict(arrowstyle="-|>", color=COLORS["rose"], lw=2.6,
                                    mutation_scale=20, shrinkA=0, shrinkB=0), zorder=7)
        ax.text(mx, 0.65, m["text"], ha="center", va="bottom", fontsize=11.5,
                weight="bold", color=COLORS["rose"], family=font, zorder=7)

    if any(e["tentative"] for e in events):
        ax.text(span, -Y_SPAN / 2 + 0.05, "Hollow marker — month is set, exact date to be confirmed",
                ha="right", va="bottom", fontsize=7.5, color=MUTED, family=font, zorder=7)

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{slide['name']}.png")
    fig.savefig(path, dpi=300, facecolor=CREAM)
    plt.close(fig)
    print(f"Saved {path}")
    return events


def _check(rendered):
    """Excel serial base and label-collision guards."""
    assert (date(2026, 6, 1) - date(1899, 12, 30)).days == 46174, "serial base drifted"
    for name, events in rendered.items():
        slots = {}
        for e in events:
            slots.setdefault((e["side"], e["tier"]), []).append((e["extent"], e["title"]))
        for slot, items in slots.items():
            items.sort()
            for (a, ta), (b, tb) in zip(items, items[1:]):
                assert a[1] <= b[0], f"{name} {slot}: '{ta}' overlaps '{tb}'"
    print("checks passed")


if __name__ == "__main__":
    apply_style()
    font = pick_font("Lato", "Open Sans", "Segoe UI", "Arial")
    _check({s["name"]: build(s, font) for s in SLIDES})
