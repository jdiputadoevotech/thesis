"""Real-generative evaluation set (Sections 4.3.1, 4.2.3, 4.10.2).

Text-to-image outputs go in data/real/images/, one row each in
data/real/prompts.csv. Then:

    localize  EasyOCR cuts every image into word crops -> data/real/crops/ + crops.csv.
              This is the served localizer, so the unit evaluated is the unit served.
    sheet     contact sheets of the crops, numbered by crop_id, for the raters.
    predict   the frozen model (Top-3, unknown verdict, homogeneity check) and both
              baselines on every crop -> data/real/predictions.csv. Raters must not
              see this file: the panel labels blind.
    score     panel labels (data/real/labels.csv) -> consensus, Fleiss' kappa, and
              every model scored against the consensus -> reports/real/real_eval.json.

labels.csv is long format, one row per rater per crop:
    crop_id, rater, font, coherence
font is a palette family name (e.g. "Open Sans") or a font_id ("OpenSans-400"),
or "unknown"; coherence is one, two or cannot_tell. A label is ground truth
when at least two of the three raters agree (Section 4.2.3).

    .venv/Scripts/python.exe src/model/real.py localize
    .venv/Scripts/python.exe src/model/real.py sheet
    .venv/Scripts/python.exe src/model/real.py predict
    .venv/Scripts/python.exe src/model/real.py score
    .venv/Scripts/python.exe src/model/real.py --check
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REAL = ROOT / "data/real"
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
MARGIN = 0.12        # crop margin around each box, as a share of the box height (cf. the corpus)
MIN_HEIGHT = 12      # boxes shorter than this many pixels are dropped: too small to show a typeface
WIDTH_THS = 0.1      # EasyOCR merges boxes closer than this x box height; low keeps words apart
CROP_FIELDS = ["crop_id", "image", "x0", "y0", "x1", "y1", "ocr_text", "ocr_conf", "crop_path"]

norm = lambda s: re.sub(r"[\s_\-]", "", s).lower()


# ---------------------------------------------------------------- localize ---

def boxes_to_crops(results, height, width):
    """EasyOCR (quad, text, conf) -> axis-aligned crop boxes with a margin.
    Drops boxes shorter than MIN_HEIGHT."""
    out = []
    for quad, text, conf in results:
        xs, ys = [p[0] for p in quad], [p[1] for p in quad]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        h = y1 - y0
        if h < MIN_HEIGHT:
            continue
        m = MARGIN * h
        box = (max(0, int(x0 - m)), max(0, int(y0 - m)), min(width, int(np.ceil(x1 + m))), min(height, int(np.ceil(y1 + m))))
        out.append((box, text, float(conf)))
    return out


def localize(args):
    import easyocr
    from PIL import Image
    (REAL / "images").mkdir(exist_ok=True)  # gitignored, so absent in a fresh clone
    images = sorted(p for p in (REAL / "images").iterdir() if p.suffix.lower() in IMAGE_TYPES)
    assert images, f"no images yet: put the generator outputs in {REAL / 'images'} (see data/real/README.md)"
    reader = easyocr.Reader(["en"], gpu=args.gpu, verbose=False)  # its progress bar crashes a cp1252 console
    (REAL / "crops").mkdir(exist_ok=True)
    rows = []
    for img_path in images:
        img = Image.open(img_path).convert("RGB")
        a = np.asarray(img)
        found = boxes_to_crops(reader.readtext(a, width_ths=WIDTH_THS), *a.shape[:2])
        for k, ((x0, y0, x1, y1), text, conf) in enumerate(found):
            crop_id = f"{img_path.stem}_{k:02d}"
            path = REAL / "crops" / f"{crop_id}.png"
            img.crop((x0, y0, x1, y1)).save(path)
            rows.append({"crop_id": crop_id, "image": img_path.name, "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                         "ocr_text": text, "ocr_conf": round(conf, 3),
                         "crop_path": path.relative_to(ROOT).as_posix()})
        print(f"{img_path.name}: {len(found)} crops", file=sys.stderr)
    with (REAL / "crops.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CROP_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} crops from {len(images)} images -> {REAL / 'crops.csv'}")


# ------------------------------------------------------------------- sheet ---

def sheet(args, per_page=24, cell=(420, 150)):
    from PIL import Image, ImageDraw
    rows = list(csv.DictReader((REAL / "crops.csv").open(encoding="utf-8")))
    pages = [rows[i:i + per_page] for i in range(0, len(rows), per_page)]
    for n, page in enumerate(pages, 1):
        cols = 3
        im = Image.new("RGB", (cols * cell[0], ((len(page) + cols - 1) // cols) * cell[1]), "white")
        d = ImageDraw.Draw(im)
        for i, r in enumerate(page):
            crop = Image.open(ROOT / r["crop_path"]).convert("RGB")
            crop.thumbnail((cell[0] - 20, cell[1] - 34))
            x, y = (i % cols) * cell[0], (i // cols) * cell[1]
            im.paste(crop, (x + 10, y + 26))
            d.text((x + 10, y + 6), r["crop_id"], fill="black")
            d.rectangle([x, y, x + cell[0] - 1, y + cell[1] - 1], outline=(200, 200, 200))
        path = REAL / f"sheet_{n:02d}.png"
        im.save(path)
        print(path, file=sys.stderr)
    print(f"{len(pages)} sheet(s), {len(rows)} crops")


# ----------------------------------------------------------------- predict ---

def predict(args):
    import torch
    from encoder import FontEmbedder, Head
    from homogeneity import CHOSEN, GRID_CUTS, calibrated, cut_distances
    from open_set import calibrate, decide, embed
    from train_head import prototypes

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    ck = torch.load(ROOT / args.head, map_location="cpu")
    head = Head(ck["d_in"], ck.get("dim", 256), ck.get("hidden", 512)).eval()
    head.load_state_dict(ck["state_dict"])
    fonts = ck["fonts"]
    fi = {f: i for i, f in enumerate(fonts)}
    rows_c, z = embed(head, ck["backbone"], "data/corpus")
    y = torch.tensor([fi[r["font_id"]] for r in rows_c])
    split = np.array([r["split"] for r in rows_c])
    protos = prototypes(z[split == "train"], y[split == "train"], len(fonts))
    tau = calibrate(decide(z[split == "validation"], protos)[0])
    grid, h_score, h_cut = calibrated()
    assert np.array_equal(grid, GRID_CUTS)

    emb = FontEmbedder.load(ROOT / args.head).to(dev)
    from PIL import Image
    crops = list(csv.DictReader((REAL / "crops.csv").open(encoding="utf-8")))
    load = lambda r: torch.from_numpy(np.array(Image.open(ROOT / r["crop_path"]).convert("L")))

    def recognise(img):
        with torch.no_grad(), torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
            zz = emb([img]).float().cpu()
        sims = (zz @ protos.T)[0]
        v, i = sims.topk(3)
        return [fonts[int(k)] for k in i], [round(float(s), 4) for s in v]

    def check(img):
        d = cut_distances(emb, [img], dev, GRID_CUTS)
        sc, arg = h_score(d, np.array([img.shape[:2]]))
        return bool(sc[0] >= h_cut), float(GRID_CUTS[arg[0]])

    out = []
    for n, r in enumerate(crops):
        img = load(r)
        top, sims = recognise(img)
        flagged, cut = check(img)
        row = {"crop_id": r["crop_id"], "ours_top3": "|".join(top), "ours_sims": "|".join(map(str, sims)),
               "ours_verdict": "known" if sims[0] >= tau else "unknown",
               "homog_flag": flagged, "homog_cut": round(cut, 2) if flagged else "", "halves": ""}
        if flagged:  # split once at the cut and match each half; a half still flagged is mixed typography
            c = int(round(img.shape[1] * cut))
            halves = []
            for half in (img[:, :c], img[:, c:]):
                h_top, h_sims = recognise(half)
                still, _ = check(half)
                halves.append("mixed" if still else (h_top[0] if h_sims[0] >= tau else "unknown"))
            row["halves"] = "|".join(halves)
        out.append(row)
        if n % 20 == 0:
            print(f"ours {n}/{len(crops)}", file=sys.stderr)

    # Baselines: top-3 families in their own catalogues.
    from baselines import Chen, Storia
    for name, model in (("storia", Storia()), ("chen", Chen(dev))):
        for row, r in zip(out, crops):
            p = model.probs([Image.open(ROOT / r["crop_path"]).convert("RGB")])[0]
            fam = {}
            for c, f in enumerate(model.classes):
                fam[f] = max(fam.get(f, 0.0), float(p[c]))
            row[f"{name}_top3"] = "|".join(f for f, _ in sorted(fam.items(), key=lambda kv: -kv[1])[:3])

    with (REAL / "predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} crops -> {REAL / 'predictions.csv'} (tau {tau:.4f}, homogeneity cutoff {h_cut:.3f}, {CHOSEN})")


# ------------------------------------------------------------------- score ---

def fleiss_kappa(table):
    """table: (items, categories) counts of raters per category; every item rated
    by the same number of raters."""
    t = np.asarray(table, float)
    n = t.sum(1)[0]
    assert (t.sum(1) == n).all() and n > 1, "every item needs the same number of raters"
    p_j = t.sum(0) / t.sum()
    p_i = ((t * t).sum(1) - n) / (n * (n - 1))
    p_bar, p_e = p_i.mean(), (p_j ** 2).sum()
    return float((p_bar - p_e) / (1 - p_e)) if p_e < 1 else 1.0


def consensus(labels, k=2):
    """The value at least k raters gave, or None."""
    value, count = Counter(labels).most_common(1)[0]
    return value if count >= k else None


def to_family(label, family_of):
    """A rater's answer -> normalized palette family, or 'unknown'."""
    key = norm(label)
    if key in ("unknown", "hallucinated", "unknownhallucinated", ""):
        return "unknown"
    return family_of.get(key, key)


