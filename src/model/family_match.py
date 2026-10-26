"""Same-family share of accepted unknown-font crops (Chapter 5, Section 5.3.2).

The final open-set report lists, for each held-out unknown font, the three
palette fonts its accepted crops were most often matched to, with counts. This
counts how many of those matches fall in the unknown font's own structural
family, to test the claim that a wrongly accepted unknown font still lands on a
usable look-alike.

# ponytail: the report keeps only the top three matches per font, so the share is
# over the crops those lists cover (about 60% of the accepted crops), not over
# every accepted crop. Exact numbers need per-crop predictions; add them if a
# reviewer asks.

    python src/model/family_match.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reports/incr3/open_set_dinov2_mid_oe_final.json"
OUT = ROOT / "reports/incr3/family_match.json"


def main():
    d = json.loads(SRC.read_text())
    per_font = d["unknown"]["n"] // len(d["unknown"]["fonts"])
    fonts, listed, same, accepted = {}, 0, 0, 0
    for font, v in d["per_unknown_font"].items():
        n_listed = sum(m["n"] for m in v["mistaken_for"])
        n_same = sum(m["n"] for m in v["mistaken_for"] if m["family"] == v["family"])
        n_acc = round(v["accepted"] * per_font)
        assert n_listed <= n_acc, f"{font}: more listed matches than accepted crops"
        fonts[font] = {"family": v["family"], "accepted": n_acc, "listed": n_listed,
                       "same_family": n_same, "share": round(n_same / n_listed, 3)}
        listed, same, accepted = listed + n_listed, same + n_same, accepted + n_acc
    out = {"source": SRC.name, "accepted": accepted, "listed": listed, "same_family": same,
           "share_same_family": round(same / listed, 4),
           "coverage_of_accepted": round(listed / accepted, 4), "per_font": fonts}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    for font, r in fonts.items():
        print(f"{font:20s} {r['family']:11s} accepted {r['accepted']:4d}  listed {r['listed']:4d}  in family {r['share']:.2f}")
    print(f"overall: {same} of {listed} listed matches in family ({same / listed:.1%}); "
          f"the lists cover {listed / accepted:.1%} of {accepted} accepted crops -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
