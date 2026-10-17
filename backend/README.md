# DiagramFlow backend

Stateless FastAPI service for turning a whiteboard image into validated graph JSON and deterministic Mermaid.

## Run

```bash
uv run --directory backend uvicorn backend.main:app --reload
```

Without `GEMINI_API_KEY`, the API uses its deterministic mock provider so the frontend can be built immediately. With a key in either the process environment or `backend/.env`, each request sends the contrast-enhanced image to the Gemini API using the configured Gemma 4 model and requires structured `DiagramGraph` JSON.

To use OpenRouter instead, configure:

```bash
DIAGRAM_PROVIDER=openrouter
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=google/gemma-4-31b-it
```

OpenRouter receives the image as a base64 data URL and returns JSON that is validated against the same local graph contract.

```bash
GEMINI_API_KEY=... GEMINI_MODEL=gemma-4-26b-a4b-it \
uv run --directory backend uvicorn backend.main:app --reload
```

`CORS_ORIGINS` is a comma-separated allowlist and defaults to `http://localhost:5173`.

## API

`POST /v1/diagrams:extract` accepts multipart field `image` (`image/png`, `image/jpeg`, or `image/webp`, maximum 10 MB). The model detects the diagram type and returns a validated discriminated union:

* **Flowchart & System Architecture** (`flowchart TD|LR`): Nodes (6 shapes: rectangle, rounded, diamond, cylinder, circle, hexagon), styled edges (`solid`, `dashed`, `thick`, `bidirectional`), and `subgraphs` (clusters/VPCs).
* **Sequence Diagram** (`sequenceDiagram`): Participants, message calls and returns (`solid`, `dashed`, `bidirectional`), and autonumbering.
* **Entity-Relationship Diagram** (`erDiagram`): Entities, typed attributes, primary/foreign keys (`PK`/`FK`), and cardinalities (`1:1`, `1:N`, `0:N`, `M:N`).
* **Class Diagram** (`classDiagram`): Classes with attributes and methods, plus relations (`inheritance`, `composition`, `aggregation`, `association`, `dependency`).

```json
{
  "graph": { "diagram_type": "flowchart", "direction": "TD", "nodes": [], "edges": [] },
  "mermaid": "flowchart TD",
  "provider": "mock"
}
```

The process retains no uploaded image or graph. See [`../docs/adr`](../docs/adr) and [`../docs/glossary.md`](../docs/glossary.md).

## Verify

```bash
backend/.venv/bin/python -m unittest discover -s backend/tests -v
```
