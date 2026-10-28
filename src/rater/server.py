"""Backend server and CLI for the Expert-Panel Rating Form (Section 4.2.3, Appendix B).

Each rater has one secret link (`/r/<token>`). The server derives the rater id from the
token, so a client can neither choose nor change it; every answer, with the time spent on it,
goes into a hash-chained audit log; finishing locks the rater's answers and returns a receipt
(the SHA-256 of the label set) that the rater confirms from the mailbox that got the link.
About a tenth of the items are hidden controls (repeats and clean reference renders).

Serves (all but the palette, fonts and the frontend need the rater's cookie, and consent):
  - GET  /r/<token>                    -> sets the cookie, logs the visit, redirects to /
  - GET  /api/me                       -> {rater, consented, receipt, consent_text, consent_sha}
  - POST /api/consent                  -> records the attestation (bound to the exact text)
  - GET  /api/crops                    -> the rater's items: the evaluation crops plus controls, in
                                          an order that is fixed per rater
  - GET  /api/labels                   -> the rater's own answers only (blind protocol)
  - POST /api/labels                   -> saves answers as the rater the cookie names; ignores any
                                          `rater` in the body; refused after finishing
  - POST /api/finish                   -> locks the answers, returns the receipt
  - GET  /data/real/crops/<id>.png     -> only the crops that rater is served
  - GET  /api/palette, /fonts/*.ttf    -> the 80 Google Fonts (public data)
  - GET  /*                            -> built React frontend from src/rater/dist/

Commands (Ch4 §4.2.3):
    .venv/bin/python src/rater/server.py tokens --base-url https://<tunnel>   # once: prints the 3 links
    .venv/bin/python src/rater/server.py controls                            # once: builds the hidden controls
    .venv/bin/python src/rater/server.py                                     # serve on 127.0.0.1:8000
    .venv/bin/python src/rater/server.py verify                              # audit chain, receipts, data quality
    .venv/bin/python src/rater/server.py --check                             # self-tests
"""

import argparse
import csv
import hashlib
import io
import json
import mimetypes
import os
import random
import secrets
import shutil
import statistics
import sys
import threading
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/data"))

import render_corpus as rc  # noqa: E402
import render_mixed as rm  # noqa: E402

PALETTE_CSV = ROOT / "data/palette.csv"
UNKNOWN_CSV = ROOT / "data/unknown.csv"
REAL_DIR = ROOT / "data/real"
CROPS_CSV = REAL_DIR / "crops.csv"
LABELS_CSV = REAL_DIR / "labels.csv"
CORPUS_META = ROOT / "data/corpus/metadata.csv"
CORPUS_UNKNOWN_META = ROOT / "data/corpus_unknown/metadata.csv"
CORPUS_MIXED_META = ROOT / "data/corpus_mixed/metadata.csv"
DATASET_CACHE_DIR = REAL_DIR / "crops" / "dataset_cache"
FONTS_DIR = ROOT / "data/fonts"
DIST_DIR = Path(__file__).resolve().parent / "dist"

LABEL_FIELDS = ["crop_id", "rater", "font", "coherence"]
VALID_RATERS = {"r1", "r2", "r3"}
VALID_COHERENCE = {"one", "two", "cannot_tell"}

_FONT_CACHE = {}
_DATASET_SPECS = None


def _get_pil_font(ttf_rel_path: str):
    if ttf_rel_path not in _FONT_CACHE:
        _FONT_CACHE[ttf_rel_path] = ImageFont.truetype(str(ROOT / ttf_rel_path), rc.EM)
    return _FONT_CACHE[ttf_rel_path]


def load_palette(palette_csv=PALETTE_CSV):
    rows = list(csv.DictReader(palette_csv.open(encoding="utf-8")))
    return [
        {
            "font_id": r["font_id"],
            "family": r["family"],
            "weight": r["weight"],
            "family_class": r["family_class"],
            "popularity": int(r["popularity"]),
            "ttf_url": f"/fonts/{Path(r['ttf_path']).name}",
        }
        for r in rows
    ]


def _peek_single_meta(seed: int):
    """Extract deterministic word_text and degradation tier without rasterizing."""
    rng = np.random.default_rng(seed)
    tier = str(rng.choice(list(rc.TIERS), p=rc.TIER_WEIGHTS))
    lo, hi = rc.TIERS[tier]
    _ = rng.uniform(lo, hi, 3) if hi > 0 else np.zeros(3)
    words, _ = rc.sample_text(rng)
    return " ".join(words), tier


def _peek_mixed_meta(seed: int):
    """Extract deterministic mixed-crop word_text and tier without rasterizing."""
    rng = np.random.default_rng(seed)
    tier = str(rng.choice(list(rc.TIERS), p=rc.TIER_WEIGHTS))
    lo, hi = rc.TIERS[tier]
    _ = rng.uniform(lo, hi, 3) if hi > 0 else np.zeros(3)
    _, text, _ = rm.sample_mix(rng)
    return text, tier


