import { AlertTriangle, ArrowUpRight, ImageUp, Loader2, RotateCcw, Type } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Badge } from "./components/ui/badge.jsx";
import { Button } from "./components/ui/button.jsx";
import { Card, CardContent } from "./components/ui/card.jsx";
import { cn } from "./lib/utils.js";

const VERDICT = {
  known: { label: "Match", badge: "emerald", color: "#059669" },
  unknown: { label: "Unknown font", badge: "amber", color: "#d97706" },
  mixed: { label: "Two typefaces", badge: "violet", color: "#7c3aed" },
};

// One FontFace per palette font, loaded the first time a card shows it.
const faces = new Map();
function useFont({ font_id, ttf_url }) {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let live = true;
    if (!faces.has(font_id)) {
      const face = new FontFace(`pf-${font_id}`, `url(${ttf_url})`);
      faces.set(
        font_id,
        face.load().then(() => document.fonts.add(face)),
      );
    }
    faces
      .get(font_id)
      .then(() => live && setReady(true))
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [font_id, ttf_url]);
  return ready ? `"pf-${font_id}", sans-serif` : "inherit";
}

async function analyze(file, checkMixed) {
  const body = new FormData();
  body.append("file", file);
  let res;
  try {
    res = await fetch(`/predict?check_mixed=${checkMixed}`, { method: "POST", body });
  } catch {
    throw new Error("Cannot reach the recognizer service. Is the server running?");
  }
  if (!res.ok) {
    const detail = await res.json().then(
      (j) => j.detail,
      () => null,
    );
    throw new Error(typeof detail === "string" ? detail : `The server returned ${res.status}.`);
  }
  return res.json();
}

function Thumb({ img, box, width }) {
  const ref = useRef(null);
  useEffect(() => {
    const [x0, y0, x1, y1] = box;
    const s = img.naturalWidth / width;
    const c = ref.current;
    c.width = Math.max(1, Math.round((x1 - x0) * s));
    c.height = Math.max(1, Math.round((y1 - y0) * s));
    c.getContext("2d").drawImage(img, x0 * s, y0 * s, c.width, c.height, 0, 0, c.width, c.height);
  }, [img, box, width]);
  return (
    <canvas
      ref={ref}
      className="h-12 max-w-36 shrink-0 rounded border border-slate-200 bg-slate-100 object-contain"
    />
  );
}

function Candidate({ c, text, rank }) {
  const family = useFont(c);
  return (
    <li className="flex items-center gap-3 py-2">
      <span className="w-4 text-xs tabular-nums text-slate-400">{rank}</span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-2xl leading-tight" style={{ fontFamily: family }}>
          {text}
        </p>
        <p className="mt-0.5 flex flex-wrap items-center gap-x-2 text-xs text-slate-500">
          <span className="font-medium text-slate-700">{c.family}</span>
          {c.weight !== "400" && <span>weight {c.weight}</span>}
          <span>{c.family_class}</span>
        </p>
      </div>
      <div className="shrink-0 text-right">
        <p
          className="text-sm tabular-nums text-slate-700"
          title="Cosine similarity to the font's prototype"
        >
          {c.similarity.toFixed(2)}
        </p>
        <a
          href={`https://fonts.google.com/specimen/${c.family.replace(/ /g, "+")}`}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center text-xs text-slate-500 underline-offset-2 hover:text-slate-900 hover:underline"
        >
          Google Fonts
          <ArrowUpRight className="size-3" />
        </a>
      </div>
    </li>
  );
}

function Candidates({ list, text }) {
  return (
    <ol className="divide-y divide-slate-100">
      {list.map((c, i) => (
        <Candidate key={c.font_id} c={c} text={text} rank={i + 1} />
      ))}
    </ol>
  );
}

