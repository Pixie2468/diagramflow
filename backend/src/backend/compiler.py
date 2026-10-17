"""Deterministic Mermaid generation from DiagramFlow's validated graphs."""

from .models import (
    AnyDiagramGraph,
    ClassDiagramGraph,
    ClassRelationType,
    EdgeStyle,
    ERCardinality,
    ERGraph,
    FlowchartGraph,
    GraphNode,
    SequenceArrowStyle,
    SequenceGraph,
    ShapeType,
)


def _escape_label(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("\n", "<br/>")


def _render_node(node: GraphNode) -> str:
    label = _escape_label(node.label)
    templates = {
        ShapeType.RECTANGLE: f'{node.id}["{label}"]',
        ShapeType.ROUNDED: f'{node.id}("{label}")',
        ShapeType.DIAMOND: f'{node.id}{{"{label}"}}',
        ShapeType.CYLINDER: f'{node.id}[("{label}")]',
        ShapeType.CIRCLE: f'{node.id}(("{label}"))',
        ShapeType.HEXAGON: f'{node.id}{{{{"{label}"}}}}',
    }
    return templates[node.shape_type]


def compile_flowchart(graph: FlowchartGraph) -> str:
    lines = [f"flowchart {graph.direction}"]
    node_by_id = {n.id: n for n in graph.nodes}
    subgraph_node_ids = set()

    for sg in graph.subgraphs:
        lines.append(f'    subgraph {sg.id}["{_escape_label(sg.label)}"]')
        for nid in sg.node_ids:
            if nid in node_by_id:
                lines.append(f"        {_render_node(node_by_id[nid])}")
                subgraph_node_ids.add(nid)
        lines.append("    end")

    for node in graph.nodes:
        if node.id not in subgraph_node_ids:
            lines.append(f"    {_render_node(node)}")

    style_tokens = {
        EdgeStyle.SOLID: ("-->", "-->"),
        EdgeStyle.DASHED: ("-.->", "-.->"),
        EdgeStyle.THICK: ("==>", "==>"),
        EdgeStyle.BIDIRECTIONAL: ("<-->", "<-->"),
    }

    for edge in graph.edges:
        unlabeled_arrow, _ = style_tokens.get(edge.style, ("-->", "-->"))
        if edge.label:
            escaped = _escape_label(edge.label)
            if edge.style == EdgeStyle.DASHED:
                arrow = f"-. {escaped} .->"
            elif edge.style == EdgeStyle.THICK:
                arrow = f"== {escaped} ==>"
            elif edge.style == EdgeStyle.BIDIRECTIONAL:
                arrow = f"<-- {escaped} -->"
            else:
                arrow = f"-->|{escaped}|"
            lines.append(f"    {edge.source} {arrow} {edge.target}")
        else:
            lines.append(f"    {edge.source} {unlabeled_arrow} {edge.target}")
    return "\n".join(lines)


def compile_sequence(graph: SequenceGraph) -> str:
    lines = ["sequenceDiagram"]
    if graph.autonumber:
        lines.append("    autonumber")
    for p in graph.participants:
        lines.append(f'    participant {p.id} as "{_escape_label(p.label)}"')

    style_arrows = {
        SequenceArrowStyle.SOLID: "->>",
        SequenceArrowStyle.DASHED: "-->>",
        SequenceArrowStyle.BIDIRECTIONAL: "<<->>",
    }

    for msg in graph.messages:
        arrow = style_arrows.get(msg.style, "->>")
        label_text = f": {_escape_label(msg.label)}" if msg.label else ""
        lines.append(f"    {msg.source}{arrow}{msg.target}{label_text}")
    return "\n".join(lines)


def compile_er(graph: ERGraph) -> str:
    lines = ["erDiagram"]
    cardinality_symbols = {
        ERCardinality.ONE_TO_ONE: "||--||",
        ERCardinality.ONE_TO_MANY: "||--|{",
        ERCardinality.ZERO_TO_MANY: "|o--o{",
        ERCardinality.MANY_TO_MANY: "}|--|{",
    }

    for rel in graph.relationships:
        sym = cardinality_symbols.get(rel.cardinality, "||--|{")
        label_text = f' : "{_escape_label(rel.label)}"' if rel.label else " : relates"
        lines.append(f"    {rel.source} {sym} {rel.target}{label_text}")

    for ent in graph.entities:
        if ent.attributes:
            lines.append(f"    {ent.id} {{")
            for attr in ent.attributes:
                key_marker = " PK" if attr.is_key else ""
                lines.append(f"        {attr.type} {attr.name}{key_marker}")
            lines.append("    }")
    return "\n".join(lines)


def compile_class(graph: ClassDiagramGraph) -> str:
    lines = ["classDiagram"]
    relation_symbols = {
        ClassRelationType.INHERITANCE: "<|--",
        ClassRelationType.COMPOSITION: "*--",
        ClassRelationType.AGGREGATION: "o--",
        ClassRelationType.ASSOCIATION: "-->",
        ClassRelationType.DEPENDENCY: "..>",
    }

    for rel in graph.relationships:
        sym = relation_symbols.get(rel.relation_type, "<|--")
        label_text = f' : "{_escape_label(rel.label)}"' if rel.label else ""
        lines.append(f"    {rel.source} {sym} {rel.target}{label_text}")

    for c in graph.classes:
        if c.attributes or c.methods:
            lines.append(f"    class {c.id} {{")
            for attr in c.attributes:
                lines.append(f"        +{_escape_label(attr)}")
            for method in c.methods:
                lines.append(f"        +{_escape_label(method)}")
            lines.append("    }")
    return "\n".join(lines)


def compile_mermaid(graph: AnyDiagramGraph) -> str:
    """Compile a graph without calling a model or depending on request state."""
    if isinstance(graph, FlowchartGraph):
        return compile_flowchart(graph)
    if isinstance(graph, SequenceGraph):
        return compile_sequence(graph)
    if isinstance(graph, ERGraph):
        return compile_er(graph)
    if isinstance(graph, ClassDiagramGraph):
        return compile_class(graph)
    raise ValueError(f"Unsupported diagram graph type: {type(graph)}")
