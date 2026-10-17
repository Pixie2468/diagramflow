"""FastAPI entrypoint for DiagramFlow's stateless extraction API."""

from pathlib import Path
from typing import Annotated, Callable

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .image_processing import MAX_IMAGE_BYTES, prepare_image
from .models import DiagramExtraction
from .providers import DiagramProvider, ProviderError, get_provider

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def create_app(
    provider_factory: Callable[[], DiagramProvider] = get_provider,
) -> FastAPI:
    app = FastAPI(title="DiagramFlow API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/healthz", tags=["system"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/v1/diagrams:extract", response_model=DiagramExtraction, tags=["diagrams"]
    )
    async def extract_diagram(
        image: Annotated[
            UploadFile, File(description="PNG, JPEG, or WebP whiteboard image")
        ],
    ) -> DiagramExtraction:
        raw_image = await image.read(MAX_IMAGE_BYTES + 1)
        await image.close()
        prepared_image, mime_type = prepare_image(raw_image, image.content_type)
        try:
            return await provider_factory().extract(prepared_image, mime_type)
        except ProviderError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                "The diagram provider could not process this image. Please try again.",
            ) from exc

    return app


app = create_app()
