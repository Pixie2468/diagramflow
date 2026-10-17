"""Validated intermediate graph contract shared by providers and the API."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ShapeType(StrEnum):
    RECTANGLE = "rectangle"
    ROUNDED = "rounded"
    DIAMOND = "diamond"
    CYLINDER = "cylinder"


class Confidence(StrEnum):
    HIGH = "high"
    LOW = "low"


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
    confidence: Confidence = Confidence.HIGH
    alternatives: list[str] = Field(default_factory=list, max_length=8)


class DiagramGraph(BaseModel):
    """A directed graph, intentionally independent of Mermaid syntax."""

    model_config = ConfigDict(extra="forbid")

    direction: str = Field(default="TD", pattern=r"^(TD|LR|BT|RL)$")
    nodes: list[GraphNode] = Field(min_length=1, max_length=100)
    edges: list[GraphEdge] = Field(default_factory=list, max_length=200)

    @model_validator(mode="after")
    def references_known_nodes(self) -> "DiagramGraph":
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
        return self


class DiagramExtraction(BaseModel):
    graph: DiagramGraph
    mermaid: str
    provider: str
