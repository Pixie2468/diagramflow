"""Validated intermediate graph contract shared by providers and the API."""

from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, TypeAdapter, model_validator


class ShapeType(StrEnum):
    RECTANGLE = "rectangle"
    ROUNDED = "rounded"
    DIAMOND = "diamond"
    CYLINDER = "cylinder"
    CIRCLE = "circle"
    HEXAGON = "hexagon"


class Confidence(StrEnum):
    HIGH = "high"
    LOW = "low"


class EdgeStyle(StrEnum):
    SOLID = "solid"
    DASHED = "dashed"
    THICK = "thick"
    BIDIRECTIONAL = "bidirectional"


class BoundingBox(BaseModel):
    """Normalized [0, 1000] image coordinates for a detected node."""

    model_config = ConfigDict(extra="forbid")

    x_min: int = Field(ge=0, le=1000)
    y_min: int = Field(ge=0, le=1000)
    x_max: int = Field(ge=0, le=1000)
    y_max: int = Field(ge=0, le=1000)

    @model_validator(mode="after")
    def has_area(self) -> "BoundingBox":
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise ValueError("bounding_box must have positive area")
        return self


class GraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    label: str = Field(min_length=1, max_length=200)
    shape_type: ShapeType = ShapeType.RECTANGLE
    bounding_box: BoundingBox | None = None


class GraphEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    target: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    label: str | None = Field(default=None, max_length=200)
    style: EdgeStyle = EdgeStyle.SOLID
    confidence: Confidence = Confidence.HIGH
    alternatives: list[str] = Field(default_factory=list, max_length=8)


class Subgraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    label: str = Field(min_length=1, max_length=200)
    node_ids: list[str] = Field(min_length=1, max_length=50)