def score(args):
    palette = list(csv.DictReader((ROOT / "data/palette.csv").open()))
    family_of = {}
    for r in palette:
        family_of[norm(r["family"])] = norm(r["family"])
        family_of[norm(r["font_id"])] = norm(r["family"])
    labels = list(csv.DictReader((REAL / "labels.csv").open(encoding="utf-8")))
    preds = {r["crop_id"]: r for r in csv.DictReader((REAL / "predictions.csv").open(encoding="utf-8"))}
    by_crop = {}
    for r in labels:
        by_crop.setdefault(r["crop_id"], []).append(r)
    unknown_labels = sorted({r["font"] for r in labels if to_family(r["font"], family_of) not in family_of.values()
                             and to_family(r["font"], family_of) != "unknown"})

    fam = lambda f: norm(f.rsplit("-", 1)[0])
    font_cats = sorted({to_family(r["font"], family_of) for r in labels})
    full = [c for c, rs in by_crop.items() if len(rs) == 3]
    table = [[sum(to_family(r["font"], family_of) == cat for r in by_crop[c]) for cat in font_cats] for c in full]
    coh_cats = ["one", "two", "cannot_tell"]
    coh_table = [[sum(r["coherence"] == cat for r in by_crop[c]) for cat in coh_cats] for c in full]

    res = {"n_crops_labelled": len(by_crop), "n_crops_three_raters": len(full),
           "fleiss_kappa_font": fleiss_kappa(table) if full else None,
           "fleiss_kappa_coherence": fleiss_kappa(coh_table) if full else None,
           "labels_not_in_palette": unknown_labels}
    known, unknown, coherent = [], [], []
    for c, rs in by_crop.items():
        f = consensus([to_family(r["font"], family_of) for r in rs])
        coh = consensus([r["coherence"] for r in rs])
        if c not in preds:
            continue
        p = preds[c]
        if coh in ("one", "two"):
            coherent.append((coh == "two", p["homog_flag"] == "True"))
        if f is None:
            continue
        ours = [fam(x) for x in p["ours_top3"].split("|")]
        accepted = p["ours_verdict"] == "known"
        if f == "unknown":
            unknown.append({"ours_says_unknown": not accepted})
        else:
            known.append({"top1": ours[0] == f, "top3": f in ours, "accepted": accepted,
                          "storia_top1": p["storia_top3"].split("|")[0] == f,
                          "chen_top1": p["chen_top3"].split("|")[0] == f})
    mean = lambda xs, k: float(np.mean([x[k] for x in xs])) if xs else None
    res["consensus_font"] = {"n": len(known), "top1": mean(known, "top1"), "top3": mean(known, "top3"),
                             "accepted": mean(known, "accepted"),
                             "top1_when_accepted": (float(np.mean([x["top1"] for x in known if x["accepted"]]))
                                                    if any(x["accepted"] for x in known) else None),
                             "storia_top1": mean(known, "storia_top1"), "chen_top1": mean(known, "chen_top1")}
    res["consensus_unknown"] = {"n": len(unknown), "ours_says_unknown": mean(unknown, "ours_says_unknown")}
    res["homogeneity_vs_panel"] = {
        "n": len(coherent),
        "agreement": float(np.mean([a == b for a, b in coherent])) if coherent else None,
        "panel_two_fonts": int(sum(a for a, _ in coherent)),
        "flagged_when_panel_two": (float(np.mean([b for a, b in coherent if a])) if any(a for a, _ in coherent) else None),
        "flagged_when_panel_one": (float(np.mean([b for a, b in coherent if not a])) if any(not a for a, _ in coherent) else None)}
    out = ROOT / "reports/real/real_eval.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


