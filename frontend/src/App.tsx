import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import mermaid from "mermaid";

type IconName =
  | "sparkle"
  | "folder"
  | "settings"
  | "help"
  | "plus"
  | "upload"
  | "image"
  | "chevron"
  | "play"
  | "export"
  | "more"
  | "zoomIn"
  | "zoomOut"
  | "fit"
  | "close"
  | "history"
  | "download"
  | "edit"
  | "maximize"
  | "minimize";

type ExtractionResponse = { mermaid: string; provider: string };

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

const Icon = ({ name, size = 18 }: { name: IconName; size?: number }) => {
  const props = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };

  const paths: Record<IconName, ReactNode> = {
    sparkle: (
      <>
        <path d="m12 3-1.25 5.75L5 10l5.75 1.25L12 17l1.25-5.75L19 10l-5.75-1.25L12 3Z" />
        <path d="m19 16-.55 2.45L16 19l2.45.55L19 22l.55-2.45L22 19l-2.45-.55L19 16Z" />
      </>
    ),
    folder: (
      <path d="M3 6.5A2.5 2.5 0 0 1 5.5 4h4l2 2h7A2.5 2.5 0 0 1 21 8.5v9a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5v-11Z" />
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.12 2.12-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20.5h-3v-.28A1.7 1.7 0 0 0 10.68 18.66a1.7 1.7 0 0 0-1.88.34l-.06.06-2.12-2.12.06-.06A1.7 1.7 0 0 0 7.02 15a1.7 1.7 0 0 0-1.56-1.03H5.2v-3h.26A1.7 1.7 0 0 0 7.02 9.94a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.12-2.12.06.06a1.7 1.7 0 0 0 1.88.34 1.7 1.7 0 0 0 1.03-1.56V4.5h3v.22a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06L19.8 8l-.06.06a1.7 1.7 0 0 0-.34 1.88 1.7 1.7 0 0 0 1.56 1.03h.26v3h-.26A1.7 1.7 0 0 0 19.4 15Z" />
      </>
    ),
    help: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M9.5 9a2.6 2.6 0 1 1 4.2 2.05c-.92.7-1.7 1.17-1.7 2.45" />
        <path d="M12 17h.01" />
      </>
    ),
    plus: <path d="M12 5v14M5 12h14" />,
    upload: (
      <>
        <path d="M12 16V4" />
        <path d="m8 8 4-4 4 4" />
        <path d="M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
      </>
    ),
    image: (
      <>
        <rect x="3" y="4" width="18" height="16" rx="2" />
        <circle cx="8.5" cy="9" r="1.5" />
        <path d="m21 15-4.5-4.5L7 20" />
      </>
    ),
    chevron: <path d="m6 9 6 6 6-6" />,
    play: <path d="m8 5 11 7-11 7V5Z" />,
    export: (
      <>
        <path d="M12 3v12" />
        <path d="m8 7 4-4 4 4" />
        <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7" />
      </>
    ),
    more: (
      <>
        <circle cx="5" cy="12" r="1" fill="currentColor" />
        <circle cx="12" cy="12" r="1" fill="currentColor" />
        <circle cx="19" cy="12" r="1" fill="currentColor" />
      </>
    ),
    zoomIn: (
      <>
        <circle cx="11" cy="11" r="6" />
        <path d="M11 8v6M8 11h6M20 20l-4.2-4.2" />
      </>
    ),
    zoomOut: (
      <>
        <circle cx="11" cy="11" r="6" />
        <path d="M8 11h6M20 20l-4.2-4.2" />
      </>
    ),
    fit: <path d="M8 3H3v5M16 3h5v5M21 16v5h-5M3 16v5h5" />,
    close: <path d="m6 6 12 12M18 6 6 18" />,
    history: (
      <>
        <path d="M3 12a9 9 0 1 0 3-6.7" />
        <path d="M3 4v5h5M12 7v5l3 2" />
      </>
    ),
    download: (
      <>
        <path d="M12 3v12" />
        <path d="m8 11 4 4 4-4" />
        <path d="M5 20h14" />
      </>
    ),
    edit: (
      <>
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
      </>
    ),
    maximize: (
      <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
    ),
    minimize: (
      <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
    ),
  };

  return <svg {...props}>{paths[name]}</svg>;
};

