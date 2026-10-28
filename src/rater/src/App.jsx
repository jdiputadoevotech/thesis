import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Contrast,
  Database,
  Download,
  Eye,
  FlipHorizontal,
  Layers,
  Pin,
  RotateCcw,
  Search,
  Sparkles,
  SplitSquareVertical,
  Type,
  UserCheck,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ConsentScreen, Notice, ReceiptScreen } from "./Gate.jsx";
import { Badge } from "./components/ui/badge.jsx";
import { Button } from "./components/ui/button.jsx";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card.jsx";
import { Input } from "./components/ui/input.jsx";
import { Progress, Separator, TabsList, TabsTrigger } from "./components/ui/progress.jsx";
import { cn } from "./lib/utils.js";
import { FALLBACK_PALETTE } from "./paletteData.js";

const COHERENCE_OPTIONS = [
  {
    value: "one",
    keyHint: "1",
    label: "One typeface",
    desc: "All characters belong to a single consistent typeface family",
    activeClass: "border-emerald-600 bg-emerald-50/70 ring-1 ring-emerald-600",
    dotClass: "border-emerald-600 bg-emerald-600",
    badgeVariant: "emerald",
  },
  {
    value: "two",
    keyHint: "2",
    label: "More than one typeface",
    desc: "Noticeable mid-word or word-level typeface switch (chimeric text)",
    activeClass: "border-amber-600 bg-amber-50/70 ring-1 ring-amber-600",
    dotClass: "border-amber-600 bg-amber-600",
    badgeVariant: "amber",
  },
  {
    value: "cannot_tell",
    keyHint: "3",
    label: "Cannot tell",
    desc: "Too short, blurred, or distorted to judge homogeneity",
    activeClass: "border-slate-800 bg-slate-100 ring-1 ring-slate-800",
    dotClass: "border-slate-800 bg-slate-800",
    badgeVariant: "secondary",
  },
];

const CLASS_TABS = [
  { id: "all", label: "All (80)" },
  { id: "sans-serif", label: "Sans (38)" },
  { id: "serif", label: "Serif (20)" },
  { id: "display", label: "Display (16)" },
  { id: "monospace", label: "Mono (6)" },
];

const CLASS_BADGE_VARIANT = {
  "sans-serif": "blue",
  serif: "amber",
  display: "destructive",
  monospace: "emerald",
};

