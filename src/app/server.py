"""Font-identification web application: the FastAPI backend (Sections 4.5, 4.6.3).

    POST /predict   multipart `file` (PNG, JPEG or WebP) -> one entry per text region: box, OCR text, verdict
                    (known | unknown | mixed) and the Top-K palette fonts. Stateless.
    GET  /api/info  model provenance, threshold, palette size, device
    GET  /fonts/*   the palette's TTF files, for the live previews
    GET  /*         the built frontend (src/app/dist)

    .venv/bin/python src/app/server.py                 # http://127.0.0.1:8001 (needs `bun run build` in src/app)
    .venv/bin/python src/app/server.py --check         # response contract, abnormal inputs, determinism

The weights and the localizer load once at startup. The pipeline is the one the real-crop evaluation runs
(src/model/real.py predict): EasyOCR word boxes, grayscale crop, bundle.Recognizer.
"""

import argparse
import csv
import io
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import numpy as np
import torch
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/model"))

from bundle import Recognizer  # noqa: E402
from real import WIDTH_THS, boxes_to_crops  # noqa: E402

FONTS_DIR = ROOT / "data/fonts"
DIST_DIR = Path(__file__).resolve().parent / "dist"
TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_BYTES = 10 * 2**20
MAX_SIDE = 2048     # longer images are scaled down before OCR; boxes come back in the scaled frame
MAX_REGIONS = 12    # the largest regions are kept: each costs about 3 s on CPU with the homogeneity check, 1 s without

PALETTE = {r["font_id"]: r for r in csv.DictReader((ROOT / "data/palette.csv").open(encoding="utf-8"))}
LOCK = threading.Lock()  # one inference at a time: single-user demo, and the localizer is not thread-safe
Verdict = Literal["known", "unknown", "mixed"]


class Candidate(BaseModel):
    font_id: str
    family: str
    weight: str
    family_class: str
    similarity: float
    ttf_url: str


class Half(BaseModel):
    verdict: Verdict
    candidates: list[Candidate]


class Region(BaseModel):
    id: int
    box: tuple[int, int, int, int]  # x0, y0, x1, y1 in the analysed image
    text: str
    ocr_conf: float
    verdict: Verdict                # mixed: the crop looks like two typefaces, see halves
    candidates: list[Candidate]
    cut: float | None = None        # where mixed regions are split, as a share of the width
    halves: list[Half] | None = None


class Prediction(BaseModel):
    width: int
    height: int
    regions: list[Region]
    skipped: int                    # regions beyond MAX_REGIONS, smallest first
    tau: float
    latency_ms: int


def candidates(topk):
    out = []
    for font, sim in topk:
        p = PALETTE[font["font_id"]]
        out.append(Candidate(font_id=font["font_id"], family=p["family"], weight=p["weight"],
                             family_class=p["family_class"], similarity=round(sim, 4),
                             ttf_url=f"/fonts/{Path(p['ttf_path']).name}"))
    return out


@asynccontextmanager
async def lifespan(app):
    import easyocr
    app.state.rec = Recognizer()
    app.state.reader = easyocr.Reader(["en"], gpu=torch.cuda.is_available(), verbose=False)
    yield


app = FastAPI(title="Typographic hallucination font recognizer", lifespan=lifespan)


@app.get("/api/info")
def info():
    rec = app.state.rec
    return {"provenance": rec.provenance, "tau": rec.tau, "palette_size": len(rec.fonts), "device": rec.dev}