const defaultSource = `flowchart LR
  start([Start]) --> decision{Is request complete?}
  decision -->|Yes| review[Send to review]
  decision -->|No| details[Request details]
  classDef default fill:#fff,stroke:#bbb5cb,color:#413c55,stroke-width:1.2px;
  classDef decision fill:#fff,stroke:#a37bc6,color:#413c55,stroke-width:1.4px;
  class decision decision;`;

mermaid.initialize({
  startOnLoad: false,
  securityLevel: "strict",
  theme: "base",
  themeVariables: {
    primaryColor: "#ffffff",
    primaryBorderColor: "#bbb5cb",
    lineColor: "#716e82",
    primaryTextColor: "#413c55",
    fontFamily: "DM Sans, sans-serif",
  },
  flowchart: { htmlLabels: true, curve: "basis" },
});

const filenameFor = (name: string) =>
  name.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").toLowerCase() || "diagram";

const renderSvg = (source: string) =>
  mermaid.render(`export-${crypto.randomUUID()}`, source).then(({ svg }) => svg);

const downloadBlob = (blob: Blob, name: string) => {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
};

async function exportDiagram(source: string, name: string, format: "svg" | "png") {
  const svg = await renderSvg(source);
  if (format === "svg") {
    downloadBlob(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }), `${filenameFor(name)}.svg`);
    return;
  }
  const image = new Image();
  const svgUrl = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }));
  await new Promise<void>((resolve, reject) => {
    image.onload = () => resolve();
    image.onerror = () => reject(new Error("The diagram could not be converted to PNG."));
    image.src = svgUrl;
  });
  const viewBox = svg.match(/viewBox="[^"]*\s([^\s"]+)\s([^\s"]+)"/);
  const width = Math.max(1, Math.round(Number(viewBox?.[1]) || image.naturalWidth || 1200));
  const height = Math.max(1, Math.round(Number(viewBox?.[2]) || image.naturalHeight || 800));
  const canvas = document.createElement("canvas");
  canvas.width = width * 2;
  canvas.height = height * 2;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("Your browser could not create a PNG export.");
  context.fillStyle = "#fdfcfb";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  URL.revokeObjectURL(svgUrl);
  await new Promise<void>((resolve) =>
    canvas.toBlob((blob) => {
      if (blob) downloadBlob(blob, `${filenameFor(name)}.png`);
      resolve();
    }, "image/png"),
  );
}

