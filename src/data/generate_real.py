"""Real-generative image plan, generation and crop selection (Sections 4.3.1, 4.2.3).

The out-of-distribution test needs text from real text-to-image outputs. This script
plans the prompts, makes the open-weight share on a GPU, logs the images made by hand
in closed tools, and picks the evaluation crops by quota after `real.py localize`.

    plan     data/real/plan.csv: one row per image to make, with an opaque id (r001...),
             the generator, the family x severity cell it targets, the text and the prompt
    sdxl     make the sdxl rows on a CUDA GPU -> data/real/images/<id>.png (needs diffusers)
    api      make the chatgpt and gemini rows through their APIs (keys in the shell, never in
             a file) -> data/real/images/<id>.<ext>
    intake   log images made by hand (a prompt an API refused) and list what is still missing,
             with the prompt to paste
    select   after real.py localize: keep whole images, cell by cell, until each cell holds
             its quota of crops -> crops.csv (the full pool stays in crops_all.csv)
             and selection.json

The family and severity in the plan are what the prompt asks for, not what the generator
delivers; the experts' labels measure what came out. Selection reads only the plan, never
a model output, so the quota cannot favor crops the model finds easy. Crops from one
image share a style and a generator, so resample images, not crops, for confidence intervals.

    python src/data/generate_real.py plan
    python src/data/generate_real.py sdxl            # free Colab or Kaggle T4
    python src/data/generate_real.py api --openai-model <id> --gemini-model <id> --limit 1
    python src/data/generate_real.py intake
    python src/data/generate_real.py select
    python src/data/generate_real.py --check
"""

import argparse
import base64
import csv
import hashlib
import json
import math
import os
import random
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL = ROOT / "data/real"
IMAGES, PLAN, PROMPTS = REAL / "images", REAL / "plan.csv", REAL / "prompts.csv"
CROPS, POOL, SELECTION = REAL / "crops.csv", REAL / "crops_all.csv", REAL / "selection.json"
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
MIN_SIDE = 512  # a smaller image cannot hold readable text

FAMILIES = ["serif", "sans-serif", "display", "monospace"]
SEVERITIES = ["mild", "moderate", "severe"]
MANUAL = ["gemini", "chatgpt"]  # bing was dropped: no public API, and the paper does not need a third closed tool
GENERATORS = {  # plan name -> what prompts.csv records
    "sdxl": "sdxl-base-1.0",
    "gemini": "gemini",
    "chatgpt": "chatgpt-image",
}
SDXL = "stabilityai/stable-diffusion-xl-base-1.0"
NEGATIVE = "blurry, low resolution"  # nothing that suppresses garbled text: that is the signal
PLAN_FIELDS = ["image_id", "generator", "plan_id", "family", "severity", "scene", "text",
               "prompt", "seed", "width", "height"]
PROMPT_FIELDS = ["image", "generator", "prompt", "date", "plan_id", "seed"]

