# Graph Report - diagramflow  (2026-10-17)

## Corpus Check
- 29 files · ~10,795 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 4, .css 4, .lock 2)

## Summary
- 334 nodes · 577 edges · 23 communities (14 shown, 9 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d8d2d4d8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Mermaid Compiler & Graph Models
- Frontend Package Dependencies
- Image Processing & App Routes
- Architecture ADRs & Domain Specs
- DiagramGraph
- Frontend App TypeScript Config
- OpenRouter Vision Provider
- Node TypeScript Config
- Mock Provider & API Tests
- Backend Server Entrypoints
- App.tsx
- SVG Icons & Social Assets
- Oxlint Linter Configuration
- Frontend Brand & Static Assets
- TypeScript Solution Config
- Frontend Setup & Index
- Google GenAI Dependency
- Diagram Subgraph Specification
- Frontend Oxlint Config
- Backend Package Root
- DiagramFlow
- devDependencies

## God Nodes (most connected - your core abstractions)
1. `MermaidCompilerTests` - 32 edges
2. `compile_mermaid()` - 21 edges
3. `compilerOptions` - 18 edges
4. `OpenRouterDiagramProvider` - 16 edges
5. `compilerOptions` - 15 edges
6. `DiagramGraph` - 14 edges
7. `DiagramExtraction` - 13 edges
8. `MockDiagramProvider` - 13 edges
9. `GraphNode` - 12 edges
10. `FlowchartGraph` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Overview` --references--> `DiagramGraph`  [INFERRED]
  README.md → backend/src/backend/models.py
- `Ambiguity Resolver UI Pattern` --semantically_similar_to--> `Local Ambiguity Resolution Flow`  [INFERRED] [semantically similar]
  implementation.md → docs/frontend-handoff.md
- `Three-Stage Extraction Pipeline Architecture` --semantically_similar_to--> `ADR 0001: Intermediate Graph Contract`  [INFERRED] [semantically similar]
  implementation.md → docs/adr/0001-intermediate-graph-contract.md
- `Pydantic Validation Dependency` --conceptually_related_to--> `DiagramGraph Schema Contract`  [INFERRED]
  backend/requirements.txt → docs/adr/0001-intermediate-graph-contract.md
- `Pillow Image Processing Dependency` --conceptually_related_to--> `In-Memory Stateless Processing`  [INFERRED]
  backend/requirements.txt → docs/adr/0002-stateless-image-extraction.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Intermediate Diagram Graph Data Model** — docs_glossary_node, docs_glossary_edge, docs_glossary_diagramgraph [EXTRACTED 0.95]
- **Three-Stage Image to Validated Graph to Mermaid Pipeline** — implementation_three_stage_pipeline, docs_adr_0001_intermediate_graph_contract_diagramgraph, docs_adr_0001_intermediate_graph_contract_deterministic_compiler [EXTRACTED 0.95]
- **Edge Ambiguity Local Resolution System** — docs_glossary_alternative, docs_frontend_handoff_ambiguity_resolution_flow, implementation_ambiguity_resolver_ui [INFERRED 0.85]

## Communities (23 total, 9 thin omitted)

### Community 0 - "Mermaid Compiler & Graph Models"
Cohesion: 0.10
Nodes (29): compile_class(), compile_er(), compile_flowchart(), compile_mermaid(), compile_sequence(), _escape_label(), _render_node(), BoundingBox (+21 more)

### Community 1 - "Frontend Package Dependencies"
Cohesion: 0.06
Nodes (32): dependencies, elkjs, mermaid, react, react-dom, tailwindcss, @tailwindcss/vite, @xyflow/react (+24 more)

### Community 2 - "Image Processing & App Routes"
Cohesion: 0.06
Nodes (10): prepare_image(), create_app(), extract_diagram(), DiagramExtraction, DiagramProvider, GeminiDiagramProvider, get_provider(), FakeClient (+2 more)

### Community 3 - "Architecture ADRs & Domain Specs"
Cohesion: 0.09
Nodes (20): DiagramFlow Backend Service, POST /v1/diagrams:extract API Endpoint, Supported Diagram Types, FastAPI Framework Dependency, Pillow Image Processing Dependency, Pydantic Validation Dependency, DiagramGraph Schema Contract, Local Ambiguity Resolution Flow (+12 more)

### Community 5 - "Frontend App TypeScript Config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+11 more)

### Community 6 - "OpenRouter Vision Provider"
Cohesion: 0.22
Nodes (3): OpenRouterDiagramProvider, OpenRouterDiagramProviderTests, handler()

### Community 7 - "Node TypeScript Config"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 8 - "Mock Provider & API Tests"
Cohesion: 0.23
Nodes (5): MockDiagramProvider, ProviderError, ApiTests, extract(), image_bytes()

### Community 10 - "App.tsx"
Cohesion: 0.18
Nodes (15): API_BASE_URL, App(), ConnectedApp(), Diagram(), DiagramRecord, downloadBlob(), exportDiagram(), ExtractionResponse (+7 more)

### Community 11 - "SVG Icons & Social Assets"
Cohesion: 0.29
Nodes (7): Bluesky Icon, Discord Icon, Documentation Icon, GitHub Icon, Social Icon, Icon Sprite Sheet, X Icon

### Community 12 - "Oxlint Linter Configuration"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 13 - "Frontend Brand & Static Assets"
Cohesion: 0.50
Nodes (4): DiagramFlow Favicon, DiagramFlow Hero Image, React Logo, Vite Logo

### Community 21 - "DiagramFlow"
Cohesion: 0.12
Nodes (17): API Specification, Architecture Decisions, Backend Setup, Contributing, DiagramFlow, Example Request, Example Response, Features (+9 more)

### Community 22 - "devDependencies"
Cohesion: 0.17
Nodes (12): devDependencies, @babel/core, babel-plugin-react-compiler, oxlint, @rolldown/plugin-babel, @types/babel__core, @types/node, @types/react (+4 more)

## Knowledge Gaps
- **34 isolated node(s):** `backend`, `@xyflow/react`, `elkjs`, `tailwindcss`, `@babel/core` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 161 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DiagramGraph` connect `DiagramGraph` to `Mermaid Compiler & Graph Models`, `Image Processing & App Routes`, `OpenRouter Vision Provider`, `Mock Provider & API Tests`, `DiagramFlow`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `MermaidCompilerTests` (e.g. with `ClassDiagramGraph` and `ClassNode`) actually correct?**
  _`MermaidCompilerTests` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backend`, `@xyflow/react`, `elkjs` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Mermaid Compiler & Graph Models` be split into smaller, more focused modules?**
  _Cohesion score 0.10401002506265664 - nodes in this community are weakly interconnected._
- **Why does `DiagramFlow` connect `DiagramFlow` to `Architecture ADRs & Domain Specs`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `compile_mermaid()` (e.g. with `ClassDiagramGraph` and `ERGraph`) actually correct?**
  _`compile_mermaid()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Frontend Package Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.06417112299465241 - nodes in this community are weakly interconnected._