"""Backend server and CLI for the Expert-Panel Rating Form (Section 4.2.3, Appendix B).

Serves:
  - GET  /api/palette                  -> the 80 Google Fonts from data/palette.csv
  - GET  /api/crops                    -> localized real crops from data/real/crops.csv
                                          (or pre-built data/corpus/ metadata if present,
                                          or a 100-crop stratified synthetic dataset benchmark
                                          rendered via src/data/render_corpus.py & render_mixed.py)
  - GET  /api/crop-image/<crop_id>.png -> serves or deterministically renders PNG crop from dataset pipeline
  - GET  /api/labels?rater=r1          -> saved responses for ONLY the requested rater (blind protocol:
                                          never returns another rater's labels or predictions.csv)
  - POST /api/labels                   -> upserts one or more (crop_id, rater, font, coherence) rows
                                          into data/real/labels.csv atomically
  - GET  /fonts/<file>.ttf             -> static TTF files from data/fonts/ for live @font-face specimens
  - GET  /data/real/crops/...          -> static crop PNGs from data/real/crops/
  - GET  /*                            -> built React frontend from src/rater/dist/ (if built)

Usage:
    .venv/bin/python src/rater/server.py --port 8000
    .venv/bin/python src/rater/server.py --check
"""

import argparse
import csv
import io
import json
import mimetypes
import sys
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


class RaterRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep console output clean unless debugging
        pass

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, data: bytes, mime: str, cache_seconds: int = 3600):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", f"public, max-age={cache_seconds}")
        self.send_header("Access-Control-Allow-Origin", "*")
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

    def do_OPTIONS(self):
        self._send_json(HTTPStatus.OK, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path
        qs = parse_qs(parsed.query)

        if route == "/api/palette":
            self._send_json(HTTPStatus.OK, {"fonts": load_palette()})
            return

        if route == "/api/crops":
            source = (qs.get("source") or [None])[0]
            self._send_json(HTTPStatus.OK, load_crops(source=source))
            return

        if route.startswith("/api/crop-image/"):
            stem = Path(route.removeprefix("/api/crop-image/")).stem
            png_bytes = render_dataset_crop_png(stem)
            if png_bytes is None:
                self.send_error(HTTPStatus.NOT_FOUND, f"Unknown crop_id: {stem}")
                return
            self._send_bytes(png_bytes, "image/png")
            return

        if route == "/api/labels":
            rater = (qs.get("rater") or ["r1"])[0]
            if rater not in VALID_RATERS:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": f"Invalid rater: {rater}"})
                return
            self._send_json(HTTPStatus.OK, {"rater": rater, "labels": read_rater_labels(rater)})
            return

        if route.startswith("/fonts/"):
            rel = Path(route.removeprefix("/fonts/")).name
            self._send_file(FONTS_DIR / rel)
            return

        if route.startswith("/data/real/crops/"):
            rel = Path(route.removeprefix("/data/real/crops/")).name
            self._send_file(REAL_DIR / "crops" / rel)
            return

        if route.startswith("/data/corpus"):
            candidate = (ROOT / route.lstrip("/")).resolve()
            if str(candidate).startswith(str((ROOT / "data").resolve())) and candidate.is_file():
                self._send_file(candidate)
                return

        # Serve static frontend from dist/ if built
        if DIST_DIR.exists():
            candidate = (DIST_DIR / route.lstrip("/")).resolve()
            if str(candidate).startswith(str(DIST_DIR)) and candidate.is_file():
                self._send_file(candidate)
                return
            if (DIST_DIR / "index.html").is_file():
                self._send_file(DIST_DIR / "index.html")
                return

        self._send_json(
            HTTPStatus.OK,
            {
                "service": "Expert Panel Rating Form API",
                "endpoints": [
                    "/api/palette",
                    "/api/crops",
                    "/api/crop-image/crop_01_00.png",
                    "/api/labels?rater=r1",
                ],
            },
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/labels":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            entries = payload.get("entries") if isinstance(payload, dict) and "entries" in payload else [payload]
            total = upsert_labels(entries)
            self._send_json(HTTPStatus.OK, {"ok": True, "saved": len(entries), "total_rows": total})
        except Exception as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})


def check():
    """Verify palette loading, real PNG crop rendering, blind rater isolation, and real.py score."""
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
    print("ok: rater server passed all checks (including real PNG crop rendering)")


def serve(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), RaterRequestHandler)
    print(f"Expert-Panel Rating Form running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Expert-Panel Rating Form server (Ch4 §4.2.3, Appendix B)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--check", action="store_true", help="Run self-tests")
    args = ap.parse_args()
    if args.check:
        check()
    else:
        serve(args.host, args.port)
