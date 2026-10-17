# DiagramFlow glossary
 
- **DiagramGraph** — validated, provider-neutral discriminated union representing a flowchart/architecture, sequence, ER, or class diagram.
- **Node** — a detected diagram shape with an ID, label, shape type, and optional normalized bounding box.
- **Edge** — a directed connection between two node IDs with style (`solid`, `dashed`, `thick`, `bidirectional`) and ambiguity metadata.
- **Subgraph** — a grouping container representing a cluster, VPC, or subsystem enclosing multiple nodes.
- **Sequence Diagram** — an interaction diagram with participants, sequential messages, and arrow styles (`solid`, `dashed`, `bidirectional`).
- **ER Diagram** — entity-relationship diagram with entities, attributes, primary/foreign keys, and cardinalities (`1:1`, `1:N`, `0:N`, `M:N`).
- **Class Diagram** — UML structural diagram with classes, members (attributes/methods), and relationship semantics (`inheritance`, `composition`, `aggregation`, etc.).
- **Alternative** — a plausible target or connection for a low-confidence edge other than its selected target.
- **Confidence** — `high` or `low`; the UI filters low-confidence elements into the ambiguity resolver.
- **Provider** — implementation that turns an image into a `DiagramGraph`; `mock` works without credentials, `openrouter` uses Gemma 4 / compatible models via OpenRouter, and `gemini` uses Gemma 4 via Gemini API.
- **Compiler** — pure function that serializes any `DiagramGraph` into standard Mermaid source.

