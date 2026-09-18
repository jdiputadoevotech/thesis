"""Freeze the Google Fonts palette: select families, download TTFs, pin versions.

Produces data/palette.csv (the class list, committed) and data/fonts/*.ttf
(the binaries, gitignored). Every downstream stage keys on `font_id`.

Selection follows Section 4.1: top-N by Google Fonts' own popularity ranking,
quota'd across the four structural family classes of Section 3.2.1. One weight
per family by default -- Chen et al. (2026) dropped to 40.2% family accuracy by
admitting near-identical weight variants, so extra weights are opt-in.

    python src/data/build_palette.py            # build with defaults
    python src/data/build_palette.py --check    # self-check, no network writes
"""

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

METADATA_URL = "https://fonts.google.com/metadata/fonts"
CSS_URL = "https://fonts.googleapis.com/css2?family={family}:wght@{weight}"
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

# Google's category label -> the four structural classes of Section 3.2.1.
# Handwriting is excluded: it is the ornamental long tail Section 4.1 trims.
CLASSES = {
    "Sans Serif": "sans-serif",
    "Serif": "serif",
    "Display": "display",
    "Monospace": "monospace",
}

# Popularity is heavily sans-skewed, so a flat top-N would starve serif/mono.
# Quota mirrors real-world usage while guaranteeing every class is populated.
QUOTA = {"sans-serif": 32, "serif": 24, "display": 16, "monospace": 8}

WEIGHTS = ["400"]  # ponytail: one weight per family; add "700" here if the
# confusion matrix shows the model has headroom for weight discrimination.


def fetch_metadata(cache: Path):
    """Google Fonts' public family index. Cached, because the ranking drifts."""
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(METADATA_URL) as r:
            cache.write_bytes(r.read())
    # The endpoint prefixes an XSSI guard before the JSON body.
    return json.loads(cache.read_text().lstrip(")]}'\n"))["familyMetadataList"]


def eligible(fam):
    # isBrandFont is deliberately NOT a filter: Google flags its own faces that
    # way, which would drop Roboto -- the single most-used face on the web -- and
    # isOpenSource already answers the licensing question Section 4.1 cares about.
    return (
        fam["category"] in CLASSES
        and fam.get("isOpenSource")
        and not fam.get("isNoto")  # a script-coverage project, not a design palette
        and "latin" in fam.get("subsets", [])
    )


def select(families, quota=QUOTA, weights=WEIGHTS):
    """Top families per class by popularity rank (1 = most popular)."""
    picked = []
    for fam in sorted(families, key=lambda f: f["popularity"]):
        if not eligible(fam):
            continue
        cls = CLASSES[fam["category"]]
        if sum(1 for p in picked if p["family_class"] == cls) >= quota[cls] * len(weights):
            continue
        for w in weights:
            if w not in fam["fonts"]:
                continue
            picked.append(
                {
                    "font_id": f"{fam['family'].replace(' ', '')}-{w}",
                    "family": fam["family"],
                    "weight": w,
                    "family_class": cls,
                    "popularity": fam["popularity"],
                    "gf_last_modified": fam["lastModified"],
                }
            )
    return picked


def resolve_ttf(family, weight):
    """The CSS2 API hands back a versioned .ttf URL -- that version is the pin."""
    url = CSS_URL.format(family=urllib.parse.quote(family), weight=weight)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        css = r.read().decode()
    match = re.search(r"url\((https://[^)]+\.ttf)\)", css)
    if not match:
        raise RuntimeError(f"no TTF in CSS for {family}:{weight}")
    return match.group(1)


def download(row, font_dir):
    font_dir.mkdir(parents=True, exist_ok=True)
    path = font_dir / f"{row['font_id']}.ttf"
    if not path.exists():
        with urllib.request.urlopen(resolve_ttf(row["family"], row["weight"])) as r:
            path.write_bytes(r.read())
    row["ttf_path"] = str(path.relative_to(ROOT))
    row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return row


def build(out_csv, font_dir, cache):
    rows = select(fetch_metadata(cache))
    for i, row in enumerate(rows, 1):
        download(row, font_dir)
        print(f"[{i}/{len(rows)}] {row['font_id']}", file=sys.stderr)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def check():
    """Selection is the only non-trivial logic here, so it is what gets asserted."""
    fake = [
        {"family": f"F{i}", "category": cat, "popularity": i, "lastModified": "2026-01-01",
         "isOpenSource": True, "isBrandFont": False, "isNoto": False,
         "subsets": ["latin"], "fonts": {"400": {}}}
        for i, cat in enumerate(list(CLASSES) * 60, start=1)
    ]
    fake.append({"family": "NotoX", "category": "Serif", "popularity": 0,
                 "lastModified": "2026-01-01", "isOpenSource": True, "isBrandFont": False,
                 "isNoto": True, "subsets": ["latin"], "fonts": {"400": {}}})
    fake.append({"family": "CJKOnly", "category": "Serif", "popularity": 0,
                 "lastModified": "2026-01-01", "isOpenSource": True, "isBrandFont": False,
                 "isNoto": False, "subsets": ["japanese"], "fonts": {"400": {}}})
    got = select(fake)
    counts = {c: sum(1 for r in got if r["family_class"] == c) for c in QUOTA}
    assert counts == QUOTA, counts
    assert len(got) == sum(QUOTA.values()) == 80, len(got)
    assert not any(r["family"] in ("NotoX", "CJKOnly") for r in got), "filter leaked"
    assert len({r["font_id"] for r in got}) == len(got), "font_id collision"
    print("ok:", counts)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", type=Path, default=DATA / "palette.csv")
    ap.add_argument("--fonts", type=Path, default=DATA / "fonts")
    ap.add_argument("--cache", type=Path, default=DATA / "raw" / "gf_metadata.json")
    args = ap.parse_args()
    if args.check:
        check()
    else:
        rows = build(args.out, args.fonts, args.cache)
        print(f"{len(rows)} fonts -> {args.out}")
