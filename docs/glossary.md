# DiagramFlow glossary

- **DiagramGraph** — validated, provider-neutral directed graph used by the API and compiler.
- **Node** — a detected diagram shape with an ID, label, shape type, and optional normalized bounding box.
- **Edge** — a directed connection between two node IDs. It may carry a label and ambiguity metadata.
- **Alternative** — a plausible target for a low-confidence edge other than its selected target.
- **Confidence** — `high` or `low`; the UI filters low-confidence edges into the ambiguity resolver.
- **Provider** — implementation that turns an image into a `DiagramGraph`; `mock` works without credentials and `gemini` uses Gemma 4 through the Gemini API.
- **Compiler** — pure function that serializes a `DiagramGraph` into Mermaid flowchart source.