# ------------------------------------------------------------------- check ---

def check():
    # Fleiss' kappa: perfect agreement -> 1; the Wikipedia worked example -> 0.210.
    assert abs(fleiss_kappa([[3, 0], [0, 3], [3, 0]]) - 1) < 1e-9
    wiki = [[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1],
            [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]]
    assert abs(fleiss_kappa(wiki) - 0.210) < 0.001, fleiss_kappa(wiki)
    assert consensus(["a", "a", "b"]) == "a" and consensus(["a", "b", "c"]) is None
    fam = {"opensans": "opensans", "opensans400": "opensans"}
    assert to_family("Open Sans", fam) == "opensans" and to_family("OpenSans-400", fam) == "opensans"
    assert to_family("Unknown", fam) == "unknown"
    # A 100x20 box at (10, 50) in a 200x400 image gets a 12% margin, clipped at the edges.
    crops = boxes_to_crops([([[10, 50], [110, 50], [110, 70], [10, 70]], "word", 0.9),
                            ([[0, 0], [5, 0], [5, 4], [0, 4]], "tiny", 0.9)], 200, 400)
    assert len(crops) == 1 and crops[0][0] == (7, 47, 113, 73), crops
    print("ok")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    ap = argparse.ArgumentParser()
    ap.add_argument("step", nargs="?", choices=["localize", "sheet", "predict", "score"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--head", default="data/models/head_dinov2_mid_oe.pt")
    ap.add_argument("--gpu", action=argparse.BooleanOptionalAction, default=True, help="EasyOCR on the GPU")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.step:
        {"localize": localize, "sheet": sheet, "predict": predict, "score": score}[a.step](a)
    else:
        ap.print_help()
