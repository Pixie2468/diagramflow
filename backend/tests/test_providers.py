import asyncio
import base64
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx

from backend.providers import GeminiDiagramProvider, MockDiagramProvider, OpenRouterDiagramProvider, ProviderError, get_provider


class FakeModels:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.kwargs: dict[str, object] | None = None

    async def generate_content(self, **kwargs: object) -> object:
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, models: FakeModels) -> None:
        self.aio = SimpleNamespace(models=models)


class GeminiProviderTests(unittest.TestCase):
    def test_selects_gemini_when_a_key_is_configured(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True):
            self.assertIsInstance(get_provider(), GeminiDiagramProvider)

    def test_selects_mock_without_a_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsInstance(get_provider(), MockDiagramProvider)

    def test_selects_openrouter_when_requested_and_key_is_configured(self) -> None:
        with patch.dict(
            "os.environ",
            {"DIAGRAM_PROVIDER": "openrouter", "OPENROUTER_API_KEY": "test-key"},
            clear=True,
        ):
            self.assertIsInstance(get_provider(), OpenRouterDiagramProvider)

    def test_sends_the_image_and_enforces_the_graph_schema(self) -> None:
        models = FakeModels(
            SimpleNamespace(
                text='{"direction":"TD","nodes":[{"id":"start","label":"Start","shape_type":"rounded"}],"edges":[]}'
            )
        )
        provider = GeminiDiagramProvider("test-key", "gemma-4-26b-a4b-it", client=FakeClient(models))

        result = asyncio.run(provider.extract(b"image-bytes", "image/png"))

        self.assertEqual(result.provider, "gemini")
        self.assertEqual(result.graph.nodes[0].id, "start")
        self.assertEqual(models.kwargs["model"], "gemma-4-26b-a4b-it")
        config = models.kwargs["config"]
        self.assertEqual(config.response_mime_type, "application/json")
        self.assertIsNone(config.response_json_schema)

    def test_converts_invalid_structured_output_to_a_provider_error(self) -> None:
        models = FakeModels(SimpleNamespace(text='{"nodes":[],"edges":[]}'))
        provider = GeminiDiagramProvider("test-key", "gemma-4-26b-a4b-it", client=FakeClient(models))

        with self.assertRaises(ProviderError):
            asyncio.run(provider.extract(b"image-bytes", "image/png"))


class OpenRouterDiagramProviderTests(unittest.TestCase):
    def test_extract_sends_correct_payload_and_returns_extraction(self) -> None:
        captured_request = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured_request["url"] = str(request.url)
            captured_request["headers"] = dict(request.headers)
            captured_request["json"] = json.loads(request.read())
            response_data = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({
                                "direction": "LR",
                                "nodes": [
                                    {"id": "a", "label": "Service A", "shape_type": "rectangle"},
                                    {"id": "b", "label": "Service B", "shape_type": "cylinder"},
                                ],
                                "edges": [
                                    {
                                        "source": "a",
                                        "target": "b",
                                        "label": "query",
                                        "confidence": "high",
                                        "alternatives": [],
                                    }
                                ],
                            })
                        }
                    }
                ]
            }
            return httpx.Response(200, json=response_data)

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenRouterDiagramProvider(
            api_key="sk-or-test-key",
            model="google/gemma-4-31b-it",
            client=client,
        )

        test_bytes = b"fake-png-bytes"
        result = asyncio.run(provider.extract(test_bytes, "image/png"))

        self.assertEqual(result.provider, "openrouter")
        self.assertEqual(result.graph.direction, "LR")
        self.assertEqual(len(result.graph.nodes), 2)
        self.assertEqual(result.graph.nodes[0].id, "a")
        self.assertEqual(result.graph.nodes[1].id, "b")
        self.assertIn('a["Service A"]', result.mermaid)
        self.assertIn('b[("Service B")]', result.mermaid)
        self.assertIn("a -->|query| b", result.mermaid)

        self.assertEqual(captured_request["url"], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(captured_request["headers"]["authorization"], "Bearer sk-or-test-key")
        self.assertEqual(captured_request["headers"]["x-title"], "DiagramFlow")
        payload = captured_request["json"]
        self.assertEqual(payload["model"], "google/gemma-4-31b-it")
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        user_message = payload["messages"][0]
        self.assertEqual(user_message["role"], "user")
        self.assertEqual(user_message["content"][0]["type"], "text")
        self.assertEqual(user_message["content"][1]["type"], "image_url")
        expected_url = f"data:image/png;base64,{base64.b64encode(test_bytes).decode('ascii')}"
        self.assertEqual(user_message["content"][1]["image_url"]["url"], expected_url)

    def test_extract_raises_provider_error_on_http_failure(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="Internal Server Error")

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenRouterDiagramProvider("test-key", "test-model", client=client)

        with self.assertRaises(ProviderError):
            asyncio.run(provider.extract(b"bytes", "image/png"))

    def test_extract_raises_provider_error_on_invalid_json(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "not-valid-json"}}]},
            )

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenRouterDiagramProvider("test-key", "test-model", client=client)

        with self.assertRaises(ProviderError):
            asyncio.run(provider.extract(b"bytes", "image/png"))

    def test_extract_raises_provider_error_on_schema_violation(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": '{"edges": []}'}}]},
            )

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenRouterDiagramProvider("test-key", "test-model", client=client)

        with self.assertRaises(ProviderError):
            asyncio.run(provider.extract(b"bytes", "image/png"))

    def test_extract_raises_provider_error_on_malformed_response_structure(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"choices": []})

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenRouterDiagramProvider("test-key", "test-model", client=client)

        with self.assertRaises(ProviderError):
            asyncio.run(provider.extract(b"bytes", "image/png"))

    def test_extract_closes_client_when_created_internally(self) -> None:
        mock_client = unittest.mock.AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")
        with patch("backend.providers.httpx.AsyncClient", return_value=mock_client):
            provider = OpenRouterDiagramProvider("test-key", "test-model")
            with self.assertRaises(ProviderError):
                asyncio.run(provider.extract(b"bytes", "image/png"))
            mock_client.aclose.assert_awaited_once()

