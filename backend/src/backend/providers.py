"""Diagram extraction providers; only this module knows about model SDKs."""

import json
from os import getenv
from typing import Protocol

from google import genai
from google.genai import types

from .compiler import compile_mermaid
from .models import Confidence, DiagramExtraction, DiagramGraph, GraphEdge, GraphNode, ShapeType

PROMPT = """Analyze this whiteboard or hand-drawn flowchart. First inventory every readable
shape and its text, then trace directed connections. Return only the requested graph JSON.
Use bounding_box coordinates normalized from 0 to 1000 when a node location is visible.
For unclear arrow endpoints, select the most likely target, mark confidence as low, and list
other plausible target IDs in alternatives. Never invent nodes or edges not visible in the image."""


class DiagramProvider(Protocol):
    name: str

    def extract(self, image: bytes, mime_type: str) -> DiagramExtraction: ...


class MockDiagramProvider:
    """Predictable no-key provider for frontend development and API verification."""

    name = "mock"

    def extract(self, image: bytes, mime_type: str) -> DiagramExtraction:
        graph = DiagramGraph(
            nodes=[
                GraphNode(id="start", label="Start", shape_type=ShapeType.ROUNDED),
                GraphNode(id="review", label="Review request", shape_type=ShapeType.DIAMOND),
                GraphNode(id="approved", label="Approved", shape_type=ShapeType.RECTANGLE),
                GraphNode(id="rework", label="Rework", shape_type=ShapeType.RECTANGLE),
            ],
            edges=[
                GraphEdge(source="start", target="review"),
                GraphEdge(source="review", target="approved", label="yes"),
                GraphEdge(source="review", target="rework", label="no", confidence=Confidence.LOW, alternatives=["approved"]),
            ],
        )
        return DiagramExtraction(graph=graph, mermaid=compile_mermaid(graph), provider=self.name)


class GeminiDiagramProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract(self, image: bytes, mime_type: str) -> DiagramExtraction:
        response = self.client.models.generate_content(
            model=self.model,
            contents=[types.Part.from_bytes(data=image, mime_type=mime_type), PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DiagramGraph,
                temperature=0,
            ),
        )
        parsed = response.parsed
        if parsed is None:
            raise RuntimeError("Gemini returned no structured graph.")
        graph = DiagramGraph.model_validate(parsed if isinstance(parsed, dict) else json.loads(parsed.model_dump_json()))
        return DiagramExtraction(graph=graph, mermaid=compile_mermaid(graph), provider=self.name)


def get_provider() -> DiagramProvider:
    """Choose live Gemini only when its credential is deliberately configured."""
    api_key = getenv("GEMINI_API_KEY")
    if not api_key:
        return MockDiagramProvider()
    return GeminiDiagramProvider(api_key, getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it"))
