"""Deterministic Mermaid generation from DiagramFlow's validated graph."""

from .models import DiagramGraph, GraphNode, ShapeType


def _escape_label(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("\n", "<br/>")


def _render_node(node: GraphNode) -> str:
    label = _escape_label(node.label)
    templates = {
        ShapeType.RECTANGLE: f'{node.id}["{label}"]',
        ShapeType.ROUNDED: f'{node.id}("{label}")',
        ShapeType.DIAMOND: f'{node.id}{{"{label}"}}',
        ShapeType.CYLINDER: f'{node.id}[("{label}")]',
    }
    return templates[node.shape_type]


def compile_mermaid(graph: DiagramGraph) -> str:
    """Compile a graph without calling a model or depending on request state."""
    lines = [f"flowchart {graph.direction}"]
    lines.extend(f"    {_render_node(node)}" for node in graph.nodes)
    for edge in graph.edges:
        if edge.label:
            lines.append(f"    {edge.source} -->|{_escape_label(edge.label)}| {edge.target}")
        else:
            lines.append(f"    {edge.source} --> {edge.target}")
    return "\n".join(lines)