# Difficulty is what the prompt asks for: short common words on a plain ground (mild),
# several words on a sign or box (moderate), long, rare or invented words on curved,
# small or crowded surfaces (severe). Fictional names only, so no real brand or logo
# appears and no tool refuses the prompt. 24 texts per severity covers 4 families x 5 prompts.
TEXTS = {
    "mild": [
        "BAKERY", "Sunrise Coffee", "OPEN", "Fresh Bread", "Welcome Home", "Summer Sale",
        "Good Morning", "Daily Special", "Happy Birthday", "Book Club", "Ice Cream", "Pizza Night",
        "Garden Party", "Wild Flowers", "Night Market", "Blue Moon", "Hot Tea", "Pet Shop",
        "City Bikes", "Fish Market", "Sweet Dreams", "Free Wifi", "Live Music", "Grand Opening",
    ],
    "moderate": [
        "Midnight Orchid Perfumery", "Handcrafted Ceramics Studio", "Ridgeway Hardware and Supply",
        "Quarterly Growth Report", "Lantern Street Night Bazaar", "Harborview Seafood Kitchen",
        "Maple Hollow Farm Stand", "The Velvet Anchor Tavern", "Copperleaf Tea Merchants",
        "Northwind Cycle Repair", "Silver Fern Yoga Studio", "Juniper and Sage Apothecary",
        "Old Mill Bread Company", "Starlight Drive-In Cinema", "Granite Peak Climbing Gym",
        "Bluebird Children's Library", "Saffron Road Spice House", "Driftwood Surf School",
        "Marigold Lane Florist", "Ironbridge Coffee Roasters", "Cobalt Sky Observatory",
        "Tidewater Boat Rentals", "Willow Creek Candle Works", "Evergreen Dental Care",
    ],
    "severe": [
        "Quixotic Zephyr Brewing Company", "Glorbix Snaffle Trading Co.",
        "Pharmaceutical Compounding Laboratory Est. 1987", "Cinnamon Marmalade Preservation Cooperative",
        "Interdisciplinary Metallurgical Symposium 2026", "Frumious Bandersnatch Taxidermy",
        "Mnemonic Cartography Society", "Extraordinarily Delicious Dumpling House",
        "Thaddeus Wimbledon-Featherstonehaugh", "Ptarmigan Quetzal Cartographers",
        "Archaeological Preservation and Heritage Trust", "Bioluminescent Fungi Cultivation Institute",
        "Zymurgy and Fermentation Sciences Guild", "Rhododendron Conservatory Visitor Information",
        "Sesquipedalian Linguistics Review", "Crepuscular Wanderings: A Field Guide",
        "Unprecedented Clearance Event, All Departments", "Krakatoa Volcanology Research Station",
        "Chrysanthemum Horticultural Exhibition", "Whimsical Contraptions Repair and Restoration",
        "Phosphorescent Plankton Observation Deck", "Vermicelli Noodle Manufacturing Association",
        "Marionette Theatre Costume Workshop", "Quarantine Station Historical Museum",
    ],
}
SCENES = {
    "mild": ["a clean graphic poster with a plain background", "a minimalist greeting card",
             "a flat-lay product label on a white table", "a simple storefront window decal"],
    "moderate": ["a shop sign above a doorway", "a product packaging box",
                 "a printed menu board on a wall", "a banner stretched across a street"],
    "severe": ["a curved ceramic mug", "a row of book spines on a shelf",
               "a chalkboard menu with several lines of small writing", "a neon sign on a brick wall",
               "a glass bottle label with small print", "an embroidered patch on denim",
               "a vintage tin can label with several text blocks", "a stack of wooden crates"],
}
WIDE = {"a simple storefront window decal", "a shop sign above a doorway", "a banner stretched across a street",
        "a row of book spines on a shelf", "a neon sign on a brick wall"}  # 1344x768; the rest 1024x1024
STYLES = {
    "serif": ["elegant high-contrast serif lettering", "classic old-style serif typeface",
              "bookish transitional serif lettering"],
    "sans-serif": ["clean modern sans-serif lettering", "bold geometric sans-serif typeface",
                   "neutral grotesque sans-serif lettering"],
    "display": ["bold condensed poster display lettering", "playful rounded display lettering",
                "retro script display lettering", "heavy slab display lettering"],
    "monospace": ["monospaced typewriter-style lettering", "code-editor monospace typeface",
                  "terminal-style monospace lettering"],
}


# ------------------------------------------------------------------ csv helpers ---

def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def ensure_prompts(path=PROMPTS):
    """prompts.csv with the current header. The committed file holds only the old four-column one."""
    path = Path(path)
    rows = read_csv(path) if path.exists() and path.stat().st_size else []
    if not rows:
        write_csv(path, PROMPT_FIELDS, [])
    else:
        assert list(rows[0]) == PROMPT_FIELDS, f"{path.name} has rows under an old header; add the missing columns by hand"


def append_prompts(rows, path=PROMPTS):
    with Path(path).open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=PROMPT_FIELDS).writerows(rows)


def prompt_row(path, plan_row, day=None, label=None):
    path = Path(path)
    day = day or (date.fromtimestamp(path.stat().st_mtime) if path.exists() else date.today()).isoformat()
    return {"image": path.name, "generator": label or GENERATORS[plan_row["generator"]], "prompt": plan_row["prompt"],
            "date": day, "plan_id": plan_row["plan_id"], "seed": plan_row["seed"]}