function Diagram({
  source,
  full = false,
  onEdit,
}: {
  source: string;
  full?: boolean;
  onEdit?: () => void;
}) {
  const canvas = useRef<HTMLDivElement>(null);
  const target = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(100);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [dragStart, setDragStart] = useState<{ x: number; y: number; offsetX: number; offsetY: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    mermaid
      .render(`diagram-${crypto.randomUUID()}`, source)
      .then(({ svg, bindFunctions }) => {
        if (cancelled || !target.current) return;
        setError(null);
        target.current.innerHTML = svg;
        bindFunctions?.(target.current);
      })
      .catch(() => !cancelled && setError("This Mermaid source could not be rendered. Check its syntax and try again."));
    return () => {
      cancelled = true;
    };
  }, [source]);

  const scale = (value: number) => setZoom(Math.min(180, Math.max(40, value)));
  const resetView = () => {
    setZoom(100);
    setOffset({ x: 0, y: 0 });
  };
  const toggleFullscreen = async () => {
    if (document.fullscreenElement) {
      await document.exitFullscreen();
      return;
    }
    await canvas.current?.requestFullscreen();
  };

  return (
    <div
      ref={canvas}
      className={`diagram-canvas${full ? " full-canvas" : ""}${dragStart ? " is-panning" : ""}`}
      onWheel={(event) => {
        event.preventDefault();
        scale(zoom + (event.deltaY < 0 ? 10 : -10));
      }}
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        event.currentTarget.setPointerCapture(event.pointerId);
        setDragStart({ x: event.clientX, y: event.clientY, offsetX: offset.x, offsetY: offset.y });
      }}
      onPointerMove={(event) => {
        if (!dragStart) return;
        setOffset({
          x: dragStart.offsetX + event.clientX - dragStart.x,
          y: dragStart.offsetY + event.clientY - dragStart.y,
        });
      }}
      onPointerUp={() => setDragStart(null)}
      onPointerCancel={() => setDragStart(null)}
    >
      <div className="mermaid-viewport">
        <div
          ref={target}
          className="mermaid-render"
          style={{ transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom / 100})` }}
        />
        {error && <p className="render-error">{error}</p>}
      </div>
      <div className="canvas-controls">
        {onEdit && (
          <>
            <button
              aria-label="Open editor"
              title="Open editor to modify Mermaid code directly"
              onPointerDown={(event) => event.stopPropagation()}
              onClick={onEdit}
            >
              <Icon name="edit" size={15} />
            </button>
            <i />
          </>
        )}
        <button
          aria-label="Zoom out"
          title="Zoom out"
          onPointerDown={(event) => event.stopPropagation()}
          onClick={() => scale(zoom - 10)}
        >
          <Icon name="zoomOut" size={16} />
        </button>
        <span>{zoom}%</span>
        <button
          aria-label="Zoom in"
          title="Zoom in"
          onPointerDown={(event) => event.stopPropagation()}
          onClick={() => scale(zoom + 10)}
        >
          <Icon name="zoomIn" size={16} />
        </button>
        <i />
        <button
          aria-label="Reset diagram view"
          title="Reset zoom & pan"
          onPointerDown={(event) => event.stopPropagation()}
          onClick={resetView}
        >
          <Icon name="fit" size={16} />
        </button>
        <button
          aria-label="Open diagram fullscreen"
          title="Fullscreen preview"
          onPointerDown={(event) => event.stopPropagation()}
          onClick={toggleFullscreen}
        >
          <Icon name="maximize" size={16} />
        </button>
      </div>
    </div>
  );
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [source, setSource] = useState<string | null>(null);
  const [sourceDraft, setSourceDraft] = useState(defaultSource);
  const [editorOpen, setEditorOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [message, setMessage] = useState("Upload an image to get started.");
  const [notice, setNotice] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  const flash = (text: string) => {
    setNotice(text);
    window.setTimeout(() => setNotice(null), 2600);
  };

  const selectFile = (selected?: File) => {
    if (!selected) return;
    if (selected.size > 10 * 1024 * 1024) {
      setMessage("Choose an image smaller than 10 MB.");
      return;
    }
    setFile(selected);
    setSource(null);
    setMessage(`${selected.name} is ready to analyze.`);
  };

  const analyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setMessage("Reconstructing your diagram…");
    try {
      const form = new FormData();
      form.append("image", file);
      const response = await fetch(`${API_BASE_URL}/v1/diagrams:extract`, { method: "POST", body: form });
      const payload = (await response.json().catch(() => null)) as ExtractionResponse | { detail?: string } | null;
      if (!response.ok || !payload || !("mermaid" in payload)) {
        throw new Error(
          payload && "detail" in payload && payload.detail
            ? payload.detail
            : "We couldn't extract a diagram from that image. Please try another image.",
        );
      }
      setSource(payload.mermaid);
      setSourceDraft(payload.mermaid);
      setMessage(`Diagram reconstructed with ${payload.provider}.`);
      flash("Diagram reconstructed successfully!");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "We couldn't analyze that image. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const openEditor = () => {
    setSourceDraft(source ?? defaultSource);
    setEditorOpen(true);
  };

  const saveSource = () => {
    setSource(sourceDraft);
    setEditorOpen(false);
    flash("Diagram updated from Mermaid source");
  };

  const download = async (format: "svg" | "png") => {
    if (!source) return;
    try {
      await exportDiagram(source, file?.name ?? "diagram", format);
      setMessage(`${format.toUpperCase()} export downloaded.`);
      flash(`${format.toUpperCase()} downloaded`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The diagram could not be exported.");
    } finally {
      setExportOpen(false);
    }
  };

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setExportOpen(false);
        setEditorOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const handleTextareaKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      saveSource();
      return;
    }
    if (e.key === "Tab") {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const val = textarea.value;
      const updated = val.substring(0, start) + "  " + val.substring(end);
      setSourceDraft(updated);
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      });
    }
  };

  return (
    <main className="app-shell">
      <section className="content">
        <header className="topbar">
          <div className="brand">
            <span className="brand-mark">
              <Icon name="sparkle" size={18} />
            </span>
            <span>diagramflow</span>
          </div>
          <div className="top-actions">
            <span className="saved-dot">{source ? "Diagram ready" : "New diagram"}</span>
            <div className="export-menu">
              <button
                className="export-button"
                disabled={!source}
                aria-haspopup="menu"
                aria-expanded={exportOpen}
                onClick={() => setExportOpen((open) => !open)}
              >
                Export <Icon name="export" size={16} />
              </button>
              {exportOpen && (
                <div className="export-popover" role="menu">
                  <button role="menuitem" onClick={() => download("png")}>
                    <Icon name="image" size={15} /> Export PNG
                  </button>
                  <button role="menuitem" onClick={() => download("svg")}>
                    <Icon name="download" size={15} /> Export SVG
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className="workspace">
          <section className="intro">
            <div className="eyebrow">FROM PHOTO TO FLOW</div>
            <h1>
              Turn your sketch into
              <br />
              <em>something you can use.</em>
            </h1>
            <p>Drop in a photo of your whiteboard or hand-drawn diagram. We’ll reconstruct it into an editable flow.</p>
          </section>

          <section className="editor-layout">
            <div className="source-panel panel">
              <div className="panel-title">
                <div>
                  <span className="step">01</span>
                  <h2>Your source</h2>
                </div>
                <button className="small-link" onClick={() => input.current?.click()}>
                  Browse
                </button>
              </div>
              <input
                ref={input}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                hidden
                onChange={(event) => selectFile(event.target.files?.[0])}
              />
              <button
                className="upload-zone"
                onClick={() => input.current?.click()}
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault();
                  selectFile(event.dataTransfer.files[0]);
                }}
              >
                <span className="upload-icon">
                  <Icon name={file ? "image" : "upload"} size={22} />
                </span>
                {file ? (
                  <>
                    <strong>{file.name}</strong>
                    <span>Ready to analyze</span>
                  </>
                ) : (
                  <>
                    <strong>Drop your image here</strong>
                    <span>JPG, PNG, or WebP · up to 10 MB</span>
                  </>
                )}
              </button>
              <div className="tip">
                <span className="tip-spark">✦</span>
                <p>
                  <b>For best results</b>
                  <br />
                  Use a well-lit, overhead photo with clear lines and labels.
                </p>
              </div>
              <button className="analyze" onClick={analyze} disabled={!file || isAnalyzing}>
                <Icon name="sparkle" size={16} />
                {isAnalyzing ? "Analyzing…" : "Analyze diagram"}
              </button>
            </div>

            <div className="canvas-panel panel">
              <div className="canvas-header">
                <div>
                  <span className="step">02</span>
                  <h2>Reconstructed diagram</h2>
                </div>
                <div className="canvas-header-actions">
                  <button
                    className="edit-button"
                    onClick={openEditor}
                    title="Open editor to modify Mermaid code directly"
                  >
                    <Icon name="edit" size={13} /> Open editor
                  </button>
                  <span className="status">
                    <i /> {isAnalyzing ? "Analyzing" : source ? "Ready" : "Waiting for image"}
                  </span>
                </div>
              </div>

              {source ? (
                <Diagram source={source} onEdit={openEditor} />
              ) : (
                <div className="diagram-empty">
                  <Icon name="upload" size={24} />
                  <strong>
                    {isAnalyzing ? "Reconstructing your diagram…" : "Upload a photo to reconstruct your diagram"}
                  </strong>
                  <span>{message}</span>
                  {!isAnalyzing && (
                    <button
                      className="edit-button"
                      style={{ marginTop: "10px" }}
                      onClick={openEditor}
                      title="Open editor to create or modify Mermaid diagram directly"
                    >
                      <Icon name="edit" size={13} /> Open Mermaid editor
                    </button>
                  )}
                </div>
              )}

              <div className="canvas-footer">
                <div className="legend">
                  <span className="legend-node" /> Mermaid source <span className="legend-arrow">→</span> Rendered SVG
                </div>
                <div className="canvas-actions">
                  {source && <span className="pan-hint">Drag to pan · Scroll to zoom</span>}
                  <button
                    className="edit-button"
                    onClick={openEditor}
                    title="Open editor to modify Mermaid code directly"
                  >
                    <Icon name="edit" size={13} /> Open editor
                  </button>
                </div>
              </div>
            </div>
          </section>

          <p className="privacy">
            <span>◈</span> The backend processes the image only for this extraction request.
          </p>
        </div>
      </section>

      {editorOpen && (
        <div
          className={`editor-overlay${isMaximized ? " is-maximized" : ""}`}
          role="dialog"
          aria-modal="true"
          aria-label="Diagram editor"
        >
          <section className={`editor-modal${isMaximized ? " is-maximized" : ""}`}>
            <header>
              <div>
                <span className="step">EDIT MERMAID SOURCE</span>
                <h2>{file?.name ? `Editing ${file.name}` : "Direct Mermaid Editor"}</h2>
              </div>
              <div className="editor-header-actions">
                <button
                  className="icon-button"
                  aria-label={isMaximized ? "Restore window" : "Expand to full page"}
                  title={isMaximized ? "Restore window" : "Expand to full page"}
                  onClick={() => setIsMaximized((max) => !max)}
                >
                  <Icon name={isMaximized ? "minimize" : "maximize"} size={16} />
                </button>
                <button
                  className="close-editor"
                  aria-label="Close editor"
                  title="Close (Esc)"
                  onClick={() => setEditorOpen(false)}
                >
                  <Icon name="close" size={18} />
                </button>
              </div>
            </header>

            <div className="editor-body">
              <div className="source-editor">
                <div className="source-editor-header">
                  <span>Mermaid source</span>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button
                      className="small-link"
                      type="button"
                      onClick={() => setSourceDraft(defaultSource)}
                      title="Load starter flowchart template"
                    >
                      Load template
                    </button>
                    {source && (
                      <button
                        className="small-link"
                        type="button"
                        onClick={() => setSourceDraft(source)}
                        title="Reset changes back to current diagram"
                      >
                        Reset
                      </button>
                    )}
                  </div>
                </div>
                <textarea
                  value={sourceDraft}
                  onChange={(event) => setSourceDraft(event.target.value)}
                  onKeyDown={handleTextareaKeyDown}
                  placeholder="Type your Mermaid syntax here..."
                  spellCheck="false"
                />
              </div>

              <div className="full-preview">
                <div className="preview-heading">
                  <span>Live preview</span>
                  <span>Updates automatically · Scroll to zoom · Drag to pan</span>
                </div>
                <Diagram source={sourceDraft} full />
              </div>
            </div>

            <footer>
              <div className="footer-hint">
                <span>
                  Tip: Press <strong>Ctrl+Enter</strong> to save · <strong>Tab</strong> to indent · <strong>Esc</strong> to close
                </span>
              </div>
              <div style={{ display: "flex", gap: "9px" }}>
                <button className="cancel-button" onClick={() => setEditorOpen(false)}>
                  Cancel
                </button>
                <button className="save-button" onClick={saveSource}>
                  Save diagram
                </button>
              </div>
            </footer>
          </section>
        </div>
      )}

      {notice && <div className="toast">{notice}</div>}
    </main>
  );
}

export default App;