def build_dataset_specs(master_seed=2026):
    """Build a deterministic 100-crop stratified set from the thesis dataset pipeline:
      - 70 known-palette single-font crops (data/palette.csv via render_corpus.py)
      - 15 held-out unknown single-font crops (data/unknown.csv via render_corpus.py)
      - 15 two-font mixed crops (data/palette.csv pairs via render_mixed.py)
    Ground-truth font and coherence labels remain strictly server-side so the
    client payload stays 100% blind (Section 4.2.3).
    """
    global _DATASET_SPECS
    if _DATASET_SPECS is not None:
        return _DATASET_SPECS

    palette_rows = list(csv.DictReader(PALETTE_CSV.open(encoding="utf-8")))
    unknown_rows = list(csv.DictReader(UNKNOWN_CSV.open(encoding="utf-8"))) if UNKNOWN_CSV.exists() else palette_rows[:20]

    raw_items = []
    # 70 known palette crops across distinct fonts
    for i in range(70):
        prow = palette_rows[i % len(palette_rows)]
        seed = rc.crop_seed(master_seed, prow["font_id"], i + 100)
        word_text, tier = _peek_single_meta(seed)
        raw_items.append(
            {
                "kind": "known",
                "seed": seed,
                "font_row": prow,
                "ocr_text": word_text,
                "tier": tier,
            }
        )

    # 15 held-out unknown font crops
    for i in range(15):
        urow = unknown_rows[i % len(unknown_rows)]
        seed = rc.crop_seed(master_seed, f"unk_{urow['font_id']}", i + 200)
        word_text, tier = _peek_single_meta(seed)
        raw_items.append(
            {
                "kind": "unknown",
                "seed": seed,
                "font_row": urow,
                "ocr_text": word_text,
                "tier": tier,
            }
        )

    # 15 mixed two-typeface crops
    for i in range(15):
        seed = rc.crop_seed(master_seed, "mixed_panel", i + 300)
        pair_rng = np.random.default_rng(seed)
        idx_a, idx_b = pair_rng.choice(len(palette_rows), size=2, replace=False)
        word_text, tier = _peek_mixed_meta(seed)
        raw_items.append(
            {
                "kind": "mixed",
                "seed": seed,
                "font_a": palette_rows[int(idx_a)],
                "font_b": palette_rows[int(idx_b)],
                "ocr_text": word_text,
                "tier": tier,
            }
        )

    # Shuffle deterministically so known, unknown, and mixed crops are interleaved
    order = np.random.default_rng(master_seed).permutation(len(raw_items))
    specs = {}
    for idx, pos in enumerate(order, start=1):
        item = raw_items[int(pos)]
        crop_id = f"crop_{(idx - 1) // 4 + 1:02d}_{(idx - 1) % 4:02d}"
        specs[crop_id] = {
            "index": idx,
            "crop_id": crop_id,
            "image": f"gen_{(idx - 1) // 4 + 1:02d}.png",
            "ocr_text": item["ocr_text"],
            "crop_url": f"/api/crop-image/{crop_id}.png",
            "_internal": item,
        }

    _DATASET_SPECS = specs
    return specs


def render_dataset_crop_png(crop_id: str) -> bytes | None:
    """Render (or read from disk cache) the exact PNG for a dataset crop_id."""
    specs = build_dataset_specs()
    spec = specs.get(crop_id)
    if spec is None:
        return None

    DATASET_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = DATASET_CACHE_DIR / f"{crop_id}.png"
    if cache_file.exists():
        return cache_file.read_bytes()

    info = spec["_internal"]
    if info["kind"] in ("known", "unknown"):
        pil_font = _get_pil_font(info["font_row"]["ttf_path"])
        img, _ = rc.render_one(pil_font, info["seed"])
    else:
        img, _ = rm.render_one(info["font_a"], info["font_b"], info["seed"])

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    cache_file.write_bytes(data)
    return data


def load_crops(crops_csv=CROPS_CSV, source=None):
    """Load crops from:
      1. data/real/crops.csv (if present and source != 'dataset')
      2. data/corpus/metadata.csv (if present on disk and source == 'corpus')
      3. Deterministic synthetic dataset pipeline via render_corpus.py + render_mixed.py
    """
    if source != "dataset" and crops_csv.exists():
        rows = list(csv.DictReader(crops_csv.open(encoding="utf-8")))
        if rows:
            return {
                "mode": "real",
                "source_label": "Real Generative Crops (data/real/crops.csv)",
                "total": len(rows),
                "crops": [
                    {
                        "index": i + 1,
                        "crop_id": r["crop_id"],
                        "image": r.get("image", ""),
                        "ocr_text": r.get("ocr_text", ""),
                        "crop_url": f"/{r['crop_path'].lstrip('/')}",
                    }
                    for i, r in enumerate(rows)
                ],
            }

    if source in (None, "corpus") and CORPUS_META.exists():
        rows = list(csv.DictReader(CORPUS_META.open(encoding="utf-8")))
        test_rows = [r for r in rows if r.get("split") == "test"] or rows
        selected = test_rows[:100]
        if selected:
            return {
                "mode": "corpus",
                "source_label": "Pre-built Synthetic Corpus (data/corpus/metadata.csv)",
                "total": len(selected),
                "crops": [
                    {
                        "index": i + 1,
                        "crop_id": r["image_id"],
                        "image": f"{r['font_id']}.png",
                        "ocr_text": r.get("word_text", ""),
                        "crop_url": f"/{r['image_path'].lstrip('/')}",
                    }
                    for i, r in enumerate(selected)
                ],
            }

    specs = build_dataset_specs()
    public_crops = [
        {
            "index": s["index"],
            "crop_id": s["crop_id"],
            "image": s["image"],
            "ocr_text": s["ocr_text"],
            "crop_url": s["crop_url"],
        }
        for s in specs.values()
    ]
    return {
        "mode": "dataset",
        "source_label": "Synthetic Dataset Pipeline (render_corpus.py + render_mixed.py)",
        "total": len(public_crops),
        "crops": public_crops,
    }


