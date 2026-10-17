import unittest

from backend.compiler import compile_mermaid
from backend.models import Confidence, DiagramGraph, GraphEdge, GraphNode, ShapeType


class MermaidCompilerTests(unittest.TestCase):
    def test_compiles_all_supported_shapes_and_a_labeled_edge(self) -> None:
        graph = DiagramGraph(
            nodes=[
                GraphNode(id="a", label='Quote " & line\nnext', shape_type=ShapeType.RECTANGLE),
                GraphNode(id="b", label="Round", shape_type=ShapeType.ROUNDED),
                GraphNode(id="c", label="Decision", shape_type=ShapeType.DIAMOND),
                GraphNode(id="d", label="Data", shape_type=ShapeType.CYLINDER),
            ],
            edges=[GraphEdge(source="a", target="b", label="go")],
        )
        mermaid = compile_mermaid(graph)
        self.assertIn('a["Quote &quot; &amp; line<br/>next"]', mermaid)
        self.assertIn('b("Round")', mermaid)
        self.assertIn('c{"Decision"}', mermaid)
        self.assertIn('d[("Data")]', mermaid)
        self.assertIn("a -->|go| b", mermaid)

    def test_rejects_ambiguous_edge_with_selected_target_in_alternatives(self) -> None:
        with self.assertRaises(ValueError):
            DiagramGraph(
                nodes=[GraphNode(id="a", label="A"), GraphNode(id="b", label="B")],
                edges=[GraphEdge(source="a", target="b", confidence=Confidence.LOW, alternatives=["b"])],
            )