# ------------------------------------------------------------------------ plan ---

def build_plan(per_cell=5, manual_per_cell=2, seed=2026, manual_tools=MANUAL, with_sdxl=True):
    """One row per image to make. Every prompt gets an sdxl image; the first manual_per_cell
    prompts of each cell also go to a closed tool, rotating through manual_tools, so those
    prompts are paired across generators. Ids are opaque and shuffled: a rater who sees a
    crop id learns neither the generator nor the cell."""
    rng = random.Random(seed)
    need = per_cell * len(FAMILIES)
    texts = {}
    for sev in SEVERITIES:
        assert need <= len(TEXTS[sev]), f"--per-cell {per_cell} needs {need} {sev} texts, have {len(TEXTS[sev])}"
        texts[sev] = rng.sample(TEXTS[sev], need)
    prompts = []
    for sev in SEVERITIES:
        for fam in FAMILIES:
            for i in range(per_cell):
                text, scene, style = texts[sev].pop(), rng.choice(SCENES[sev]), rng.choice(STYLES[fam])
                w, h = (1344, 768) if scene in WIDE else (1024, 1024)
                prompts.append({"plan_id": f"p{len(prompts) + 1:03d}", "family": fam, "severity": sev,
                                "scene": scene, "text": text, "seed": rng.randrange(2**31), "width": w,
                                "height": h, "prompt": f'{scene.capitalize()}, showing the exact text "{text}" in {style}.',
                                "_i": i})
    images, tool = [], 0
    for p in prompts:
        if with_sdxl:
            images.append({**p, "generator": "sdxl"})
        if manual_tools and p["_i"] < manual_per_cell:
            images.append({**p, "generator": manual_tools[tool % len(manual_tools)], "seed": ""})
            tool += 1
    rng.shuffle(images)
    for n, r in enumerate(images, 1):
        r["image_id"] = f"r{n:03d}"
    return sorted(({k: r[k] for k in PLAN_FIELDS} for r in images), key=lambda r: r["image_id"])


def plan(args):
    assert not (IMAGES.exists() and any(IMAGES.iterdir())), \
        "images already exist; a new plan would no longer match their ids. Move them away first."
    rows = build_plan(args.per_cell, args.manual_per_cell, args.seed, [] if args.manual_per_cell == 0 else MANUAL,
                      not args.no_sdxl)
    write_csv(PLAN, PLAN_FIELDS, rows)
    by_gen = Counter(r["generator"] for r in rows)
    print(f"{len(rows)} images -> {PLAN.relative_to(ROOT)}: " + ", ".join(f"{g} {n}" for g, n in sorted(by_gen.items())))
    print("Read the prompts, then commit plan.csv before running sdxl on Colab.")


# ----------------------------------------------------------------------- sdxl ---

def sdxl(args):
    import torch
    from diffusers import StableDiffusionXLPipeline
    assert torch.cuda.is_available(), "sdxl needs a CUDA GPU; a free Colab or Kaggle T4 works"
    IMAGES.mkdir(parents=True, exist_ok=True)
    todo = [r for r in read_csv(PLAN) if r["generator"] == "sdxl" and not (IMAGES / f"{r['image_id']}.png").exists()]
    todo = todo[:args.limit] if args.limit else todo
    assert todo, "nothing to do: every sdxl image already exists"
    pipe = StableDiffusionXLPipeline.from_pretrained(SDXL, torch_dtype=torch.float16, variant="fp16",
                                                     use_safetensors=True)
    pipe.enable_model_cpu_offload() if args.offload else pipe.to("cuda")
    ensure_prompts()
    for k, r in enumerate(todo, 1):
        img = pipe(prompt=r["prompt"], negative_prompt=NEGATIVE, width=int(r["width"]), height=int(r["height"]),
                   num_inference_steps=args.steps, guidance_scale=args.guidance,
                   generator=torch.Generator("cuda").manual_seed(int(r["seed"]))).images[0]
        path = IMAGES / f"{r['image_id']}.png"
        img.save(path)
        append_prompts([prompt_row(path, r)])  # logged as it goes, so a crash loses nothing
        print(f"{k}/{len(todo)} {path.name}", file=sys.stderr)