@app.post("/predict", response_model=Prediction)
def predict(file: UploadFile, k: int = 3, check_mixed: bool = True, max_regions: int = MAX_REGIONS):
    if file.content_type not in TYPES:
        raise HTTPException(415, "Upload a PNG, JPEG or WebP image.")
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, f"The image is over {MAX_BYTES // 2**20} MB.")
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except Exception:
        raise HTTPException(400, "The file could not be read as an image.")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    t0, rec = time.perf_counter(), app.state.rec
    with LOCK:
        a = np.asarray(img)
        found = boxes_to_crops(app.state.reader.readtext(a, width_ths=WIDTH_THS), *a.shape[:2])
        found.sort(key=lambda f: -(f[0][2] - f[0][0]) * (f[0][3] - f[0][1]))
        skipped, found = max(0, len(found) - max_regions), found[:max_regions]
        found.sort(key=lambda f: (f[0][1] // 20, f[0][0]))  # reading order, roughly
        regions = []
        for n, (box, text, conf) in enumerate(found):
            crop = torch.from_numpy(np.array(img.crop(box).convert("L")))
            if check_mixed:
                res = rec(crop, k)
            else:
                top = rec.topk(crop, k)
                res = {"topk": top, "verdict": "known" if top[0][1] >= rec.tau else "unknown",
                       "homogeneous": True, "cut": None, "halves": None}
            r = Region(id=n, box=box, text=text, ocr_conf=round(conf, 3),
                       verdict="mixed" if not res["homogeneous"] else res["verdict"],
                       candidates=candidates(res["topk"]))
            if res["halves"]:
                r.cut = round(res["cut"], 3)
                r.halves = [Half(verdict=h["verdict"], candidates=candidates(h["topk"])) for h in res["halves"]]
            regions.append(r)
    return Prediction(width=img.width, height=img.height, regions=regions, skipped=skipped, tau=rec.tau,
                      latency_ms=round((time.perf_counter() - t0) * 1000))


app.mount("/fonts", StaticFiles(directory=FONTS_DIR), name="fonts")
if DIST_DIR.exists():  # registered last so it never shadows the routes above
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="web")


def check():
    """The contract, the failure modes of Section 4.10 (unsupported type, unreadable file, too large, no text)
    and determinism, against the real model."""
    from fastapi.testclient import TestClient
    from PIL import ImageDraw, ImageFont

    def png(im):
        b = io.BytesIO()
        im.save(b, "PNG")
        return b.getvalue()

    poster = Image.new("RGB", (1000, 360), "white")
    d = ImageDraw.Draw(poster)
    d.text((40, 30), "Summer Sale", font=ImageFont.truetype(str(FONTS_DIR / "Roboto-400.ttf"), 130), fill="black")
    d.text((40, 210), "Open Today", font=ImageFont.truetype(str(FONTS_DIR / "Lobster-400.ttf"), 110), fill="black")

    with TestClient(app) as c:
        i = c.get("/api/info").json()
        assert i["palette_size"] == 80 and 0 < i["tau"] < 1, i
        post = lambda b, t="image/png", **q: c.post("/predict", files={"file": ("x", b, t)}, params=q)

        r = post(png(poster))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["width"] == 1000 and body["height"] == 360 and body["regions"], body
        for g in body["regions"]:
            x0, y0, x1, y1 = g["box"]
            assert 0 <= x0 < x1 <= 1000 and 0 <= y0 < y1 <= 360, g
            assert g["verdict"] in ("known", "unknown", "mixed") and len(g["candidates"]) == 3, g
            assert all(0 <= cand["similarity"] <= 1 and cand["ttf_url"].startswith("/fonts/") for cand in g["candidates"])
            assert (g["verdict"] == "mixed") == (g["halves"] is not None and len(g["halves"]) == 2), g
            assert c.get(g["candidates"][0]["ttf_url"]).status_code == 200
        print("regions:", [(g["text"], g["verdict"], g["candidates"][0]["family"]) for g in body["regions"]])

        again = post(png(poster)).json()
        assert {**again, "latency_ms": 0} == {**body, "latency_ms": 0}, "same input, different output"
        fast = post(png(poster), check_mixed=False).json()
        assert all(g["verdict"] != "mixed" for g in fast["regions"])
        assert len(post(png(poster), max_regions=1).json()["regions"]) == 1

        assert post(b"hello", "text/plain").status_code == 415
        assert post(b"not an image", "image/png").status_code == 400
        assert post(b"0" * (MAX_BYTES + 5)).status_code == 413
        blank = post(png(Image.new("RGB", (400, 200), "white"))).json()
        assert blank["regions"] == [] and blank["skipped"] == 0, blank
        big = post(png(Image.new("RGB", (4000, 1000), "white"))).json()
        assert big["width"] == MAX_SIDE, big["width"]
    print("ok: web backend passed all checks")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Font-identification web application backend")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8001)
    ap.add_argument("--check", action="store_true", help="Run self-tests")
    args = ap.parse_args()
    if args.check:
        check()
    else:
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