def read_rater_labels(rater, labels_csv=LABELS_CSV):
    """Return ONLY the given rater's rows, enforcing the blind rating protocol."""
    assert rater in VALID_RATERS, f"invalid rater: {rater}"
    if not labels_csv.exists():
        return {}
    out = {}
    with labels_csv.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("rater") == rater and r.get("crop_id"):
                out[r["crop_id"]] = {
                    "crop_id": r["crop_id"],
                    "rater": r["rater"],
                    "font": r["font"],
                    "coherence": r["coherence"],
                }
    return out


def upsert_labels(entries, labels_csv=LABELS_CSV, palette_families=None):
    """Upsert a list of {crop_id, rater, font, coherence} dicts into data/real/labels.csv."""
    if palette_families is None:
        palette = load_palette()
        palette_families = {p["family"] for p in palette} | {p["font_id"] for p in palette} | {"unknown"}

    existing = []
    if labels_csv.exists():
        with labels_csv.open(encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

    by_key = {
        (r["crop_id"], r["rater"]): {k: r[k] for k in LABEL_FIELDS}
        for r in existing
        if "crop_id" in r and "rater" in r
    }

    for item in entries:
        crop_id = str(item.get("crop_id", "")).strip()
        rater = str(item.get("rater", "")).strip()
        font = str(item.get("font", "")).strip()
        coherence = str(item.get("coherence", "")).strip()
        if not crop_id:
            raise ValueError("crop_id is required")
        if rater not in VALID_RATERS:
            raise ValueError(f"rater must be one of {sorted(VALID_RATERS)}")
        if font not in palette_families:
            raise ValueError(f"font must be a palette family/font_id or 'unknown', got {font!r}")
        if coherence not in VALID_COHERENCE:
            raise ValueError(f"coherence must be one of {sorted(VALID_COHERENCE)}")
        by_key[(crop_id, rater)] = {
            "crop_id": crop_id,
            "rater": rater,
            "font": font,
            "coherence": coherence,
        }

    labels_csv.parent.mkdir(parents=True, exist_ok=True)
    tmp = labels_csv.with_suffix(".csv.tmp")
    rows_sorted = [by_key[k] for k in sorted(by_key.keys())]
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LABEL_FIELDS)
        w.writeheader()
        w.writerows(rows_sorted)
    tmp.replace(labels_csv)
    return len(rows_sorted)


# ------------------------------------------------------------------- identity ---

