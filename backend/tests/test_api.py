import asyncio
import unittest
from io import BytesIO

import httpx
from PIL import Image

from backend.main import create_app


def png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (8, 8), "white").save(output, format="PNG")
    return output.getvalue()


class ApiTests(unittest.TestCase):
    async def post_image(self, filename: str, payload: bytes, mime_type: str) -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/v1/diagrams:extract",
                files={"image": (filename, payload, mime_type)},
            )

    def test_extracts_a_mock_diagram_without_an_api_key(self) -> None:
        response = asyncio.run(self.post_image("board.png", png_bytes(), "image/png"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["provider"], "mock")
        self.assertEqual(body["graph"]["direction"], "TD")
        self.assertTrue(body["mermaid"].startswith("flowchart TD"))

    def test_rejects_an_unsupported_upload_type(self) -> None:
        response = asyncio.run(self.post_image("board.gif", b"not-an-image", "image/gif"))
        self.assertEqual(response.status_code, 415)