class FlowchartGraph(BaseModel):
    """A directed flowchart or architecture graph."""

    model_config = ConfigDict(extra="forbid")

    diagram_type: Literal["flowchart"] = "flowchart"
    direction: str = Field(default="TD", pattern=r"^(TD|LR|BT|RL)$")
    nodes: list[GraphNode] = Field(min_length=1, max_length=100)
    edges: list[GraphEdge] = Field(default_factory=list, max_length=200)
    subgraphs: list[Subgraph] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def references_known_nodes(self) -> "FlowchartGraph":
        node_ids = {node.id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("node IDs must be unique")
        for edge in self.edges:
            missing = {edge.source, edge.target, *edge.alternatives} - node_ids
            if missing:
                raise ValueError(f"edge references unknown node IDs: {sorted(missing)}")
            if edge.target in edge.alternatives:
                raise ValueError("alternatives must not repeat the selected target")
            if edge.confidence == Confidence.HIGH and edge.alternatives:
                raise ValueError("only low-confidence edges can have alternatives")
        for sg in self.subgraphs:
            missing_sg = set(sg.node_ids) - node_ids
            if missing_sg:
                raise ValueError(f"subgraph references unknown node IDs: {sorted(missing_sg)}")
        return self


# ---------------- Sequence Diagram Models ----------------


class SequenceParticipant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    label: str = Field(min_length=1, max_length=200)


class SequenceArrowStyle(StrEnum):
    SOLID = "solid"
    DASHED = "dashed"
    BIDIRECTIONAL = "bidirectional"


class SequenceMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    target: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    label: str = Field(default="", max_length=200)
    style: SequenceArrowStyle = SequenceArrowStyle.SOLID
    confidence: Confidence = Confidence.HIGH
    alternatives: list[str] = Field(default_factory=list, max_length=8)


class SequenceGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagram_type: Literal["sequence"] = "sequence"
    autonumber: bool = True
    participants: list[SequenceParticipant] = Field(min_length=1, max_length=30)
    messages: list[SequenceMessage] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def references_known_participants(self) -> "SequenceGraph":
        participant_ids = {p.id for p in self.participants}
        if len(participant_ids) != len(self.participants):
            raise ValueError("participant IDs must be unique")
        for msg in self.messages:
            missing = {msg.source, msg.target, *msg.alternatives} - participant_ids
            if missing:
                raise ValueError(f"message references unknown participant IDs: {sorted(missing)}")
            if msg.target in msg.alternatives:
                raise ValueError("alternatives must not repeat the selected target")
            if msg.confidence == Confidence.HIGH and msg.alternatives:
                raise ValueError("only low-confidence messages can have alternatives")
        return self


# ---------------- Entity-Relationship (ER) Models ----------------


class ERAttribute(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    type: str = Field(default="string", max_length=50)
    is_key: bool = False


class EREntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    attributes: list[ERAttribute] = Field(default_factory=list, max_length=50)


class ERCardinality(StrEnum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    ZERO_TO_MANY = "0:N"
    MANY_TO_MANY = "M:N"


class ERRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    target: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    cardinality: ERCardinality = ERCardinality.ONE_TO_MANY
    label: str = Field(default="", max_length=100)
    confidence: Confidence = Confidence.HIGH
    alternatives: list[str] = Field(default_factory=list, max_length=8)


class ERGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagram_type: Literal["er"] = "er"
    entities: list[EREntity] = Field(min_length=1, max_length=50)
    relationships: list[ERRelationship] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def references_known_entities(self) -> "ERGraph":
        entity_ids = {e.id for e in self.entities}
        if len(entity_ids) != len(self.entities):
            raise ValueError("entity IDs must be unique")
        for rel in self.relationships:
            missing = {rel.source, rel.target} - entity_ids
            if missing:
                raise ValueError(f"relationship references unknown entity IDs: {sorted(missing)}")
        return self


# ---------------- Class Diagram Models ----------------


class ClassNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    attributes: list[str] = Field(default_factory=list, max_length=30)
    methods: list[str] = Field(default_factory=list, max_length=30)


class ClassRelationType(StrEnum):
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    DEPENDENCY = "dependency"


class ClassRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    target: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    relation_type: ClassRelationType = ClassRelationType.INHERITANCE
    label: str | None = Field(default=None, max_length=100)
    confidence: Confidence = Confidence.HIGH
    alternatives: list[str] = Field(default_factory=list, max_length=8)


class ClassDiagramGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagram_type: Literal["class"] = "class"
    classes: list[ClassNode] = Field(min_length=1, max_length=50)
    relationships: list[ClassRelationship] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def references_known_classes(self) -> "ClassDiagramGraph":
        class_ids = {c.id for c in self.classes}
        if len(class_ids) != len(self.classes):
            raise ValueError("class IDs must be unique")
        for rel in self.relationships:
            missing = {rel.source, rel.target} - class_ids
            if missing:
                raise ValueError(f"relationship references unknown class IDs: {sorted(missing)}")
        return self


# ---------------- Discriminator and Polymorphic Root ----------------


def _get_diagram_discriminator(v: object) -> str:
    if isinstance(v, dict):
        return v.get("diagram_type", "flowchart")
    return getattr(v, "diagram_type", "flowchart")


AnyDiagramGraph = Annotated[
    Union[
        Annotated[FlowchartGraph, Tag("flowchart")],
        Annotated[SequenceGraph, Tag("sequence")],
        Annotated[ERGraph, Tag("er")],
        Annotated[ClassDiagramGraph, Tag("class")],
    ],
    Discriminator(_get_diagram_discriminator),
]

_graph_adapter = TypeAdapter(AnyDiagramGraph)


class DiagramGraph:
    """Polymorphic graph resolver with Flowchart default for backward compatibility."""

    def __new__(cls, *args, **kwargs) -> FlowchartGraph:
        return FlowchartGraph(*args, **kwargs)

    @classmethod
    def model_validate_json(cls, json_data: str | bytes) -> AnyDiagramGraph:
        return _graph_adapter.validate_json(json_data)

    @classmethod
    def model_validate(cls, obj: object) -> AnyDiagramGraph:
        return _graph_adapter.validate_python(obj)


class DiagramExtraction(BaseModel):
    graph: AnyDiagramGraph
    mermaid: str
    provider: str
