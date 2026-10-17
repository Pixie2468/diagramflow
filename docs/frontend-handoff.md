# Frontend integration handoff

The backend is ready at `POST /v1/diagrams:extract`. During local development it runs without credentials and returns a deterministic `mock` result; configure `GEMINI_API_KEY` to use Gemma 4.

## Run the API

```bash
uv run --directory backend uvicorn backend.main:app --reload
```

The default browser allowlist is `http://localhost:5173`. Set `CORS_ORIGINS` to a comma-separated list if the frontend runs elsewhere.

## Request

Send `multipart/form-data` with a single `image` field. The server accepts valid PNG, JPEG, and WebP image bytes up to 10 MB. Its decoded format—not a client-provided MIME label—is authoritative, so a valid WebP will work even when a client labels it `application/octet-stream`.

```ts
const body = new FormData();
body.append("image", file);

const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/v1/diagrams:extract`, {
  method: "POST",
  body,
});

if (!response.ok) throw new Error((await response.json()).detail);
const extraction = await response.json();
```

For local Vite use `VITE_API_BASE_URL=http://localhost:8000`.

## Response contract

```ts
type Confidence = "high" | "low";
type ShapeType = "rectangle" | "rounded" | "diamond" | "cylinder";

type DiagramGraph = {
  direction: "TD" | "LR" | "BT" | "RL";
  nodes: Array<{
    id: string;
    label: string;
    shape_type: ShapeType;
    bounding_box?: { x_min: number; y_min: number; x_max: number; y_max: number };
  }>;
  edges: Array<{
    source: string;
    target: string;
    label?: string;
    confidence: Confidence;
    alternatives: string[];
  }>;
};

type DiagramExtraction = {
  graph: DiagramGraph;
  mermaid: string;
  provider: "mock" | "gemini";
};
```

## UI behavior

1. Keep `graph` as the editable client-side source of truth.
2. Show only `edges` with `confidence === "low"` in the ambiguity list.
3. Resolve an ambiguity by replacing `edge.target` with one of its `alternatives`, then clear `alternatives` and set `confidence` to `high`.
4. Recompile Mermaid locally after each edit; do not call the extraction API again.
5. Before rendering, validate Mermaid syntax with the Mermaid client library. Display a recoverable error if parsing fails.
6. Offer copy and download of the current Mermaid text as a `.mmd` file.

## Acceptance checklist

- Uploading a valid PNG, JPEG, or WebP displays a diagram and `provider: mock` without an API key.
- A low-confidence edge is visible and can be switched without a network request.
- The Mermaid preview updates after a switch.
- Copy/download uses the current rendered graph, not the original API response.
- 413, 415, and 422 responses show the server-provided `detail` message.

## Out of scope

No user accounts, project persistence, image storage, drag-and-drop canvas editing, or server-side Mermaid rendering are included in v1.
