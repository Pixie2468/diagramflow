# ADR 0001: Compile Mermaid from a validated intermediate graph

## Status

Accepted — 2026-10-17

## Context

Whiteboard images have uncertain text, shapes, and arrow endpoints. Requesting Mermaid directly from a vision model combines perception, syntax generation, and repair into one unreliable string response.

## Decision

Providers must return `DiagramGraph`: nodes, directed edges, shape types, optional normalized bounds, confidence, and alternatives. Pydantic validates it before the deterministic compiler converts it to `flowchart TD` Mermaid.

Low-confidence edges keep one selected `target` plus possible `alternatives`; clients can repair this graph locally and recompile without another model request.

## Consequences

The backend can use a mock provider without changing the API, providers cannot leak Mermaid syntax into the graph contract, and v1 supports only flowcharts. Mermaid client-side parsing remains the rendering UI's responsibility.