export default function App() {
  // who the server says this is: undefined while loading, null without a valid personal link
  const [me, setMe] = useState(undefined);
  const rater = me?.rater ?? "";
  const [palette, setPalette] = useState(FALLBACK_PALETTE);
  const [crops, setCrops] = useState([]);
  const [cropMode, setCropMode] = useState("real");
  const [sourceLabel, setSourceLabel] = useState("Real Generative Crops");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [labelsByCrop, setLabelsByCrop] = useState({});
  const [selectedFont, setSelectedFont] = useState("");
  const [selectedCoherence, setSelectedCoherence] = useState("");
  const [saveState, setSaveState] = useState("idle");
  const [filterUnratedOnly, setFilterUnratedOnly] = useState(false);

  // Crop Inspector & Comparator states
  const [zoom, setZoom] = useState(1.5);
  const [canvasTheme, setCanvasTheme] = useState("checker-dark"); // checker-dark | checker-light | dark | light
  const [invertCrop, setInvertCrop] = useState(false);
  const [highContrastCrop, setHighContrastCrop] = useState(false);
  const [pixelatedCrop, setPixelatedCrop] = useState(false);
  const [cropDimensions, setCropDimensions] = useState(null);
  const [cropLoadError, setCropLoadError] = useState(false);

  // Specimen Comparator Controls
  const [specimenSize, setSpecimenSize] = useState(44);
  const [specimenTracking, setSpecimenTracking] = useState(0);
  const [specimenTextMode, setSpecimenTextMode] = useState("crop"); // crop | upper | lower | anatomy | custom
  const [customSpecimenText, setCustomSpecimenText] = useState("");
  const [pinnedFonts, setPinnedFonts] = useState(["Open Sans", "Roboto", "Playfair Display"]);
  const [hoveredFont, setHoveredFont] = useState(null);

  // Q1 Combobox dropdown state
  const [comboOpen, setComboOpen] = useState(false);
  const [comboQuery, setComboQuery] = useState("");
  const comboRef = useRef(null);
  const shownAt = useRef(Date.now()); // when the current item appeared, for the time-on-item record

  // Right-pane Palette Browser state
  const [browserClass, setBrowserClass] = useState("all");
  const [browserSearch, setBrowserSearch] = useState("");

  // Inject @font-face declarations for all 80 pinned TTFs
  useEffect(() => {
    const id = "thesis-palette-font-faces";
    if (document.getElementById(id)) return;
    const style = document.createElement("style");
    style.id = id;
    style.textContent = palette
      .map(
        (f) =>
          `@font-face { font-family: "Palette_${f.font_id}"; src: url("${f.ttf_url}") format("truetype"); font-display: swap; }`,
      )
      .join("\n");
    document.head.appendChild(style);
  }, [palette]);

  useEffect(() => {
    fetch("/api/me")
      .then((r) => (r.ok ? r.json() : null))
      .then(setMe)
      .catch(() => setMe(null));
  }, []);

  // Load palette & crops from backend
  useEffect(() => {
    let active = true;
    fetch("/api/palette")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (active && data?.fonts?.length) setPalette(data.fonts);
      })
      .catch(() => {});

    if (me?.consented) {
      fetch("/api/crops")
        .then((r) => (r.ok ? r.json() : null))
        .then((data) => {
          if (active && data?.crops?.length) {
            setCrops(data.crops);
            setCropMode(data.mode || "real");
            if (data.source_label) setSourceLabel(data.source_label);
          }
        })
        .catch(() => {});
    }
    return () => {
      active = false;
    };
  }, [me?.consented]);

  // The server holds the only copy of the answers, and returns only this rater's (blind protocol)
  useEffect(() => {
    if (!me?.consented) return;
    let active = true;
    fetch("/api/labels")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (active && data?.labels) setLabelsByCrop(data.labels);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [me?.consented]);

  const currentCrop = crops[currentIndex] || crops[0];

  const shownId = currentCrop?.crop_id;
  useEffect(() => {
    if (shownId) shownAt.current = Date.now();
  }, [shownId]);

  // Sync Q1 & Q2 selections when switching crop
  useEffect(() => {
    if (!currentCrop) return;
    setCropDimensions(null);
    setCropLoadError(false);
    const saved = labelsByCrop[currentCrop.crop_id];
    setSelectedFont(saved?.font || "");
    setSelectedCoherence(saved?.coherence || "");
    setSaveState(saved ? "saved" : "idle");
  }, [currentCrop, labelsByCrop]);

  // Close Q1 combobox on outside click
  useEffect(() => {
    function onDocClick(e) {
      if (comboRef.current && !comboRef.current.contains(e.target)) {
        setComboOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const persistEntry = useCallback(
    async (cropId, fontVal, coherenceVal) => {
      if (!cropId || !fontVal || !coherenceVal) return false;
      const entry = {
        crop_id: cropId,
        font: fontVal,
        coherence: coherenceVal,
        ms: Date.now() - shownAt.current,
      };
      setSaveState("saving");
      try {
        const res = await fetch("/api/labels", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ entries: [entry] }),
        });
        if (res.ok) {
          setLabelsByCrop((prev) => ({ ...prev, [cropId]: { ...entry, rater } }));
          setSaveState("saved");
          return true;
        }
      } catch {
        // fall through: the answer is not counted until the server has it
      }
      setSaveState("error");
      return false;
    },
    [rater],
  );

  const canSaveCurrent = Boolean(currentCrop && selectedFont && selectedCoherence);

  const handleSaveAndNext = useCallback(async () => {
    if (!canSaveCurrent) return;
    if (!(await persistEntry(currentCrop.crop_id, selectedFont, selectedCoherence))) return;
    if (currentIndex < crops.length - 1) {
      setCurrentIndex((idx) => idx + 1);
    }
  }, [
    canSaveCurrent,
    currentCrop,
    currentIndex,
    crops.length,
    persistEntry,
    selectedCoherence,
    selectedFont,
  ]);

  const handlePrev = useCallback(async () => {
    if (canSaveCurrent) {
      if (!(await persistEntry(currentCrop.crop_id, selectedFont, selectedCoherence))) return;
    }
    setCurrentIndex((idx) => Math.max(0, idx - 1));
  }, [canSaveCurrent, currentCrop, persistEntry, selectedCoherence, selectedFont]);

  const handleNextWithoutSave = useCallback(() => {
    if (filterUnratedOnly) {
      const nextUnrated = crops.findIndex(
        (c, idx) => idx > currentIndex && !labelsByCrop[c.crop_id],
      );
      if (nextUnrated !== -1) {
        setCurrentIndex(nextUnrated);
        return;
      }
    }
    setCurrentIndex((idx) => Math.min(crops.length - 1, idx + 1));
  }, [crops, currentIndex, filterUnratedOnly, labelsByCrop]);

  // Keyboard shortcuts
  useEffect(() => {
    function onKeyDown(e) {
      const tag = document.activeElement?.tagName?.toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") return;
      if (e.key === "ArrowLeft" || e.key === "[") {
        e.preventDefault();
        handlePrev();
      } else if (e.key === "ArrowRight" || e.key === "]") {
        e.preventDefault();
        handleNextWithoutSave();
      } else if (e.key === "1") {
        setSelectedCoherence("one");
      } else if (e.key === "2") {
        setSelectedCoherence("two");
      } else if (e.key === "3") {
        setSelectedCoherence("cannot_tell");
      } else if (e.key === "u" || e.key === "U") {
        setSelectedFont("unknown");
      } else if (e.key === "i" || e.key === "I") {
        setInvertCrop((v) => !v);
      } else if (e.key === "Enter" && canSaveCurrent && !comboOpen) {
        e.preventDefault();
        handleSaveAndNext();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [canSaveCurrent, comboOpen, handleNextWithoutSave, handlePrev, handleSaveAndNext]);

  const filteredComboFonts = useMemo(() => {
    const q = comboQuery.trim().toLowerCase();
    if (!q) return palette;
    return palette.filter(
      (f) =>
        f.family.toLowerCase().includes(q) ||
        f.font_id.toLowerCase().includes(q) ||
        f.family_class.toLowerCase().includes(q),
    );
  }, [comboQuery, palette]);

  const filteredBrowserFonts = useMemo(() => {
    const q = browserSearch.trim().toLowerCase();
    return palette.filter((f) => {
      if (browserClass !== "all" && f.family_class !== browserClass) {
        return false;
      }
      if (!q) return true;
      return f.family.toLowerCase().includes(q) || f.font_id.toLowerCase().includes(q);
    });
  }, [browserClass, browserSearch, palette]);

  const selectedPaletteObj = useMemo(
    () => palette.find((f) => f.family === selectedFont || f.font_id === selectedFont),
    [palette, selectedFont],
  );

  // Active comparison font in the live comparator (hovered font in palette browser, or selected Q1 font)
  const activeCompareFontObj = useMemo(() => {
    if (hoveredFont) {
      const found = palette.find((f) => f.family === hoveredFont);
      if (found) return found;
    }
    return selectedPaletteObj || null;
  }, [hoveredFont, palette, selectedPaletteObj]);

  // Specimen string to render for direct comparison against the crop
  const comparisonText = useMemo(() => {
    const baseText = currentCrop?.ocr_text || "Typography";
    if (specimenTextMode === "upper") return baseText.toUpperCase();
    if (specimenTextMode === "lower") return baseText.toLowerCase();
    if (specimenTextMode === "anatomy") {
      return `${baseText} · Aa Bb Gg Qq Rr M y 0123`;
    }
    if (specimenTextMode === "custom" && customSpecimenText.trim()) {
      return customSpecimenText;
    }
    return baseText;
  }, [currentCrop?.ocr_text, customSpecimenText, specimenTextMode]);

  const togglePinFont = useCallback((family) => {
    setPinnedFonts((prev) => {
      if (prev.includes(family)) return prev.filter((f) => f !== family);
      return [...prev.slice(-3), family];
    });
  }, []);

  const ratedCount = useMemo(
    () => crops.filter((c) => Boolean(labelsByCrop[c.crop_id])).length,
    [crops, labelsByCrop],
  );
  const progressPct = crops.length ? Math.round((ratedCount / crops.length) * 100) : 0;

  const handleExportCsv = useCallback(() => {
    const rows = [["crop_id", "rater", "font", "coherence"]];
    for (const c of crops) {
      const item = labelsByCrop[c.crop_id];
      if (item) {
        rows.push([item.crop_id, item.rater, item.font, item.coherence]);
      }
    }
    const csvText = `${rows.map((r) => r.join(",")).join("\n")}\n`;
    const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `labels_${rater}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [crops, labelsByCrop, rater]);

  const handleFinish = useCallback(async () => {
    if (!window.confirm("Submit your answers? They will be locked and cannot be changed.")) return;
    const res = await fetch("/api/finish", { method: "POST" }).catch(() => null);
    const data = await res?.json().catch(() => null);
    if (res?.ok && data?.receipt) setMe((m) => ({ ...m, receipt: data.receipt }));
    else window.alert(data?.error || "Could not submit. Check your connection and try again.");
  }, []);

  const isSavedCurrent = Boolean(
    currentCrop &&
      labelsByCrop[currentCrop.crop_id] &&
      labelsByCrop[currentCrop.crop_id].font === selectedFont &&
      labelsByCrop[currentCrop.crop_id].coherence === selectedCoherence,
  );

  if (me === undefined) return <Notice title="Loading..." />;
  if (me === null) {
    return (
      <Notice title="Open your personal link">
        <p>
          This form opens only from the personal link in your invitation email. Open that link
          again, in this browser. If it does not work, ask the researchers for a new one.
        </p>
      </Notice>
    );
  }
  if (!me.consented)
    return <ConsentScreen me={me} onAgreed={() => setMe({ ...me, consented: true })} />;
  if (me.receipt) return <ReceiptScreen receipt={me.receipt} />;
  if (!crops.length) return <Notice title="Loading items..." />;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50/80 text-slate-900">
      {/* Top Application Bar */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-xs">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4 px-6 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-white shadow-2xs">
              <Type className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-semibold tracking-tight text-slate-950">
                  Expert-Panel Typography Evaluation
                </h1>
                <Badge variant="secondary" className="text-[11px]">
                  Blind Protocol · Ch. 4 §4.2.3
                </Badge>
                <Badge
                  variant={cropMode === "real" ? "emerald" : "blue"}
                  className="text-[11px]"
                  title={sourceLabel}
                >
                  <Database className="h-3 w-3" />
                  {cropMode === "real" ? "Real Generative Crops" : "Dataset Pipeline PNGs"}
                </Badge>
              </div>
              <p className="text-xs text-slate-500">
                Compare the degraded raster crop against live Google Fonts specimens and record Q1
                (typeface) + Q2 (coherence).
              </p>
            </div>
          </div>

          {/* Right Header Controls: Rater Switcher, Progress & CSV Export */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1">
              <UserCheck className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-xs font-medium text-slate-600">Rater:</span>
              <span className="text-xs font-semibold text-slate-900">{rater}</span>
            </div>

            <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-1.5 shadow-2xs">
              <div className="flex flex-col gap-1 min-w-[140px]">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-600">Progress</span>
                  <span className="font-semibold text-slate-900">
                    {ratedCount} / {crops.length} ({progressPct}%)
                  </span>
                </div>
                <Progress value={progressPct} className="h-1.5" />
              </div>
              <Separator orientation="vertical" className="h-6" />
              <button
                type="button"
                onClick={() => setFilterUnratedOnly((v) => !v)}
                className={cn(
                  "rounded px-2 py-0.5 text-[11px] font-medium transition-colors cursor-pointer",
                  filterUnratedOnly
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200",
                )}
                title="When active, Skip/Next jumps directly to the next unrated crop"
              >
                {filterUnratedOnly ? "Unrated Only" : "All Crops"}
              </button>
              <select
                aria-label="Jump to crop"
                value={currentIndex}
                onChange={(e) => setCurrentIndex(Number(e.target.value))}
                className="text-xs font-medium text-slate-700 bg-transparent focus:outline-none cursor-pointer max-w-[155px]"
              >
                {crops.map((c, idx) => {
                  const done = Boolean(labelsByCrop[c.crop_id]);
                  return (
                    <option key={c.crop_id} value={idx}>
                      {done ? "✓ " : "○ "}#{String(idx + 1).padStart(2, "0")} · {c.crop_id}
                    </option>
                  );
                })}
              </select>
            </div>

            {ratedCount === crops.length && (
              <Button size="sm" onClick={handleFinish}>
                <Check className="h-3.5 w-3.5" />
                Finish and submit
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCsv}
              title="Export current rater's labels.csv"
            >
              <Download className="h-3.5 w-3.5" />
              Export CSV
            </Button>
          </div>
        </div>
      </header>

      {/* Main Split Workspace */}
      <main className="mx-auto grid w-full max-w-[1600px] flex-1 grid-cols-1 gap-6 px-6 py-5 lg:grid-cols-12">
        {/* LEFT COLUMN (7 cols): Target Crop Inspector + Direct Specimen Comparator + Rating Form */}
        <div className="flex flex-col gap-5 lg:col-span-7">
          {/* Card 1: AI / Degraded Crop vs. Live Candidate Specimen Comparator */}
          <Card className="overflow-hidden border-slate-200/90 shadow-xs">
            <CardHeader className="border-b border-slate-100 bg-slate-50/60 py-3.5 px-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="default" className="font-mono text-xs">
                    Item #{String(currentIndex + 1).padStart(2, "0")} / {crops.length}
                  </Badge>
                  <Badge variant="outline" className="font-mono text-xs">
                    crop_id: {currentCrop?.crop_id}
                  </Badge>
                  {currentCrop?.ocr_text && (
                    <Badge variant="secondary" className="text-xs">
                      Text: &ldquo;{currentCrop.ocr_text}&rdquo;
                    </Badge>
                  )}
                  {cropDimensions && (
                    <Badge variant="outline" className="text-[11px] font-mono">
                      {cropDimensions.w}×{cropDimensions.h}px PNG
                    </Badge>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  {isSavedCurrent ? (
                    <Badge variant="emerald">
                      <CheckCircle2 className="h-3 w-3" />
                      Saved ({rater})
                    </Badge>
                  ) : (
                    <Badge variant="amber">Unsaved item</Badge>
                  )}
                </div>
              </div>
            </CardHeader>

            {/* Crop Inspection Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-white px-4 py-2 text-xs">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="font-medium text-slate-500 mr-1">Zoom:</span>
                {[1, 1.5, 2, 2.5].map((z) => (
                  <Button
                    key={z}
                    variant={zoom === z ? "default" : "outline"}
                    size="sm"
                    className="h-7 px-2 text-xs"
                    onClick={() => setZoom(z)}
                  >
                    {Math.round(z * 100)}%
                  </Button>
                ))}
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => setZoom((z) => Math.max(0.75, z - 0.25))}
                  title="Zoom out"
                >
                  <ZoomOut className="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => setZoom((z) => Math.min(3.5, z + 0.25))}
                  title="Zoom in"
                >
                  <ZoomIn className="h-3.5 w-3.5" />
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-1.5">
                <Button
                  variant={invertCrop ? "default" : "outline"}
                  size="sm"
                  className="h-7 px-2.5 text-xs"
                  onClick={() => setInvertCrop((v) => !v)}
                  title="Invert crop luminance polarity (Key: I)"
                >
                  <FlipHorizontal className="h-3.5 w-3.5" />
                  Invert (I)
                </Button>
                <Button
                  variant={highContrastCrop ? "default" : "outline"}
                  size="sm"
                  className="h-7 px-2.5 text-xs"
                  onClick={() => setHighContrastCrop((v) => !v)}
                  title="Boost edge contrast on blurred crops"
                >
                  <Contrast className="h-3.5 w-3.5" />
                  Contrast Boost
                </Button>
                <Button
                  variant={pixelatedCrop ? "default" : "outline"}
                  size="sm"
                  className="h-7 px-2.5 text-xs"
                  onClick={() => setPixelatedCrop((v) => !v)}
                  title="Toggle crisp pixel rendering vs smooth bicubic"
                >
                  <Eye className="h-3.5 w-3.5" />
                  {pixelatedCrop ? "Pixel Grid" : "Smooth"}
                </Button>
                <TabsList className="h-7 p-0.5">
                  {[
                    { id: "checker-dark", label: "Dark Grid" },
                    { id: "checker-light", label: "Light Grid" },
                    { id: "dark", label: "Solid Dark" },
                  ].map((bg) => (
                    <TabsTrigger
                      key={bg.id}
                      active={canvasTheme === bg.id}
                      onClick={() => setCanvasTheme(bg.id)}
                      className="px-2 py-0.5 text-[11px]"
                    >
                      {bg.label}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </div>
            </div>

            <CardContent className="p-0">
              {/* TOP HALF: Target Degraded / AI Raster Crop Viewport */}
              <div
                className={cn(
                  "relative flex min-h-[210px] flex-col items-center justify-center overflow-auto p-6 transition-colors",
                  canvasTheme === "checker-dark" && "bg-checkerboard-dark",
                  canvasTheme === "checker-light" && "bg-checkerboard",
                  canvasTheme === "dark" && "bg-slate-950",
                )}
              >
                <div className="absolute top-3 left-3 flex items-center gap-1.5">
                  <Badge
                    variant="secondary"
                    className="bg-slate-900/80 text-white border-slate-700 text-[11px] backdrop-blur-xs"
                  >
                    TARGET RASTER CROP ({currentCrop?.crop_id}.png)
                  </Badge>
                </div>

                {currentCrop?.crop_url && !cropLoadError ? (
                  <div className="flex items-center justify-center rounded-lg p-2">
                    <img
                      key={currentCrop.crop_url}
                      src={currentCrop.crop_url}
                      alt={`Crop ${currentCrop.crop_id}`}
                      onLoad={(e) => {
                        setCropDimensions({
                          w: e.currentTarget.naturalWidth,
                          h: e.currentTarget.naturalHeight,
                        });
                      }}
                      onError={() => setCropLoadError(true)}
                      style={{
                        transform: `scale(${zoom})`,
                        transformOrigin: "center center",
                        imageRendering: pixelatedCrop ? "pixelated" : "auto",
                        filter: [
                          invertCrop ? "invert(1)" : "",
                          highContrastCrop ? "contrast(2.15)" : "",
                        ]
                          .filter(Boolean)
                          .join(" "),
                      }}
                      className="max-h-[160px] w-auto rounded-sm shadow-md transition-transform duration-150"
                    />
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-slate-600 bg-slate-900/90 px-6 py-4 text-center text-slate-200">
                    <p className="text-xs font-medium text-amber-300">
                      Backend server not running on port 8000 — start{" "}
                      <code>.venv/bin/python src/rater/server.py</code> to load raster PNG crops
                    </p>
                    <span className="text-3xl font-bold tracking-wider">
                      {currentCrop?.ocr_text || "SAMPLE"}
                    </span>
                  </div>
                )}
              </div>

              {/* MIDDLE BAR: Direct Specimen Comparison Controls */}
              <div className="border-t border-b border-slate-200 bg-slate-100/90 px-4 py-2">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <SplitSquareVertical className="h-4 w-4 text-slate-700" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                      Live Specimen Diff (Synced to Crop Text)
                    </span>
                    {hoveredFont && (
                      <Badge variant="blue" className="text-[11px]">
                        Previewing hovered: {hoveredFont}
                      </Badge>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs">
                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-500">Size:</span>
                      <input
                        type="range"
                        min={24}
                        max={72}
                        value={specimenSize}
                        onChange={(e) => setSpecimenSize(Number(e.target.value))}
                        className="w-20 accent-slate-900 cursor-pointer"
                      />
                      <span className="font-mono text-[11px] text-slate-700 w-8">
                        {specimenSize}px
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-500">Tracking:</span>
                      <input
                        type="range"
                        min={-6}
                        max={16}
                        value={specimenTracking}
                        onChange={(e) => setSpecimenTracking(Number(e.target.value))}
                        className="w-16 accent-slate-900 cursor-pointer"
                      />
                      <span className="font-mono text-[11px] text-slate-700 w-10">
                        {specimenTracking > 0 ? `+${specimenTracking}` : specimenTracking}%
                      </span>
                    </div>

                    <TabsList className="h-7 p-0.5">
                      {[
                        { id: "crop", label: "Crop Text" },
                        { id: "upper", label: "UPPER" },
                        { id: "lower", label: "lower" },
                        { id: "anatomy", label: "+ Glyphs" },
                      ].map((m) => (
                        <TabsTrigger
                          key={m.id}
                          active={specimenTextMode === m.id}
                          onClick={() => setSpecimenTextMode(m.id)}
                          className="px-2 py-0.5 text-[11px]"
                        >
                          {m.label}
                        </TabsTrigger>
                      ))}
                    </TabsList>
                  </div>
                </div>
              </div>

              {/* BOTTOM HALF: Active Candidate Specimen + Pinned Finalists Tray */}
              <div className="bg-white p-4 space-y-3">
                {/* Primary Active Candidate Specimen */}
                <div
                  className={cn(
                    "rounded-lg border p-3.5 transition-all",
                    activeCompareFontObj
                      ? "border-slate-300 bg-slate-50/60"
                      : selectedFont === "unknown"
                        ? "border-rose-200 bg-rose-50/40"
                        : "border-dashed border-slate-200 bg-slate-50/30",
                  )}
                >
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-700">
                        {hoveredFont
                          ? `Hovered Candidate: ${activeCompareFontObj?.family}`
                          : selectedFont === "unknown"
                            ? "Q1 Selection: Unknown / Hallucinated Typeface"
                            : activeCompareFontObj
                              ? `Q1 Selected Specimen: ${activeCompareFontObj.family}`
                              : "No Q1 typeface selected yet — click or hover any font on the right"}
                      </span>
                      {activeCompareFontObj && (
                        <Badge
                          variant={
                            CLASS_BADGE_VARIANT[activeCompareFontObj.family_class] || "secondary"
                          }
                        >
                          {activeCompareFontObj.family_class}
                        </Badge>
                      )}
                    </div>
                    {activeCompareFontObj && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 px-2 text-xs"
                        onClick={() => togglePinFont(activeCompareFontObj.family)}
                      >
                        <Pin className="h-3 w-3" />
                        {pinnedFonts.includes(activeCompareFontObj.family)
                          ? "Unpin"
                          : "Pin to tray"}
                      </Button>
                    )}
                  </div>

                  {activeCompareFontObj ? (
                    <div
                      className="overflow-x-auto py-1 text-slate-950 select-all"
                      style={{
                        fontFamily: `"Palette_${activeCompareFontObj.font_id}", sans-serif`,
                        fontSize: `${specimenSize}px`,
                        letterSpacing: `${specimenTracking * 0.01}em`,
                        lineHeight: 1.2,
                      }}
                    >
                      {comparisonText}
                    </div>
                  ) : selectedFont === "unknown" ? (
                    <p className="text-xs text-rose-700">
                      Marked as <strong>Unknown / hallucinated (no palette match)</strong>. You can
                      still hover or pin fonts from the palette browser to verify no match exists.
                    </p>
                  ) : (
                    <p className="text-xs text-slate-500">
                      Hover over any font card in the <strong>Palette Reference Browser</strong> on
                      the right to preview it here in{" "}
                      <span className="font-mono font-medium text-slate-700">
                        &ldquo;{comparisonText}&rdquo;
                      </span>
                      , or pin 2–4 finalist fonts below for stacked comparison.
                    </p>
                  )}
                </div>

                {/* Pinned Finalists Comparison Tray */}
                {pinnedFonts.length > 0 && (
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span className="font-medium flex items-center gap-1.5">
                        <Layers className="h-3.5 w-3.5 text-slate-500" />
                        Pinned Comparison Tray ({pinnedFonts.length}/4) — click any row to select as
                        Q1:
                      </span>
                      <button
                        type="button"
                        onClick={() => setPinnedFonts([])}
                        className="text-[11px] text-slate-400 hover:text-slate-700 cursor-pointer"
                      >
                        Clear tray
                      </button>
                    </div>
                    <div className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
                      {pinnedFonts.map((fam) => {
                        const fObj = palette.find((f) => f.family === fam);
                        if (!fObj) return null;
                        const isChosen = selectedFont === fObj.family;
                        return (
                          <div
                            key={fObj.font_id}
                            className={cn(
                              "group flex items-center justify-between gap-2 rounded-md border px-3 py-2 text-left transition-all",
                              isChosen
                                ? "border-slate-900 bg-slate-900/5 ring-1 ring-slate-900"
                                : "border-slate-200 bg-white hover:border-slate-400",
                            )}
                          >
                            <button
                              type="button"
                              onClick={() => setSelectedFont(fObj.family)}
                              className="min-w-0 flex-1 text-left cursor-pointer"
                            >
                              <div className="flex items-center gap-1.5">
                                <span className="text-xs font-semibold text-slate-800 truncate">
                                  {fObj.family}
                                </span>
                                <Badge
                                  variant={CLASS_BADGE_VARIANT[fObj.family_class] || "secondary"}
                                  className="text-[10px] px-1.5 py-0"
                                >
                                  {fObj.family_class}
                                </Badge>
                              </div>
                              <div
                                className="truncate text-slate-900 mt-0.5"
                                style={{
                                  fontFamily: `"Palette_${fObj.font_id}", sans-serif`,
                                  fontSize: "22px",
                                  letterSpacing: `${specimenTracking * 0.01}em`,
                                }}
                              >
                                {comparisonText}
                              </div>
                            </button>
                            <button
                              type="button"
                              onClick={() => togglePinFont(fObj.family)}
                              className="text-slate-400 hover:text-slate-700 p-1 cursor-pointer"
                              title="Remove from comparison tray"
                            >
                              <X className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Card 2: Structured Q1 & Q2 Rating Controls */}
          <Card className="border-slate-200/90 shadow-xs">
            <CardContent className="p-5 space-y-5">
              {/* Q1: Closest Palette Typeface */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">
                      Q1 · Closest Palette Typeface
                    </h2>
                    <p className="text-xs text-slate-500">
                      Select one of the 80 Google Fonts from the palette, or mark Unknown /
                      hallucinated if no typeface matches.
                    </p>
                  </div>
                  {selectedFont && (
                    <Badge variant={selectedFont === "unknown" ? "destructive" : "default"}>
                      {selectedFont === "unknown" ? "Unknown / hallucinated" : selectedFont}
                    </Badge>
                  )}
                </div>

                <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-12">
                  {/* Searchable Combobox for 80 Palette Fonts */}
                  <div className="relative sm:col-span-7" ref={comboRef}>
                    <button
                      type="button"
                      onClick={() => setComboOpen((o) => !o)}
                      className={cn(
                        "flex h-10 w-full items-center justify-between rounded-md border px-3 py-2 text-sm transition-colors cursor-pointer",
                        selectedPaletteObj
                          ? "border-slate-900 bg-slate-900/5 font-medium text-slate-900"
                          : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50",
                      )}
                    >
                      <span className="truncate">
                        {selectedPaletteObj
                          ? `${selectedPaletteObj.family} (${selectedPaletteObj.family_class})`
                          : "Search or select from 80 palette fonts..."}
                      </span>
                      <ChevronDown className="h-4 w-4 text-slate-400 shrink-0" />
                    </button>

                    {comboOpen && (
                      <div className="absolute left-0 right-0 z-40 mt-1 rounded-lg border border-slate-200 bg-white p-2 shadow-xl">
                        <div className="relative mb-2">
                          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
                          <Input
                            placeholder="Filter by family name or class..."
                            value={comboQuery}
                            onChange={(e) => setComboQuery(e.target.value)}
                            className="pl-8 h-8 text-xs"
                            autoFocus
                          />
                        </div>
                        <div className="max-h-60 overflow-y-auto divide-y divide-slate-100">
                          {filteredComboFonts.map((f) => {
                            const active = selectedFont === f.family;
                            return (
                              <button
                                key={f.font_id}
                                type="button"
                                onClick={() => {
                                  setSelectedFont(f.family);
                                  setComboOpen(false);
                                  setComboQuery("");
                                }}
                                className={cn(
                                  "flex w-full items-center justify-between gap-2 px-2.5 py-2 text-left text-xs transition-colors hover:bg-slate-100 cursor-pointer",
                                  active && "bg-slate-100 font-semibold",
                                )}
                              >
                                <div className="min-w-0 flex-1">
                                  <div className="flex items-center gap-1.5">
                                    <span className="font-medium text-slate-900">{f.family}</span>
                                    <Badge
                                      variant={CLASS_BADGE_VARIANT[f.family_class] || "secondary"}
                                      className="text-[10px] px-1.5 py-0"
                                    >
                                      {f.family_class}
                                    </Badge>
                                  </div>
                                  <div
                                    className="truncate text-base text-slate-800 mt-0.5"
                                    style={{
                                      fontFamily: `"Palette_${f.font_id}", sans-serif`,
                                    }}
                                  >
                                    {comparisonText}
                                  </div>
                                </div>
                                {active && <Check className="h-4 w-4 text-slate-900 shrink-0" />}
                              </button>
                            );
                          })}
                          {filteredComboFonts.length === 0 && (
                            <div className="py-4 text-center text-xs text-slate-400">
                              No matching palette font. Use Unknown / hallucinated if off-palette.
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Dedicated Unknown / Hallucinated Button */}
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFont("unknown");
                      setComboOpen(false);
                    }}
                    className={cn(
                      "sm:col-span-5 flex h-10 items-center justify-center gap-2 rounded-md border px-3 text-xs font-medium transition-all cursor-pointer",
                      selectedFont === "unknown"
                        ? "border-rose-600 bg-rose-600 text-white shadow-xs"
                        : "border-rose-200 bg-rose-50/70 text-rose-800 hover:bg-rose-100",
                    )}
                  >
                    <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                    <span>Unknown / Hallucinated (Key: U)</span>
                  </button>
                </div>
              </div>

              <Separator />

              {/* Q2: Typographic Coherence */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">
                      Q2 · Typographic Coherence (Intra-Crop Homogeneity)
                    </h2>
                    <p className="text-xs text-slate-500">
                      Are all characters in the crop rendered in one consistent typeface, or does
                      the font switch mid-crop?
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
                  {COHERENCE_OPTIONS.map((opt) => {
                    const active = selectedCoherence === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setSelectedCoherence(opt.value)}
                        className={cn(
                          "flex flex-col justify-between rounded-lg border p-3 text-left transition-all cursor-pointer",
                          active
                            ? opt.activeClass
                            : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/60",
                        )}
                      >
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <span className="text-xs font-semibold text-slate-900">{opt.label}</span>
                          <kbd className="rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-600">
                            {opt.keyHint}
                          </kbd>
                        </div>
                        <p className="text-[11px] leading-snug text-slate-600">{opt.desc}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              <Separator />

              {/* Action Bar */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePrev}
                    disabled={currentIndex === 0}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Prev
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleNextWithoutSave}
                    disabled={currentIndex >= crops.length - 1}
                  >
                    Skip / Next
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedFont("");
                      setSelectedCoherence("");
                    }}
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    Reset
                  </Button>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 hidden sm:inline">
                    {saveState === "saving"
                      ? "Saving..."
                      : saveState === "error"
                        ? "Not saved: check your connection and press Save again"
                        : isSavedCurrent
                          ? "Saved"
                          : "Select Q1 & Q2 then press Enter"}
                  </span>
                  <Button
                    variant="default"
                    size="default"
                    disabled={!canSaveCurrent}
                    onClick={handleSaveAndNext}
                    className="font-semibold"
                  >
                    <Check className="h-4 w-4" />
                    Save & Next (Enter)
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* RIGHT COLUMN (5 cols): Interactive 80-Font Palette Specimen Browser */}
        <div className="lg:col-span-5">
          <Card className="flex h-[calc(100vh-5.75rem)] min-h-[680px] flex-col border-slate-200/90 shadow-xs sticky top-[4.5rem]">
            <CardHeader className="border-b border-slate-100 pb-3 pt-4 px-4 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-sm font-semibold flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-slate-700" />
                    80-Font Palette Specimen Browser
                  </CardTitle>
                  <CardDescription className="mt-0.5">
                    Hover any card to live-diff against the crop; click to select as Q1.
                  </CardDescription>
                </div>
                <Badge variant="outline" className="text-xs font-mono">
                  {filteredBrowserFonts.length} / 80
                </Badge>
              </div>

              {/* Search + Custom Text Inputs */}
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
                  <Input
                    placeholder="Search font family..."
                    value={browserSearch}
                    onChange={(e) => setBrowserSearch(e.target.value)}
                    className="pl-8 h-8 text-xs"
                  />
                </div>
                <Input
                  placeholder={`Override text ("${currentCrop?.ocr_text || "sample"}")`}
                  value={customSpecimenText}
                  onChange={(e) => {
                    setCustomSpecimenText(e.target.value);
                    if (e.target.value.trim()) {
                      setSpecimenTextMode("custom");
                    } else {
                      setSpecimenTextMode("crop");
                    }
                  }}
                  className="h-8 text-xs"
                />
              </div>

              {/* Category Filter Tabs */}
              <TabsList className="w-full grid grid-cols-5 h-8">
                {CLASS_TABS.map((tab) => (
                  <TabsTrigger
                    key={tab.id}
                    active={browserClass === tab.id}
                    onClick={() => setBrowserClass(tab.id)}
                    className="text-[11px] px-1.5"
                  >
                    {tab.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </CardHeader>

            {/* Scrollable Specimen Cards */}
            <CardContent className="flex-1 overflow-y-auto p-3 space-y-2">
              {filteredBrowserFonts.map((f) => {
                const isSelected = selectedFont === f.family;
                const isPinned = pinnedFonts.includes(f.family);
                return (
                  <div
                    key={f.font_id}
                    onMouseEnter={() => setHoveredFont(f.family)}
                    onMouseLeave={() => setHoveredFont(null)}
                    className={cn(
                      "group rounded-lg border p-3 transition-all",
                      isSelected
                        ? "border-slate-900 bg-slate-900/5 ring-1 ring-slate-900 shadow-2xs"
                        : "border-slate-200 bg-white hover:border-slate-400 hover:shadow-2xs",
                    )}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <button
                        type="button"
                        onClick={() => setSelectedFont(f.family)}
                        className="flex items-center gap-2 min-w-0 flex-1 text-left cursor-pointer"
                      >
                        <span className="text-xs font-semibold text-slate-900 truncate">
                          {f.family}
                        </span>
                        <Badge
                          variant={CLASS_BADGE_VARIANT[f.family_class] || "secondary"}
                          className="text-[10px] px-1.5 py-0"
                        >
                          {f.family_class}
                        </Badge>
                        <span className="text-[10px] font-mono text-slate-400">
                          #{f.popularity}
                        </span>
                      </button>

                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => togglePinFont(f.family)}
                          className={cn(
                            "inline-flex items-center gap-1 rounded px-2 py-0.5 text-[11px] font-medium transition-colors cursor-pointer",
                            isPinned
                              ? "bg-slate-900 text-white"
                              : "bg-slate-100 text-slate-600 hover:bg-slate-200",
                          )}
                          title="Pin to side-by-side comparison tray"
                        >
                          <Pin className="h-3 w-3" />
                          {isPinned ? "Pinned" : "Pin"}
                        </button>
                        {isSelected && (
                          <Badge variant="default" className="text-[10px]">
                            Selected Q1
                          </Badge>
                        )}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => setSelectedFont(f.family)}
                      className="w-full text-left cursor-pointer"
                    >
                      {/* Synced Crop Text Specimen */}
                      <div
                        className="truncate text-slate-950 py-0.5"
                        style={{
                          fontFamily: `"Palette_${f.font_id}", sans-serif`,
                          fontSize: "26px",
                          letterSpacing: `${specimenTracking * 0.01}em`,
                          lineHeight: 1.2,
                        }}
                      >
                        {comparisonText}
                      </div>

                      {/* Diagnostic Glyph Anatomy Strip */}
                      <div
                        className="truncate text-slate-500 border-t border-slate-100 pt-1 mt-1"
                        style={{
                          fontFamily: `"Palette_${f.font_id}", sans-serif`,
                          fontSize: "14px",
                        }}
                      >
                        Aa Bb Cc Gg Jj M N Qq Rr Ww a e g r t y 0123456789
                      </div>
                    </button>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
