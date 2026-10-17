"""Diagram extraction providers; only this module knows about model SDKs."""

import base64
from os import getenv
from typing import Protocol

import httpx
from google import genai
from google.genai import types
from pydantic import ValidationError

from .compiler import compile_mermaid
from .models import Confidence, DiagramExtraction, DiagramGraph, GraphEdge, GraphNode, ShapeType

PROMPT = """Analyze this diagram image and detect its type. Return strictly JSON adhering to one of these formats, with no Markdown or extra text:

1. FLOWCHART or ARCHITECTURE:
{"diagram_type":"flowchart","direction":"TD","nodes":[{"id":"node_id","label":"visible text","shape_type":"rectangle|rounded|diamond|cylinder|circle|hexagon"}],"edges":[{"source":"node_id","target":"node_id","label":"optional","style":"solid|dashed|thick|bidirectional","confidence":"high|low","alternatives":["alt_id"]}],"subgraphs":[{"id":"group_id","label":"group title","node_ids":["node_id"]}]}

2. SEQUENCE DIAGRAM (actors/lifelines & sequential message arrows):
{"diagram_type":"sequence","autonumber":true,"participants":[{"id":"part_id","label":"visible text"}],"messages":[{"source":"part_id","target":"part_id","label":"call or response","style":"solid|dashed|bidirectional","confidence":"high|low","alternatives":["alt_id"]}]}

3. ENTITY-RELATIONSHIP (ER) DIAGRAM (database entities & relationships):
{"diagram_type":"er","entities":[{"id":"entity_name","attributes":[{"name":"col_name","type":"string|int|uuid","is_key":false}]}],"relationships":[{"source":"entity_name","target":"entity_name","cardinality":"1:1|1:N|0:N|M:N","label":"verb phrase","confidence":"high|low","alternatives":["alt_id"]}]}

4. CLASS DIAGRAM (UML classes, methods/fields & relations):
{"diagram_type":"class","classes":[{"id":"class_name","attributes":["attr: type"],"methods":["method()"]}],"relationships":[{"source":"class_name","target":"class_name","relation_type":"inheritance|composition|aggregation|association|dependency","label":"optional","confidence":"high|low","alternatives":["alt_id"]}]}

Use valid identifiers for ids. Use low confidence and alternatives only for ambiguous lines. Return valid JSON only."""


class DiagramProvider(Protocol):
    name: str

    async def extract(self, image: bytes, mime_type: str) -> DiagramExtraction: ...


class ProviderError(RuntimeError):
    """A safe, provider-neutral error suitable for returning as a 502."""


class MockDiagramProvider:
    """Predictable no-key provider for frontend development and API verification."""

    name = "mock"

    async def extract(self, image: bytes, mime_type: str) -> DiagramExtraction:
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

    def __init__(self, api_key: str, model: str, client: Any | None = None) -> None:
        self.client = client or genai.Client(api_key=api_key)
        self.model = model

    async def extract(self, image: bytes, mime_type: str) -> DiagramExtraction:
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[types.Part.from_bytes(data=image, mime_type=mime_type), PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
        except Exception as exc:
            raise ProviderError("Gemini request failed.") from exc

        try:
            response_text = response.text
            if not response_text:
                raise ValueError("Gemini returned no structured graph.")
            graph = DiagramGraph.model_validate_json(response_text)
        except (TypeError, ValueError, ValidationError) as exc:
            raise ProviderError("Gemini returned an invalid graph.") from exc
        return DiagramExtraction(graph=graph, mermaid=compile_mermaid(graph), provider=self.name)


class OpenRouterDiagramProvider:
    """OpenRouter-backed vision extraction using its OpenAI-compatible API."""

    name = "openrouter"

    def __init__(self, api_key: str, model: str, client: httpx.AsyncClient | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.client = client

    async def extract(self, image: bytes, mime_type: str) -> DiagramExtraction:
        request_client = self.client or httpx.AsyncClient(timeout=55)
        try:
            response = await request_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Title": "DiagramFlow",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64.b64encode(image).decode('ascii')}"
                                    },
                                },
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0,
                    "max_tokens": 2048,
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            graph = DiagramGraph.model_validate_json(content)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
            raise ProviderError("OpenRouter request failed or returned an invalid graph.") from exc
        finally:
            if self.client is None:
                await request_client.aclose()
        return DiagramExtraction(graph=graph, mermaid=compile_mermaid(graph), provider=self.name)


def get_provider() -> DiagramProvider:
    """Select the configured live provider, with mock mode as the no-key default."""
    provider_name = getenv("DIAGRAM_PROVIDER", "gemini").lower()
    if provider_name == "openrouter":
        api_key = getenv("OPENROUTER_API_KEY")
        if api_key:
            return OpenRouterDiagramProvider(api_key, getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it"))
        return MockDiagramProvider()

    api_key = getenv("GEMINI_API_KEY")
    if api_key:
        return GeminiDiagramProvider(api_key, getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it"))
    return MockDiagramProvider()