# ------------------------------------------------------------------------- api ---

API_TOOLS = ["chatgpt", "gemini"]  # the closed tools, both through a public image API
EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def http_json(url, headers, body, tries=3):
    import time
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", **headers})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and k < tries - 1:
                time.sleep(30)  # rate limit or busy: wait and retry the same prompt
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")


def parse_openai(d):
    return base64.b64decode(d["data"][0]["b64_json"]), ".png"


def parse_gemini(d):
    """The last image part that is not a "thought": thinking models send interim drafts first."""
    parts = ((d.get("candidates") or [{}])[0].get("content") or {}).get("parts", [])
    blobs = [part.get("inlineData") or part.get("inline_data") for part in parts if not part.get("thought")]
    blobs = [b for b in blobs if b]
    if not blobs:
        raise RuntimeError("no image in the reply (refused or blocked): " + json.dumps(d)[:200])
    b = blobs[-1]
    return base64.b64decode(b["data"]), EXT.get(b.get("mimeType") or b.get("mime_type"), ".png")


def openai_image(row, key, model, quality):
    wide = int(row["width"]) > int(row["height"])
    return parse_openai(http_json("https://api.openai.com/v1/images/generations", {"Authorization": f"Bearer {key}"},
                                  {"model": model, "prompt": row["prompt"], "quality": quality, "n": 1,
                                   "size": "1536x1024" if wide else "1024x1024"}))


def gemini_image(row, key, model):
    wide = int(row["width"]) > int(row["height"])
    return parse_gemini(http_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                  {"x-goog-api-key": key},
                                  {"contents": [{"parts": [{"text": row["prompt"]}]}],
                                   "generationConfig": {"responseModalities": ["IMAGE"],
                                                        "imageConfig": {"aspectRatio": "16:9" if wide else "1:1"}}}))


def api(args):
    """One request per prompt, first output kept: no retries for a better image, no prompt edits."""
    keys = {"chatgpt": os.environ.get("OPENAI_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")}
    models = {"chatgpt": args.openai_model, "gemini": args.gemini_model}
    tools = [args.only] if args.only else API_TOOLS
    for t in tools:
        assert keys[t], f"set {'OPENAI_API_KEY' if t == 'chatgpt' else 'GEMINI_API_KEY'} in the shell first (never in a file)"
        assert models[t], f"give --{'openai' if t == 'chatgpt' else 'gemini'}-model (see data/real/README.md)"
    have = {p.stem for p in IMAGES.glob("*")} if IMAGES.exists() else set()
    todo = [r for r in read_csv(PLAN) if r["generator"] in tools and r["image_id"] not in have][:args.limit]
    assert todo, "nothing to do: every api image already exists"
    IMAGES.mkdir(parents=True, exist_ok=True)
    ensure_prompts()
    failed = []
    for k, r in enumerate(todo, 1):
        t = r["generator"]
        try:
            data, ext = (openai_image(r, keys[t], models[t], args.quality) if t == "chatgpt"
                         else gemini_image(r, keys[t], models[t]))
        except (RuntimeError, OSError) as e:
            if str(e).startswith(("HTTP 401", "HTTP 403")):
                sys.exit(f"stopped: {e}")  # a bad key or an unverified account fails every call
            failed.append(r["image_id"])
            print(f"{k}/{len(todo)} {r['image_id']} FAILED: {e}", file=sys.stderr)
            continue
        path = IMAGES / f"{r['image_id']}{ext}"
        path.write_bytes(data)
        append_prompts([prompt_row(path, r, label=models[t] + (f" quality={args.quality}" if t == "chatgpt" else ""))])
        print(f"{k}/{len(todo)} {path.name} ({t})", file=sys.stderr)
    if failed:
        print(f"\nfailed {failed}: run api again to retry, or make them by hand (intake lists them)")


# --------------------------------------------------------------------- intake ---

def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except ImportError:
        return (0, 0)  # no Pillow: skip the size check


