import asyncio
import unittest
from io import BytesIO

import httpx
from PIL import Image

from backend.main import create_app
from backend.providers import MockDiagramProvider, ProviderError


def image_bytes(image_format: str = "PNG") -> bytes:
    output = BytesIO()
    Image.new("RGB", (8, 8), "white").save(output, format=image_format)
    return output.getvalue()


class ApiTests(unittest.TestCase):
    async def post_image(self, filename: str, payload: bytes, mime_type: str, app=None) -> httpx.Response:
        if app is None:
            app = create_app(provider_factory=lambda: MockDiagramProvider())
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/v1/diagrams:extract",
                files={"image": (filename, payload, mime_type)},
            )

    def test_extracts_a_mock_diagram_without_an_api_key(self) -> None:
        response = asyncio.run(self.post_image("board.png", image_bytes(), "image/png"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["provider"], "mock")
        self.assertEqual(body["graph"]["direction"], "TD")
        self.assertTrue(body["mermaid"].startswith("flowchart TD"))

    def test_rejects_a_genuine_unsupported_image_format(self) -> None:
        response = asyncio.run(self.post_image("board.gif", image_bytes("GIF"), "image/gif"))
        self.assertEqual(response.status_code, 415)

    def test_rejects_invalid_image_bytes(self) -> None:
        response = asyncio.run(self.post_image("board.png", b"not-an-image", "image/png"))
        self.assertEqual(response.status_code, 422)

    def test_accepts_valid_webp_when_the_client_sends_a_generic_mime_type(self) -> None:
        response = asyncio.run(self.post_image("board.webp", image_bytes("WEBP"), "application/octet-stream"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["provider"], "mock")

    def test_returns_a_safe_upstream_error_when_gemini_fails(self) -> None:
        class FailingProvider:
            async def extract(self, image: bytes, mime_type: str) -> object:
                raise ProviderError("credential detail must not reach clients")

        app = create_app(provider_factory=lambda: FailingProvider())
        response = asyncio.run(self.post_image("board.png", image_bytes(), "image/png", app))
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "The diagram provider could not process this image. Please try again.")