CONSENT_TEXT = (
    "By continuing I confirm that: (1) I am the expert who was invited, and I will rate every item "
    "myself, alone; (2) I will not use AI tools, font-identification services, other people's help or "
    "other raters' answers; (3) my answers, the time I spend on each item, and a scrambled (salted, "
    "one-way) code of my network address and browser are recorded, only to show that the answers are "
    "mine and have not been changed, and my name and address are not stored with them; (4) the form "
    "includes repeated items and clean reference items, used only to check data quality; (5) I can stop "
    "at any time, and my answers will be used in the thesis without my name."
)
CONSENT_SHA = hashlib.sha256(CONSENT_TEXT.encode("utf-8")).hexdigest()
GENESIS = "0" * 64
N_DUP, N_GOLD = 8, 6  # hidden controls: repeated crops, and clean reference renders with a known font
GOLD_CLASSES = ["serif", "sans-serif", "display", "monospace", "serif", "sans-serif"]


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ApiError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Store:
    """Everything that identifies a rater or proves what they did, under one directory.

    raters.private.json   salt + the hash of each rater's token (never the token); not committed
    audit.jsonl           append-only events, each hashed with the one before; only its head is published
    controls.private.json the hidden controls and their ground truth; not committed
    labels.csv            the answers to the evaluation crops (what real.py score reads)
    labels_controls.csv   the answers to the controls, kept apart so the scoring never sees them
    """

    def __init__(self, real_dir=REAL_DIR):
        self.dir = Path(real_dir)
        self.private = self.dir / "raters.private.json"
        self.audit_path = self.dir / "audit.jsonl"
        self.controls_path = self.dir / "controls.private.json"
        self.labels = self.dir / "labels.csv"
        self.labels_controls = self.dir / "labels_controls.csv"
        self.crops_csv = self.dir / "crops.csv"
        self.lock = threading.RLock()

    # tokens ---------------------------------------------------------------------
    def config(self):
        return json.loads(self.private.read_text()) if self.private.exists() else None

    def issue_tokens(self):
        assert not self.private.exists(), f"{self.private.name} exists: delete it to issue new links (the old ones stop working)"
        tokens = {r: secrets.token_urlsafe(18) for r in sorted(VALID_RATERS)}
        self.private.parent.mkdir(parents=True, exist_ok=True)
        self.private.write_text(json.dumps({"salt": secrets.token_hex(16), "tokens": {sha(t): r for r, t in tokens.items()}}))
        self.private.chmod(0o600)
        return tokens

    def rater_for(self, token):
        cfg = self.config()
        return cfg["tokens"].get(sha(token)) if cfg and token else None

    def scramble(self, value):
        return sha(self.config()["salt"] + value)[:16]

    # audit log ------------------------------------------------------------------
    def events(self):
        if not self.audit_path.exists():
            return []
        return [json.loads(line) for line in self.audit_path.read_text(encoding="utf-8").splitlines() if line]

    def head(self):
        ev = self.events()
        return ev[-1]["hash"] if ev else GENESIS

    def log(self, event, rater, ip="", ua="", **fields):
        with self.lock:
            rec = {"t": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "event": event, "rater": rater,
                   "ip_h": self.scramble(ip), "ua_h": self.scramble(ua), **fields}
            prev = self.head()
            rec["prev"] = prev
            rec["hash"] = sha(prev + json.dumps({k: v for k, v in rec.items() if k != "prev"}, sort_keys=True, separators=(",", ":")))
            with self.audit_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            return rec

    def status(self, rater):
        ev = [e for e in self.events() if e["rater"] == rater]
        return {"consented": any(e["event"] == "consent" and e.get("text_sha") == CONSENT_SHA for e in ev),
                "receipt": next((e for e in reversed(ev) if e["event"] == "finish"), None)}

    # items ----------------------------------------------------------------------
    def real_crops(self):
        rows = list(csv.DictReader(self.crops_csv.open(encoding="utf-8")))
        return [{"crop_id": r["crop_id"], "image": r.get("image", ""), "ocr_text": r.get("ocr_text", ""),
                 "crop_url": f"/{r['crop_path'].lstrip('/')}"} for r in rows]

    def controls(self):
        return json.loads(self.controls_path.read_text())["items"] if self.controls_path.exists() else {}

    def served(self, rater):
        """The rater's items: evaluation crops and controls, in an order fixed per rater. Nothing in the
        payload says which are controls."""
        crops = self.real_crops() + [
            {"crop_id": cid, "image": f"{cid.split('_')[0]}.png", "ocr_text": c["ocr_text"], "crop_url": f"/data/real/crops/{cid}.png"}
            for cid, c in self.controls().items()]
        random.Random(sha(self.config()["salt"] + rater)).shuffle(crops)
        return [{**c, "index": i + 1} for i, c in enumerate(crops)]

    def rater_labels(self, rater):
        return {**read_rater_labels(rater, self.labels), **read_rater_labels(rater, self.labels_controls)}

    # answers --------------------------------------------------------------------
    def consent(self, rater, text_sha, ip="", ua=""):
        if text_sha != CONSENT_SHA:
            raise ApiError(400, "the consent text changed: reload the page")
        return self.log("consent", rater, ip, ua, text_sha=CONSENT_SHA)

    def save(self, rater, entries, ip="", ua=""):
        with self.lock:
            st = self.status(rater)
            if not st["consented"]:
                raise ApiError(403, "consent is required before rating")
            if st["receipt"]:
                raise ApiError(409, "already submitted: the answers are locked")
            served = {c["crop_id"] for c in self.served(rater)}
            ctrl = set(self.controls())
            for e in entries:
                if str(e.get("crop_id", "")).strip() not in served:
                    raise ApiError(400, f"not one of your items: {e.get('crop_id')!r}")
            for path, group in ((self.labels, [e for e in entries if e["crop_id"] not in ctrl]),
                                (self.labels_controls, [e for e in entries if e["crop_id"] in ctrl])):
                if group:
                    try:
                        upsert_labels([{**e, "rater": rater} for e in group], labels_csv=path)  # the cookie decides who
                    except ValueError as exc:
                        raise ApiError(400, str(exc))
            for e in entries:
                ms = e.get("ms")
                self.log("save", rater, ip, ua, crop_id=e["crop_id"], ans=sha(f"{e['font']}|{e['coherence']}")[:16],
                         ms=min(max(int(ms), 0), 3_600_000) if isinstance(ms, (int, float)) else None)
            return len(entries)

    def label_set_sha(self, rater):
        rows = self.rater_labels(rater)
        return sha(json.dumps(sorted([cid, r["font"], r["coherence"]] for cid, r in rows.items())))

    def finish(self, rater, ip="", ua=""):
        with self.lock:
            st = self.status(rater)
            if not st["consented"]:
                raise ApiError(403, "consent is required before rating")
            if st["receipt"]:
                return self.receipt(st["receipt"])
            missing = {c["crop_id"] for c in self.served(rater)} - set(self.rater_labels(rater))
            if missing:
                raise ApiError(409, f"{len(missing)} items are still unanswered")
            rec = self.log("finish", rater, ip, ua, rows=len(self.rater_labels(rater)), set_sha=self.label_set_sha(rater))
            return self.receipt(rec)

    @staticmethod
    def receipt(rec):
        return {"rater": rec["rater"], "rows": rec["rows"], "finished_at": rec["t"], "label_set_sha256": rec["set_sha"],
                "audit_hash": rec["hash"]}

    # controls -------------------------------------------------------------------
    def build_controls(self, seed=2026, n_dup=N_DUP, n_gold=N_GOLD):
        assert not self.controls_path.exists(), f"{self.controls_path.name} exists: controls must not change once raters start"
        rng = random.Random(seed)
        real = self.real_crops()
        palette = list(csv.DictReader(PALETTE_CSV.open(encoding="utf-8")))
        n, items = 85, {}  # ids continue past the plan's r084, so they never collide with a localized crop
        for orig in rng.sample(real, n_dup):
            cid = f"r{n:03d}_00"
            n += 1
            dest = self.dir / "crops" / f"{cid}.png"
            assert not dest.exists(), dest
            shutil.copyfile(self.dir / "crops" / f"{orig['crop_id']}.png", dest)
            items[cid] = {"kind": "dup", "of": orig["crop_id"], "ocr_text": orig["ocr_text"]}
        used = set()
        for cls in GOLD_CLASSES[:n_gold]:
            pool = sorted((r for r in palette if r["family_class"] == cls and r["family"] not in used), key=lambda r: int(r["popularity"]))[:12]
            row = rng.choice(pool)
            used.add(row["family"])
            font = _get_pil_font(row["ttf_path"])
            for i in range(200):  # the first seed whose render is the pristine tier
                img, meta = rc.render_one(font, rc.crop_seed(seed, row["font_id"], 900 + i))
                if meta["tier"] == "pristine":
                    break
            cid = f"r{n:03d}_00"
            n += 1
            img.save(self.dir / "crops" / f"{cid}.png")
            items[cid] = {"kind": "gold", "font_id": row["font_id"], "family": row["family"], "family_class": cls,
                          "ocr_text": meta["word_text"]}
        self.controls_path.write_text(json.dumps({"seed": seed, "items": items}, indent=1))
        self.controls_path.chmod(0o600)
        return items

    # audit ----------------------------------------------------------------------
    def verify(self):
        ev, prev, bad = self.events(), GENESIS, None
        for k, e in enumerate(ev, 1):
            body = json.dumps({x: v for x, v in e.items() if x not in ("prev", "hash")}, sort_keys=True, separators=(",", ":"))
            if e["prev"] != prev or e["hash"] != sha(prev + body):
                bad = k
                break
            prev = e["hash"]
        palette = load_palette()
        klass = {p["family"]: p["family_class"] for p in palette} | {p["font_id"]: p["family_class"] for p in palette}
        ctrl, out = self.controls(), {}
        for r in sorted(VALID_RATERS):
            mine = [e for e in ev if e["rater"] == r]
            if not mine:
                continue
            labels, fin = self.rater_labels(r), next((e for e in reversed(mine) if e["event"] == "finish"), None)
            ms = [e["ms"] for e in mine if e["event"] == "save" and e.get("ms") is not None]
            dups = [(labels.get(c), labels.get(i["of"])) for c, i in ctrl.items() if i["kind"] == "dup"]
            golds = [(labels.get(c), i) for c, i in ctrl.items() if i["kind"] == "gold"]
            out[r] = {
                "events": len(mine), "first": mine[0]["t"], "last": mine[-1]["t"],
                "devices": len({(e["ip_h"], e["ua_h"]) for e in mine}),
                "consented": self.status(r)["consented"],
                "answered": len(labels), "expected": len(self.served(r)),
                "finished": bool(fin),
                "receipt_matches": bool(fin) and fin["set_sha"] == self.label_set_sha(r),
                "median_seconds_per_item": round(statistics.median(ms) / 1000, 1) if ms else None,
                "items_under_2s": sum(m < 2000 for m in ms),
                "retest_font_same": sum(1 for a, b in dups if a and b and a["font"] == b["font"]),
                "retest_coherence_same": sum(1 for a, b in dups if a and b and a["coherence"] == b["coherence"]),
                "retest_items": len(dups),
                "gold_family_correct": sum(1 for a, i in golds if a and klass.get(a["font"]) == i["family_class"]),
                "gold_exact": sum(1 for a, i in golds if a and a["font"] in (i["family"], i["font_id"])),
                "gold_items": len(golds),
            }
        return {"chain_ok": bad is None, "first_bad_event": bad, "events": len(ev), "head": prev, "raters": out}