def intake(args):
    plan_rows = {r["image_id"]: r for r in read_csv(PLAN)}
    ensure_prompts()
    logged = {Path(r["image"]).stem for r in read_csv(PROMPTS)}
    files = {p.stem: p for p in sorted(IMAGES.glob("*")) if p.suffix.lower() in IMAGE_TYPES} if IMAGES.exists() else {}
    stray = sorted(set(files) - set(plan_rows))
    assert not stray, f"not in plan.csv: {stray}. Save each hand-made image as its image_id, e.g. r012.png"
    fresh = [files[i] for i in sorted(files) if i not in logged]
    seen, dupes, small = {}, [], []
    for p in fresh:
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if digest in seen:
            dupes.append((p.name, seen[digest]))
        seen[digest] = p.name
        w, h = image_size(p)
        if w and min(w, h) < MIN_SIDE:
            small.append(p.name)
    append_prompts([prompt_row(p, plan_rows[p.stem]) for p in fresh])
    print(f"logged {len(fresh)} new images -> {PROMPTS.relative_to(ROOT)}")
    for what, items in (("identical images", dupes), (f"under {MIN_SIDE}px", small)):
        if items:
            print(f"warning, {what}: {items}")
    for g in GENERATORS:
        ids = [i for i, r in plan_rows.items() if r["generator"] == g]
        print(f"{g:8s} {sum(i in files for i in ids):3d}/{len(ids)} made")
    todo = [r for i, r in sorted(plan_rows.items()) if r["generator"] != "sdxl" and i not in files]
    if todo:
        print(f"\nstill to make by hand ({len(todo)}): save each as <id>.png in {IMAGES.relative_to(ROOT)}")
        for r in todo:
            print(f"  {r['image_id']}  {r['generator']:8s} {r['prompt']}")


# --------------------------------------------------------------------- select ---

def interleave(groups, start):
    """One item from each group in turn, beginning at group number `start`."""
    names = sorted(groups)
    names = names[start % len(names):] + names[:start % len(names)]
    queues, out = {n: list(groups[n]) for n in names}, []
    while any(queues.values()):
        out += [queues[n].pop(0) for n in names if queues[n]]
    return out


