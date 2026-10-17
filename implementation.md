To make **DiagramFlow** eligible for both the **Best Use of Gemma 4** and **Best Open-Source AI Project** prizes, you should avoid asking the vision model to output raw Mermaid.js syntax directly from an image. Vision models frequently hallucinate Mermaid syntax on messy sketches, and debugging raw string outputs in a hackathon is painful.

Instead, design a **three-stage pipeline**: **Image $\rightarrow$ Intermediate Graph JSON (with confidence scores) $\rightarrow$ Deterministic Mermaid Compiler**. This gives you the exact data structure needed for your twist (letting users fix ambiguous connections) and keeps your architecture modular.

---

## 1. System Architecture & The "Dual-Prize" Strategy

To qualify for both tracks without doubling your workload, decouple your core extraction engine from your UI:

1. **Core Engine & Agent Skill (DigitalOcean Track):** Package the vision-to-JSON-to-Mermaid logic so it complies with the **Agent Skill Open Standard** (`SKILL.md` + scripts/endpoints) in a public GitHub repo with an open-source license. Any coding agent or CLI user can pass an image path and get a verified Mermaid file back.


2. **Interactive Web App (DeepMind Track):** Build a lightweight frontend (Svelte pairs great here with a Go or FastAPI backend) that calls your core engine via the Gemini API running Gemma 4. It renders the parsed graph, highlights low-confidence edges in red/yellow, lets the user toggle/fix them in two clicks, and live-renders the resulting Mermaid diagram.



---

## 2. Phase-by-Phase Implementation Guide

### Phase 1: Design the Intermediate Graph Schema (Start Here)

Before writing any API calls, define the strict JSON schema that Gemma 4 must return.

* **What to think about:** A diagram isn't just text; it's a directed or undirected graph $G = (V, E)$.
* **Nodes ($V$):** What properties does a node need? (`id`, `label`, `shape_type` like rectangle/diamond/cylinder, and maybe `bounding_box` or `zone` so the user knows which box on the whiteboard it refers to).
* **Edges ($E$):** How do you represent an ambiguous arrow? If an arrow sits between Node A, Node B, and Node C and isn't clearly touching either, how should the JSON capture that?
* *Hint:* Give each edge a `source`, `target`, `label`, `confidence` (`high` | `low`), and an `alternatives` array (e.g., if `confidence` is `low`, `target` might be `"node_2"`, with `alternatives: ["node_3"]`).



### Phase 2: Multimodal Prompting & Structured Outputs

Use the Gemini API to call **Gemma 4** with your whiteboard image.

* **Image Pre-processing:** Whiteboard photos suffer from glare and low contrast. Before sending the image over the wire, run a quick contrast/grayscale pass (either on the HTML5 canvas client-side or in your backend) so faint marker lines pop out.
* **Two-Step Reasoning in One Call:** Instruct the model to first inventory all text and shapes it sees, and *then* trace the lines connecting them. Enforce your Phase 1 JSON schema on the response so your backend never has to parse markdown code blocks or broken strings.

### Phase 3: The Deterministic Compiler & Verification Loop

Write a pure function in your backend or frontend that takes your validated Graph JSON and compiles it into a Mermaid string (e.g., `flowchart TD`).

* **Why a pure function?** Because when the user clicks "Swap target from Node B to Node C" in the UI to resolve an ambiguous arrow, you shouldn't have to call the LLM again. You just mutate the JSON state and re-run your compiler in milliseconds.
* **Programmatic Validation:** Use `mermaid.parse(code)` on the client side to verify that the generated syntax is 100% valid before rendering.

### Phase 4: The "Ambiguity Resolver" UI (Your Winning Feature)

Judges only spend 2–3 minutes looking at your demo. Don't make them drag-and-drop nodes on a complex canvas—that takes too long to build and is finicky to demo.

* Build a **Split-Screen View**:
* **Left Pane:** The uploaded photo + a simple list of **"Flagged Ambiguities"** (filtered from edges where `confidence == "low"`). Each flagged item shows: *"Arrow from [Auth Service] points to [DB] (or did you mean [Cache]?)"* with a 1-click swap button.
* **Right Pane:** Live-rendered Mermaid SVG + a one-click copy/export button for `.mmd` or Markdown.



---

## 3. Immediate Next Step

Let's lock down **Phase 1 and 2** first.

1. What backend/frontend stack are you planning to spin up for this? (e.g., Go + Svelte, or Python/FastAPI + Svelte?)
2. Take a shot at drafting the JSON struct/schema for a single **Node** and a single **Edge** (including how you want to represent ambiguity). Paste it here, and we'll stress-test it against tricky whiteboard edge cases before wiring up the Gemma 4 call.