def print_report(rep):
    print(f"audit chain: {'intact' if rep['chain_ok'] else 'BROKEN at event ' + str(rep['first_bad_event'])}"
          f" | {rep['events']} events | head {rep['head']}")
    for r, d in rep["raters"].items():
        print(f"\n{r}: consent {'yes' if d['consented'] else 'NO'}, answered {d['answered']}/{d['expected']}, "
              f"{'finished' if d['finished'] else 'not finished'}"
              + (f", receipt {'matches the labels' if d['receipt_matches'] else 'DOES NOT MATCH the labels'}" if d["finished"] else ""))
        print(f"   {d['first']} -> {d['last']} | {d['devices']} device(s) | median {d['median_seconds_per_item']} s per item, "
              f"{d['items_under_2s']} saved in under 2 s")
        print(f"   repeats: same font {d['retest_font_same']}/{d['retest_items']}, same coherence {d['retest_coherence_same']}/{d['retest_items']}"
              f" | clean references: right family {d['gold_family_correct']}/{d['gold_items']}, exact font {d['gold_exact']}/{d['gold_items']}")


# --------------------------------------------------------------------- server ---

class RaterRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # the audit log is the record; the console stays quiet

    @property
    def store(self):
        return self.server.store

    def _send_json(self, status, payload, headers=()):
        body = json.dumps(payload).encode("utf-8")  # same origin only: no CORS headers
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, data: bytes, mime: str, cache: str = "private, max-age=3600"):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        mime, _ = mimetypes.guess_type(str(path))
        if path.suffix.lower() == ".ttf":
            mime = "font/ttf"
        self._send_bytes(path.read_bytes(), mime or "application/octet-stream")

    def _who(self):
        ip = (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
        return ip, self.headers.get("User-Agent", "")

    def _rater(self):
        c = SimpleCookie(self.headers.get("Cookie", "")).get("rt")
        return self.store.rater_for(c.value) if c else None

    def _gate(self, need_consent=True):
        rater = self._rater()
        if not rater:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "open your personal link"})
        elif need_consent and not self.store.status(rater)["consented"]:
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "consent required"})
        else:
            return rater
        return None

    def do_GET(self):
        route = urlparse(self.path).path

        if route.startswith("/r/"):
            token = route.removeprefix("/r/")
            rater = self.store.rater_for(token)
            if not rater:
                self._send_json(HTTPStatus.FORBIDDEN, {"error": "this link is not valid"})
                return
            self.store.log("open", rater, *self._who())
            secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Set-Cookie", f"rt={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000{secure}")
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if route == "/api/palette":
            self._send_json(HTTPStatus.OK, {"fonts": load_palette()})
            return

        if route == "/api/me":
            rater = self._gate(need_consent=False)
            if rater:
                st = self.store.status(rater)
                self._send_json(HTTPStatus.OK, {"rater": rater, "consented": st["consented"],
                                                "receipt": self.store.receipt(st["receipt"]) if st["receipt"] else None,
                                                "consent_text": CONSENT_TEXT, "consent_sha": CONSENT_SHA})
            return

        if route == "/api/crops":
            rater = self._gate()
            if rater:
                crops = self.store.served(rater)
                self._send_json(HTTPStatus.OK, {"mode": "real", "source_label": "Real Generative Crops", "total": len(crops), "crops": crops})
            return

        if route == "/api/labels":
            rater = self._gate()
            if rater:
                self._send_json(HTTPStatus.OK, {"rater": rater, "labels": self.store.rater_labels(rater)})
            return

        if route.startswith("/fonts/"):
            self._send_file(FONTS_DIR / Path(route.removeprefix("/fonts/")).name)
            return

        if route.startswith("/data/real/crops/"):
            rater = self._gate()
            if rater:
                name = Path(route.removeprefix("/data/real/crops/")).name
                if Path(name).stem in {c["crop_id"] for c in self.store.served(rater)}:
                    self._send_file(self.store.dir / "crops" / name)
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        if route.startswith("/api/"):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "unknown endpoint"})
            return

        if DIST_DIR.exists():  # the frontend carries no data, so it is public
            candidate = (DIST_DIR / route.lstrip("/")).resolve()
            if str(candidate).startswith(str(DIST_DIR)) and candidate.is_file():
                self._send_file(candidate)
                return
            if (DIST_DIR / "index.html").is_file():
                self._send_file(DIST_DIR / "index.html")
                return
        self._send_json(HTTPStatus.OK, {"service": "Expert Panel Rating Form: open your personal link"})

    def do_POST(self):
        route = urlparse(self.path).path
        if route not in ("/api/consent", "/api/labels", "/api/finish"):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint"})
            return
        rater = self._gate(need_consent=False)
        if not rater:
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            ip, ua = self._who()
            if route == "/api/consent":
                if payload.get("agree") is not True:
                    raise ApiError(400, "consent was not given")
                self.store.consent(rater, payload.get("text_sha"), ip, ua)
                self._send_json(HTTPStatus.OK, {"ok": True})
            elif route == "/api/labels":
                entries = payload.get("entries") if isinstance(payload, dict) and "entries" in payload else [payload]
                saved = self.store.save(rater, entries, ip, ua)
                self._send_json(HTTPStatus.OK, {"ok": True, "saved": saved})
            else:
                self._send_json(HTTPStatus.OK, {"ok": True, "receipt": self.store.finish(rater, ip, ua)})
        except ApiError as exc:
            self._send_json(exc.code, {"error": str(exc)})
        except Exception as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})