function RegionCard({ r, img, width, tau, active, onSelect }) {
  const v = VERDICT[r.verdict];
  const n = r.halves ? Math.round(r.text.length * r.cut) : 0;
  return (
    <Card
      id={`region-${r.id}`}
      onClick={onSelect}
      className={cn("scroll-mt-4 cursor-pointer", active && "ring-2 ring-slate-900")}
    >
      <CardContent className="space-y-3 p-4">
        <div className="flex items-center gap-3">
          <span
            className="flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white"
            style={{ background: v.color }}
          >
            {r.id + 1}
          </span>
          <Thumb img={img} box={r.box} width={width} />
          <div className="min-w-0 flex-1">
            <p className="truncate font-medium">{r.text || "(no text read)"}</p>
            <p className="text-xs text-slate-500">
              Read with {Math.round(r.ocr_conf * 100)}% confidence
            </p>
          </div>
          <Badge variant={v.badge}>{v.label}</Badge>
        </div>

        {r.verdict === "known" && <Candidates list={r.candidates} text={r.text} />}

        {r.verdict === "unknown" && (
          <div className="space-y-2 text-sm text-slate-600">
            <p>
              No font in the palette is close enough to call it a match (best similarity{" "}
              {r.candidates[0].similarity.toFixed(2)}, needs {tau.toFixed(2)}). Better no answer
              than a wrong one.
            </p>
            <details>
              <summary className="cursor-pointer text-xs text-slate-500">
                Closest, below the threshold
              </summary>
              <Candidates list={r.candidates} text={r.text} />
            </details>
          </div>
        )}

        {r.verdict === "mixed" && (
          <div className="space-y-2">
            <p className="text-sm text-slate-600">
              This region looks like two typefaces, split about {Math.round(r.cut * 100)}% across.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              {r.halves.map((h, i) => (
                <div
                  key={i === 0 ? "left" : "right"}
                  className="rounded-lg border border-slate-100 p-2"
                >
                  <p className="mb-1 text-xs font-medium text-slate-500">
                    {i === 0 ? "Left part" : "Right part"}
                  </p>
                  {h.verdict === "known" ? (
                    <Candidates
                      list={h.candidates}
                      text={i === 0 ? r.text.slice(0, n) : r.text.slice(n)}
                    />
                  ) : (
                    <p className="text-sm text-slate-600">
                      {h.verdict === "mixed"
                        ? "Still more than one typeface."
                        : "No palette font is close enough."}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Overlay({ url, result, active, setActive }) {
  const { width: w, height: h } = result;
  return (
    <div className="relative">
      <img src={url} alt="Uploaded" className="block w-full rounded-lg border border-slate-200" />
      <svg
        viewBox={`0 0 ${w} ${h}`}
        preserveAspectRatio="none"
        className="absolute inset-0 h-full w-full"
      >
        <title>Detected text regions</title>
        {result.regions.map((r) => {
          const [x0, y0, x1, y1] = r.box;
          const { color } = VERDICT[r.verdict];
          return (
            <rect
              key={r.id}
              x={x0}
              y={y0}
              width={x1 - x0}
              height={y1 - y0}
              fill={active === r.id ? `${color}33` : "transparent"}
              stroke={color}
              strokeWidth={active === r.id ? 3 : 2}
              vectorEffect="non-scaling-stroke"
              className="cursor-pointer"
              onClick={() => setActive(r.id)}
            />
          );
        })}
      </svg>
      {result.regions.map((r) => (
        <button
          key={r.id}
          type="button"
          onClick={() => setActive(r.id)}
          className="absolute flex size-5 -translate-y-full items-center justify-center rounded-full text-[11px] font-semibold text-white"
          style={{
            left: `${(r.box[0] / w) * 100}%`,
            top: `${(r.box[1] / h) * 100}%`,
            background: VERDICT[r.verdict].color,
          }}
        >
          {r.id + 1}
        </button>
      ))}
    </div>
  );
}

function Dropzone({ onFile, checkMixed, setCheckMixed }) {
  const [over, setOver] = useState(false);
  return (
    <div className="mx-auto max-w-xl space-y-3">
      <label
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]);
        }}
        className={cn(
          "flex cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed border-slate-300 bg-white px-6 py-14 text-center transition-colors hover:border-slate-500",
          over && "border-slate-900 bg-slate-100",
        )}
      >
        <ImageUp className="size-8 text-slate-400" />
        <span className="font-medium">Drop an image here, or click to choose one</span>
        <span className="text-sm text-slate-500">
          PNG, JPEG or WebP, up to 10 MB. The image is analysed and not stored.
        </span>
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp"
          className="sr-only"
          onChange={(e) => e.target.files[0] && onFile(e.target.files[0])}
        />
      </label>
      <label className="flex items-center gap-2 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={checkMixed}
          onChange={(e) => setCheckMixed(e.target.checked)}
        />
        Also check each region for two typefaces (slower)
      </label>
    </div>
  );
}

export default function App() {
  const [info, setInfo] = useState(null);
  const [state, setState] = useState({ phase: "idle" });
  const [checkMixed, setCheckMixed] = useState(true);
  const [active, setActive] = useState(null);

  useEffect(() => {
    fetch("/api/info")
      .then((r) => r.json())
      .then(setInfo)
      .catch(() =>
        setState({
          phase: "error",
          message: "Cannot reach the recognizer service. Is the server running?",
        }),
      );
  }, []);

  useEffect(() => {
    if (active !== null)
      document
        .getElementById(`region-${active}`)
        ?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [active]);

  async function onFile(file) {
    const url = URL.createObjectURL(file);
    setActive(null);
    setState({ phase: "loading", url });
    try {
      const img = new Image();
      img.src = url;
      const [result] = await Promise.all([analyze(file, checkMixed), img.decode().catch(() => {})]);
      setState({ phase: "done", url, img, result });
    } catch (e) {
      setState({ phase: "error", message: e.message });
    }
  }

  const reset = () => {
    if (state.url) URL.revokeObjectURL(state.url);
    setState({ phase: "idle" });
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-lg bg-slate-900 text-white">
            <Type className="size-5" />
          </span>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Font Recognizer</h1>
            <p className="text-sm text-slate-500">
              Finds the closest Google Font for the text in an AI-generated image, or says it can't.
            </p>
          </div>
        </div>
        {info && (
          <p className="text-xs text-slate-500">
            {info.palette_size} Google Fonts · match threshold {info.tau.toFixed(2)} · {info.device}
          </p>
        )}
      </header>

      {state.phase === "idle" && (
        <Dropzone onFile={onFile} checkMixed={checkMixed} setCheckMixed={setCheckMixed} />
      )}

      {state.phase === "loading" && (
        <div className="mx-auto flex max-w-xl flex-col items-center gap-3 rounded-xl border border-slate-200 bg-white px-6 py-14 text-center">
          <Loader2 className="size-7 animate-spin text-slate-400" />
          <p className="font-medium">Reading the text and comparing fonts…</p>
          <p className="text-sm text-slate-500">A few seconds per text region on a CPU.</p>
        </div>
      )}

      {state.phase === "error" && (
        <div className="mx-auto max-w-xl space-y-4 rounded-xl border border-rose-200 bg-rose-50 p-6">
          <p className="flex items-start gap-2 text-rose-800">
            <AlertTriangle className="mt-0.5 size-4 shrink-0" />
            {state.message}
          </p>
          <Button variant="outline" onClick={reset}>
            <RotateCcw className="size-4" />
            Try another image
          </Button>
        </div>
      )}

      {state.phase === "done" && (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)]">
          <div className="space-y-3 lg:sticky lg:top-6 lg:self-start">
            <Overlay url={state.url} result={state.result} active={active} setActive={setActive} />
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-slate-500">
                {state.result.regions.length} text region
                {state.result.regions.length === 1 ? "" : "s"} ·{" "}
                {(state.result.latency_ms / 1000).toFixed(1)} s
              </p>
              <Button variant="outline" size="sm" onClick={reset}>
                <RotateCcw className="size-3.5" />
                Another image
              </Button>
            </div>
          </div>

          <div className="space-y-3">
            {state.result.skipped > 0 && (
              <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                {state.result.skipped} smaller text region
                {state.result.skipped === 1 ? " was" : "s were"} left out to keep the wait short.
                The largest are shown.
              </p>
            )}
            {state.result.regions.length === 0 ? (
              <p className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">
                No text found. Try an image where the text is larger or clearer.
              </p>
            ) : (
              state.result.regions.map((r) => (
                <RegionCard
                  key={r.id}
                  r={r}
                  img={state.img}
                  width={state.result.width}
                  tau={state.result.tau}
                  active={active === r.id}
                  onSelect={() => setActive(r.id)}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