def choose_crops(crops, plan_rows, n=100, seed=2026, cap=6):
    """Keep whole images, cell by cell, until each family x severity cell holds its quota of
    crops, taking turns between generators so none dominates (Section 4.3.1). At most `cap`
    boxes stay per image (a fixed-seed sample), so a sign that repeats its text, or an image
    with many boxes, cannot fill a cell alone. Reads only the plan."""
    cells = [(f, s) for s in SEVERITIES for f in FAMILIES]
    quota = math.ceil(n / len(cells))
    by_image = defaultdict(list)
    for c in crops:
        by_image[Path(c["image"]).stem].append(c)
    stray = sorted(set(by_image) - set(plan_rows))
    assert not stray, f"crops from images that are not in plan.csv: {stray}"
    capped = {}
    for i, cs in by_image.items():
        capped[i] = max(0, len(cs) - cap)
        if capped[i]:
            by_image[i] = random.Random(f"{seed}-{i}").sample(sorted(cs, key=lambda c: c["crop_id"]), cap)
    rng, chosen, report = random.Random(seed), [], {}
    extra = set(rng.sample(range(len(cells)), n % len(cells)))  # cells that take one more crop so the total is exactly n
    target = [n // len(cells) + (k in extra) for k in range(len(cells))]
    for k, (fam, sev) in enumerate(cells):
        groups = defaultdict(list)
        for i in sorted(by_image):
            if (plan_rows[i]["family"], plan_rows[i]["severity"]) == (fam, sev):
                groups[plan_rows[i]["generator"]].append(i)
        for g in groups.values():
            rng.shuffle(g)
        got, picked = 0, []
        for i in interleave(groups, k):
            if got >= quota:
                break
            picked.append(i)
            got += len(by_image[i])
        keep = {i: list(by_image[i]) for i in picked}
        while sum(map(len, keep.values())) > target[k]:  # trim to the cell's exact share: the fullest image gives one up
            big = max(len(v) for v in keep.values())
            i = rng.choice(sorted(i for i, v in keep.items() if len(v) == big))
            keep[i].pop(rng.randrange(len(keep[i])))
        kept = sum(map(len, keep.values()))
        chosen += [c for v in keep.values() for c in v]
        report[f"{fam}|{sev}"] = {"quota": target[k], "crops": kept, "images": picked, "shortfall": max(0, target[k] - kept),
                                  "capped": sum(capped[i] for i in picked), "trimmed": got - kept}
    return sorted(chosen, key=lambda c: c["crop_id"]), report


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select(args):
    plan_rows = {r["image_id"]: r for r in read_csv(PLAN)}
    ours = SELECTION.exists() and json.loads(SELECTION.read_text())["crops_sha256"] == sha(CROPS)
    if not ours:  # crops.csv came straight from real.py localize: it is the full pool
        shutil.copyfile(CROPS, POOL)
    pool = read_csv(POOL)
    usable = [c for c in pool if int(c["y1"]) - int(c["y0"]) >= args.min_height]  # a rule on size, set before labeling
    chosen, report = choose_crops(usable, plan_rows, args.n, args.seed, args.max_per_image)
    write_csv(CROPS, list(pool[0]), chosen)
    gen = Counter(plan_rows[Path(c["image"]).stem]["generator"] for c in chosen)
    SELECTION.write_text(json.dumps({"target": args.n, "seed": args.seed, "max_per_image": args.max_per_image, "min_height": args.min_height,
                                     "too_small": len(pool) - len(usable), "selected": len(chosen),
                                     "by_generator": dict(gen), "cells": report,
                                     "crops_sha256": sha(CROPS)}, indent=2) + "\n")
    print(f"{len(pool) - len(usable)} of {len(pool)} boxes under {args.min_height} px high left out (too small to show a typeface)")
    print(f"{len(chosen)} of {len(usable)} crops selected (target {args.n}) -> {CROPS.relative_to(ROOT)}; "
          f"full pool kept in {POOL.name}")
    for cell, r in report.items():
        print(f"  {cell:20s} {r['crops']:3d}/{r['quota']} crops from {len(r['images'])} images"
              + (f"  SHORT by {r['shortfall']}" if r["shortfall"] else "")
              + (f"  ({r['capped']} boxes over the per-image cap left out)" if r["capped"] else "")
              + (f"  ({r['trimmed']} trimmed to the exact share)" if r["trimmed"] else ""))
    print("by generator: " + ", ".join(f"{g} {n}" for g, n in sorted(gen.items())))
    print("Next: check the crops, delete boxes that are not text (note what and why), then real.py sheet.")


# ---------------------------------------------------------------------- check ---

def check():
    a = build_plan(seed=1)
    assert a == build_plan(seed=1) and a != build_plan(seed=2), "the plan is not seeded"
    sd = [r for r in a if r["generator"] == "sdxl"]
    cells = Counter((r["family"], r["severity"]) for r in sd)
    assert len(cells) == 12 and set(cells.values()) == {5}, cells
    ids = [r["image_id"] for r in a]
    assert ids == sorted(ids) and len(set(ids)) == len(ids) and ids[0] == "r001", "ids are not opaque and unique"
    assert len({r["text"] for r in sd}) == len(sd), "a text repeats"
    tools = Counter(r["generator"] for r in a if r["generator"] != "sdxl")
    assert sum(tools.values()) == 24 and max(tools.values()) - min(tools.values()) <= 1, tools
    assert {r["plan_id"] for r in a if r["generator"] != "sdxl"} <= {r["plan_id"] for r in sd}, "a manual prompt has no sdxl twin"
    assert all(1000 <= int(r["width"]) <= 1344 for r in a)
    # selection: quota met in every cell, deterministic, more than one generator
    plan_rows = {r["image_id"]: r for r in a}
    crops = [{"crop_id": f"{i}_{k:02d}", "image": f"{i}.png"} for i in plan_rows for k in range(3)]
    chosen, rep = choose_crops(crops, plan_rows, n=36, seed=1)
    assert all(v["crops"] >= v["quota"] for v in rep.values()), rep
    assert len(choose_crops(crops, plan_rows, n=100, seed=1)[0]) == 100, "the selection is not exactly n crops"
    assert chosen == choose_crops(crops, plan_rows, n=36, seed=1)[0], "selection is not seeded"
    busy = a[0]["image_id"]
    more = crops + [{"crop_id": f"{busy}_{k:02d}", "image": f"{busy}.png"} for k in range(3, 23)]
    chosen2, rep2 = choose_crops(more, plan_rows, n=1200, seed=1, cap=6)  # a big quota picks every image
    assert sum(c["image"] == f"{busy}.png" for c in chosen2) == 6, "the per-image cap did not hold"
    assert chosen2 == choose_crops(more, plan_rows, n=1200, seed=1, cap=6)[0], "the cap is not seeded"
    assert any(v["capped"] for v in rep2.values()), "the cap left nothing out"
    assert len(Counter(plan_rows[c["image"][:-4]]["generator"] for c in chosen)) > 1, "one generator dominates"
    # prompts.csv: old four-column header is upgraded; rows round-trip
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "prompts.csv"
        p.write_text("image,generator,prompt,date\n")
        ensure_prompts(p)
        append_prompts([prompt_row(Path("r001.png"), a[0], "2026-01-01")], p)
        row = read_csv(p)[0]
        assert row["image"] == "r001.png" and row["generator"] == GENERATORS[a[0]["generator"]], row
    # api replies: both shapes parse, a reply with no image is an error, not a blank file
    png = b"\x89PNG-test"
    b64 = base64.b64encode(png).decode()
    assert parse_openai({"data": [{"b64_json": b64}]}) == (png, ".png")
    assert parse_gemini({"candidates": [{"content": {"parts": [{"text": "hi"}, {"inlineData": {"mimeType": "image/jpeg", "data": b64}}]}}]}) == (png, ".jpg")
    draft = {"thought": True, "inlineData": {"mimeType": "image/png", "data": base64.b64encode(b"draft").decode()}}
    assert parse_gemini({"candidates": [{"content": {"parts": [draft, {"inlineData": {"mimeType": "image/png", "data": b64}}]}}]}) == (png, ".png"), "kept an interim thought image"
    try:
        parse_gemini({"candidates": [{"finishReason": "SAFETY"}]})
        raise AssertionError("a reply without an image was accepted")
    except RuntimeError:
        pass
    print("ok: plan, selection, prompt log and api parsers passed all checks")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("step", nargs="?", choices=["plan", "sdxl", "api", "intake", "select"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--per-cell", type=int, default=5, help="plan: prompts per family x severity cell")
    ap.add_argument("--manual-per-cell", type=int, default=2, help="plan: prompts per cell also made by hand (0 = none)")
    ap.add_argument("--no-sdxl", action="store_true", help="plan: leave the open-weight model out")
    ap.add_argument("--n", type=int, default=100, help="select: evaluation crops to aim for (Section 4.3.1)")
    ap.add_argument("--limit", type=int, help="sdxl, api: stop after this many images")
    ap.add_argument("--steps", type=int, default=30, help="sdxl: denoising steps")
    ap.add_argument("--guidance", type=float, default=7.5, help="sdxl: guidance scale")
    ap.add_argument("--offload", action="store_true", help="sdxl: CPU offload for GPUs under 12 GB (slower)")
    ap.add_argument("--max-per-image", type=int, default=6, help="select: most crops kept from one image")
    ap.add_argument("--min-height", type=int, default=24, help="select: smallest crop height in px (with margin) a rater can judge")
    ap.add_argument("--only", choices=API_TOOLS, help="api: one tool only")
    ap.add_argument("--openai-model", help="api: OpenAI image model id (list with the curl in data/real/README.md)")
    ap.add_argument("--gemini-model", help="api: Gemini image model id")
    ap.add_argument("--quality", default="medium", help="api: OpenAI quality (low, medium, high)")
    args = ap.parse_args()
    if args.check:
        return check()
    if not args.step:
        ap.error("give a step: plan, sdxl, api, intake or select")
    {"plan": plan, "sdxl": sdxl, "api": api, "intake": intake, "select": select}[args.step](args)


if __name__ == "__main__":
    main()