def check():
    """Verify palette loading, real PNG crop rendering, blind rater isolation, real.py score, and the whole
    identity path (token -> cookie -> consent -> answers -> receipt -> audit) against a live server."""
    import http.client
    import tempfile
    from PIL import Image

    sys.path.insert(0, str(ROOT / "src/model"))
    from real import consensus, to_family

    palette = load_palette()
    assert len(palette) == 80, f"expected 80 palette fonts, got {len(palette)}"
    crops_info = load_crops(source="dataset")
    assert crops_info["total"] == 100 and len(crops_info["crops"]) == 100
    first_crop = crops_info["crops"][0]
    assert first_crop["crop_url"].startswith("/api/crop-image/")
    assert "_internal" not in first_crop, "blind protocol violation: internal ground truth leaked"

    # Verify actual PNG rendering via render_corpus.py / render_mixed.py
    png_bytes = render_dataset_crop_png(first_crop["crop_id"])
    assert png_bytes is not None and png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
    im = Image.open(io.BytesIO(png_bytes))
    assert max(im.size) == rc.OUT_MAX and im.mode == "L", (im.size, im.mode)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_csv = Path(tmp) / "labels.csv"
        upsert_labels(
            [
                {"crop_id": "crop_01_00", "rater": "r1", "font": "Open Sans", "coherence": "one"},
                {"crop_id": "crop_01_00", "rater": "r2", "font": "Open Sans", "coherence": "one"},
                {"crop_id": "crop_01_00", "rater": "r3", "font": "unknown", "coherence": "two"},
            ],
            labels_csv=tmp_csv,
        )
        # Blind protocol: r1 query must never return r2 or r3 answers.
        r1_only = read_rater_labels("r1", labels_csv=tmp_csv)
        assert list(r1_only.keys()) == ["crop_01_00"]
        assert r1_only["crop_01_00"]["font"] == "Open Sans"

        # Updating r1's answer overwrites in place without duplicating rows.
        total = upsert_labels(
            [{"crop_id": "crop_01_00", "rater": "r1", "font": "Roboto", "coherence": "one"}],
            labels_csv=tmp_csv,
        )
        assert total == 3
        assert read_rater_labels("r1", labels_csv=tmp_csv)["crop_01_00"]["font"] == "Roboto"

        # Verify schema matches src/model/real.py score expectations.
        rows = list(csv.DictReader(tmp_csv.open(encoding="utf-8")))
        assert list(rows[0].keys()) == ["crop_id", "rater", "font", "coherence"]
        fam_map = {p["family"].lower().replace(" ", ""): p["family"].lower().replace(" ", "") for p in palette}
        assert to_family(rows[1]["font"], fam_map) == "opensans"
        assert consensus([r["coherence"] for r in rows]) == "one"

    # ---- identity path, end to end, on a throwaway directory and a live server -------------------
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "crops").mkdir()
        rows = []
        for k in range(6):
            Image.new("RGB", (80, 30), (k * 30, 90, 200)).save(d / "crops" / f"r001_{k:02d}.png")
            rows.append({"crop_id": f"r001_{k:02d}", "image": "r001.png", "ocr_text": f"w{k}", "crop_path": f"data/real/crops/r001_{k:02d}.png"})
        with (d / "crops.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        store = Store(d)
        assert store.config() is None
        tokens = store.issue_tokens()
        assert "tokens" in store.private.read_text() and all(t not in store.private.read_text() for t in tokens.values()), "a token is stored in the clear"
        try:
            store.issue_tokens()
            raise AssertionError("tokens were reissued over existing ones")
        except AssertionError as exc:
            assert "exists" in str(exc)
        items = store.build_controls(seed=1, n_dup=2, n_gold=2)
        assert sorted(v["kind"] for v in items.values()) == ["dup", "dup", "gold", "gold"]
        assert all((d / "crops" / f"{cid}.png").exists() for cid in items)
        order = {r: [c["crop_id"] for c in store.served(r)] for r in sorted(VALID_RATERS)}
        assert all(len(v) == 10 for v in order.values()) and len({tuple(v) for v in order.values()}) > 1, "order is not per rater"
        assert all(set(c) == {"crop_id", "image", "ocr_text", "crop_url", "index"} for c in store.served("r1")), "a control is marked in the payload"

        server = ThreadingHTTPServer(("127.0.0.1", 0), RaterRequestHandler)
        server.store = store
        threading.Thread(target=server.serve_forever, daemon=True).start()
        port = server.server_address[1]

        def call(method, path, body=None, cookie=None):
            c = http.client.HTTPConnection("127.0.0.1", port)
            h = {"Content-Type": "application/json", "User-Agent": "check"}
            if cookie:
                h["Cookie"] = f"rt={cookie}"
            c.request(method, path, json.dumps(body) if body is not None else None, h)
            r = c.getresponse()
            data = r.read()
            try:
                data = json.loads(data)
            except ValueError:
                pass
            return r.status, data, r

        assert call("GET", "/api/me")[0] == 401 and call("GET", "/api/labels")[0] == 401 and call("POST", "/api/labels", {})[0] == 401
        assert call("GET", "/r/not-a-token")[0] == 403
        st, _, resp = call("GET", f"/r/{tokens['r1']}")
        assert st == 302 and f"rt={tokens['r1']}" in resp.getheader("Set-Cookie") and "HttpOnly" in resp.getheader("Set-Cookie")
        r1, r2 = tokens["r1"], tokens["r2"]
        st, me, _ = call("GET", "/api/me", cookie=r1)
        assert st == 200 and me["rater"] == "r1" and me["consented"] is False
        assert call("GET", "/api/crops", cookie=r1)[0] == 403, "crops served before consent"
        assert call("POST", "/api/labels", {"entries": [{"crop_id": "r001_00", "font": "Roboto", "coherence": "one"}]}, r1)[0] == 403
        assert call("POST", "/api/consent", {"agree": True, "text_sha": "stale"}, r1)[0] == 400
        assert call("POST", "/api/consent", {"agree": True, "text_sha": CONSENT_SHA}, r1)[0] == 200
        st, got, _ = call("GET", "/api/crops", cookie=r1)
        ids = [c["crop_id"] for c in got["crops"]]
        assert st == 200 and len(ids) == 10 and ids == order["r1"]
        assert call("GET", f"/data/real/crops/{ids[0]}.png", cookie=r1)[0] == 200
        assert call("GET", "/data/real/crops/r001_00.png", cookie=r1)[0] == 200
        assert call("GET", "/data/real/crops/zzz.png", cookie=r1)[0] == 404, "a crop that is not the rater's was served"
        # the body may claim another rater: the cookie wins
        spoof = {"entries": [{"crop_id": ids[0], "rater": "r2", "font": "Roboto", "coherence": "one", "ms": 5000}]}
        assert call("POST", "/api/labels", spoof, r1)[0] == 200
        assert not store.rater_labels("r2") and list(store.rater_labels("r1")) == [ids[0]]
        assert call("POST", "/api/labels", {"entries": [{"crop_id": "elsewhere", "font": "Roboto", "coherence": "one"}]}, r1)[0] == 400
        assert call("GET", "/api/labels", cookie=r2)[0] == 403, "r2 read labels without consenting"
        assert call("POST", "/api/consent", {"agree": True, "text_sha": CONSENT_SHA}, r2)[0] == 200
        assert call("GET", "/api/labels?rater=r1", cookie=r2)[1] == {"rater": "r2", "labels": {}}, "r2 can read r1's answers"
        assert call("POST", "/api/finish", {}, r1)[0] == 409, "finished with items unanswered"
        entries = [{"crop_id": c, "font": "Lora" if i % 2 else "unknown", "coherence": "one", "ms": 4000 + i} for i, c in enumerate(ids)]
        assert call("POST", "/api/labels", {"entries": entries}, r1)[0] == 200
        st, fin, _ = call("POST", "/api/finish", {}, r1)
        rc1 = fin["receipt"]
        assert st == 200 and rc1["rows"] == 10 and rc1["label_set_sha256"] == store.label_set_sha("r1")
        assert call("POST", "/api/finish", {}, r1)[1]["receipt"] == rc1, "finish is not idempotent"
        assert call("POST", "/api/labels", {"entries": entries[:1]}, r1)[0] == 409, "answers changed after finishing"
        assert call("GET", "/api/me", cookie=r1)[1]["receipt"] == rc1
        assert not (d / "labels.csv").read_text().count("elsewhere")
        assert set(read_rater_labels("r1", d / "labels.csv")).isdisjoint(items), "a control reached labels.csv, which real.py score reads"
        assert set(read_rater_labels("r1", d / "labels_controls.csv")) == set(items)

        rep = store.verify()
        assert rep["chain_ok"] and rep["raters"]["r1"]["receipt_matches"] and rep["raters"]["r1"]["answered"] == 10, rep
        assert rep["raters"]["r1"]["retest_items"] == 2 and rep["raters"]["r1"]["gold_items"] == 2
        print_report(rep)
        # tampering is detected: an edited log line, and a label changed after the receipt
        lines = store.audit_path.read_text().splitlines()
        original = store.audit_path.read_text()
        store.audit_path.write_text("\n".join(lines[:2] + [lines[2].replace('"ms":', '"ms":1,"x":')] + lines[3:]) + "\n")
        assert not store.verify()["chain_ok"], "an edited audit line was not detected"
        store.audit_path.write_text(original)
        assert store.verify()["chain_ok"]
        upsert_labels([{"crop_id": "r001_00", "rater": "r1", "font": "Roboto", "coherence": "two"}], labels_csv=store.labels)
        assert not store.verify()["raters"]["r1"]["receipt_matches"], "a label edited after the receipt was not detected"
        server.shutdown()
        server.server_close()
    print("ok: rater server passed all checks (PNG crops, blind isolation, token identity, consent, controls, receipts, audit chain)")


def serve(host="127.0.0.1", port=8000):
    store = Store()
    if not store.config():
        sys.exit("no rater links yet: run `server.py tokens --base-url <your public url>` first")
    if not store.controls_path.exists():
        print("note: no hidden controls yet (run `server.py controls` before any rater starts)")
    server = ThreadingHTTPServer((host, port), RaterRequestHandler)
    server.store = store
    print(f"Expert-Panel Rating Form running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Expert-Panel Rating Form server (Ch4 §4.2.3, Appendix B)")
    ap.add_argument("cmd", nargs="?", default="serve", choices=["serve", "tokens", "controls", "verify"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--base-url", default=None, help="tokens: the public address the raters will open")
    ap.add_argument("--check", action="store_true", help="Run self-tests")
    args = ap.parse_args()
    if args.check:
        check()
    elif args.cmd == "tokens":
        base = (args.base_url or f"http://{args.host}:{args.port}").rstrip("/")
        links = Store().issue_tokens()
        print("Personal links (shown once; only their hashes are stored). Send each to its own expert, by email:")
        for r, t in links.items():
            print(f"  {r}: {base}/r/{t}")
    elif args.cmd == "controls":
        made = Store().build_controls()
        print(f"{len(made)} hidden controls built ({sum(v['kind'] == 'dup' for v in made.values())} repeats, "
              f"{sum(v['kind'] == 'gold' for v in made.values())} clean references) -> data/real/controls.private.json (not committed)")
    elif args.cmd == "verify":
        print_report(Store().verify())
    else:
        serve(args.host, args.port)
