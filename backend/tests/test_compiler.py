import unittest

from backend.compiler import compile_mermaid
from backend.models import (
    ClassDiagramGraph,
    ClassNode,
    ClassRelationship,
    ClassRelationType,
    Confidence,
    DiagramGraph,
    EdgeStyle,
    ERAttribute,
    ERCardinality,
    EREntity,
    ERGraph,
    ERRelationship,
    FlowchartGraph,
    GraphEdge,
    GraphNode,
    SequenceArrowStyle,
    SequenceGraph,
    SequenceMessage,
    SequenceParticipant,
    ShapeType,
    Subgraph,
)


class MermaidCompilerTests(unittest.TestCase):
    def test_compiles_all_supported_shapes_and_a_labeled_edge(self) -> None:
        graph = DiagramGraph(
            nodes=[
                GraphNode(id="a", label='Quote " & line\nnext', shape_type=ShapeType.RECTANGLE),
                GraphNode(id="b", label="Round", shape_type=ShapeType.ROUNDED),
                GraphNode(id="c", label="Decision", shape_type=ShapeType.DIAMOND),
                GraphNode(id="d", label="Data", shape_type=ShapeType.CYLINDER),
                GraphNode(id="e", label="Circle", shape_type=ShapeType.CIRCLE),
                GraphNode(id="f", label="Hexagon", shape_type=ShapeType.HEXAGON),
            ],
            edges=[GraphEdge(source="a", target="b", label="go")],
        )
        mermaid = compile_mermaid(graph)
        self.assertIn('a["Quote &quot; &amp; line<br/>next"]', mermaid)
        self.assertIn('b("Round")', mermaid)
        self.assertIn('c{"Decision"}', mermaid)
        self.assertIn('d[("Data")]', mermaid)
        self.assertIn('e(("Circle"))', mermaid)
        self.assertIn('f{{"Hexagon"}}', mermaid)
        self.assertIn("a -->|go| b", mermaid)

    def test_compiles_flowchart_subgraphs_and_edge_styles(self) -> None:
        graph = FlowchartGraph(
            direction="LR",
            nodes=[
                GraphNode(id="app", label="App", shape_type=ShapeType.RECTANGLE),
                GraphNode(id="db", label="DB", shape_type=ShapeType.CYLINDER),
                GraphNode(id="cache", label="Cache", shape_type=ShapeType.CYLINDER),
            ],
            edges=[
                GraphEdge(source="app", target="db", label="query", style=EdgeStyle.SOLID),
                GraphEdge(source="app", target="cache", label="lookup", style=EdgeStyle.DASHED),
                GraphEdge(source="cache", target="db", style=EdgeStyle.THICK),
            ],
            subgraphs=[
                Subgraph(id="data_tier", label="Data Tier", node_ids=["db", "cache"]),
            ],
        )
        mermaid = compile_mermaid(graph)
        self.assertTrue(mermaid.startswith("flowchart LR"))
        self.assertIn('subgraph data_tier["Data Tier"]', mermaid)
        self.assertIn('app["App"]', mermaid)
        self.assertIn("app -->|query| db", mermaid)
        self.assertIn("app -. lookup .-> cache", mermaid)
        self.assertIn("cache ==> db", mermaid)

    def test_compiles_sequence_diagram(self) -> None:
        graph = SequenceGraph(
            autonumber=True,
            participants=[
                SequenceParticipant(id="user", label="User Browser"),
                SequenceParticipant(id="api", label="API Gateway"),
                SequenceParticipant(id="auth", label="Auth Service"),
            ],
            messages=[
                SequenceMessage(source="user", target="api", label="POST /login", style=SequenceArrowStyle.SOLID),
                SequenceMessage(source="api", target="auth", label="verify()", style=SequenceArrowStyle.SOLID),
                SequenceMessage(source="auth", target="api", label="token", style=SequenceArrowStyle.DASHED),
                SequenceMessage(
                    source="api",
                    target="user",
                    label="200 OK",
                    style=SequenceArrowStyle.DASHED,
                    confidence=Confidence.LOW,
                    alternatives=["auth"],
                ),
            ],
        )
        mermaid = compile_mermaid(graph)
        self.assertTrue(mermaid.startswith("sequenceDiagram"))
        self.assertIn("autonumber", mermaid)
        self.assertIn('participant user as "User Browser"', mermaid)
        self.assertIn("user->>api: POST /login", mermaid)
        self.assertIn("api->>auth: verify()", mermaid)
        self.assertIn("auth-->>api: token", mermaid)
        self.assertIn("api-->>user: 200 OK", mermaid)

    def test_compiles_er_diagram(self) -> None:
        graph = ERGraph(
            entities=[
                EREntity(
                    id="CUSTOMER",
                    attributes=[
                        ERAttribute(name="id", type="string", is_key=True),
                        ERAttribute(name="email", type="string"),
                    ],
                ),
                EREntity(
                    id="ORDER",
                    attributes=[
                        ERAttribute(name="id", type="int", is_key=True),
                        ERAttribute(name="total", type="float"),
                    ],
                ),
            ],
            relationships=[
                ERRelationship(source="CUSTOMER", target="ORDER", cardinality=ERCardinality.ONE_TO_MANY, label="places"),
            ],
        )
        mermaid = compile_mermaid(graph)
        self.assertTrue(mermaid.startswith("erDiagram"))
        self.assertIn('CUSTOMER ||--|{ ORDER : "places"', mermaid)
        self.assertIn("CUSTOMER {", mermaid)
        self.assertIn("string id PK", mermaid)
        self.assertIn("string email", mermaid)

    def test_compiles_class_diagram(self) -> None:
        graph = ClassDiagramGraph(
            classes=[
                ClassNode(id="Vehicle", attributes=["speed: int"], methods=["drive()"]),
                ClassNode(id="Car", attributes=["wheels: int"], methods=["honk()"]),
            ],
            relationships=[
                ClassRelationship(source="Car", target="Vehicle", relation_type=ClassRelationType.INHERITANCE),
            ],
        )
        mermaid = compile_mermaid(graph)
        self.assertTrue(mermaid.startswith("classDiagram"))
        self.assertIn("Car <|-- Vehicle", mermaid)
        self.assertIn("class Vehicle {", mermaid)
        self.assertIn("+speed: int", mermaid)
        self.assertIn("+drive()", mermaid)

    def test_rejects_ambiguous_edge_with_selected_target_in_alternatives(self) -> None:
        with self.assertRaises(ValueError):
            DiagramGraph(
                nodes=[GraphNode(id="a", label="A"), GraphNode(id="b", label="B")],
                edges=[GraphEdge(source="a", target="b", confidence=Confidence.LOW, alternatives=["b"])],
            )

    def test_rejects_subgraph_with_unknown_nodes(self) -> None:
        with self.assertRaises(ValueError):
            FlowchartGraph(
                nodes=[GraphNode(id="a", label="A")],
                subgraphs=[Subgraph(id="sg", label="Group", node_ids=["unknown"])],
            )

    def test_rejects_sequence_message_with_unknown_participants(self) -> None:
        with self.assertRaises(ValueError):
            SequenceGraph(
                participants=[SequenceParticipant(id="user", label="User")],
                messages=[SequenceMessage(source="user", target="unknown", label="call")],
            )

    def test_rejects_er_relationship_with_unknown_entities(self) -> None:
        with self.assertRaises(ValueError):
            ERGraph(
                entities=[EREntity(id="USER")],
                relationships=[ERRelationship(source="USER", target="UNKNOWN", label="relates")],
            )

    def test_supports_architecture_diagram_type_and_aliases(self) -> None:
        raw_json = (
            '{"diagram_type":"architecture","direction":"TD",'
            '"nodes":[{"id":"lb","label":"Load Balancer","shape_type":"rectangle"}],'
            '"edges":[]}'
        )
        graph = DiagramGraph.model_validate_json(raw_json)
        self.assertIsInstance(graph, FlowchartGraph)
        self.assertEqual(compile_mermaid(graph), 'flowchart TD\n    lb["Load Balancer"]')

