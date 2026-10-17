"""FastAPI entrypoint for DiagramFlow's stateless extraction API."""

from os import getenv
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .image_processing import MAX_IMAGE_BYTES, prepare_image
from .models import DiagramExtraction
from .providers import get_provider


def create_app() -> FastAPI:
    app = FastAPI(title="DiagramFlow API", version="0.1.0")
    origins = [origin.strip() for origin in getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/healthz", tags=["system"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/diagrams:extract", response_model=DiagramExtraction, tags=["diagrams"])
    async def extract_diagram(image: Annotated[UploadFile, File(description="PNG, JPEG, or WebP whiteboard image")]) -> DiagramExtraction:
        raw_image = await image.read(MAX_IMAGE_BYTES + 1)
        await image.close()
        prepared_image, mime_type = prepare_image(raw_image, image.content_type)
        return get_provider().extract(prepared_image, mime_type)

    return app


app = create_app()
