"""
Gemini-backed image and video ("reel") generation, using Google's
`google-genai` SDK against the Gemini Developer API (a plain GEMINI_API_KEY —
no Vertex AI / GCP project required).

- Images: Gemini 2.5 Flash Image ("Nano Banana") via `generate_content`,
  which returns inline image bytes as a response part. An Imagen model id
  (e.g. "imagen-4.0-generate-001") is also selectable via
  `GEMINI_IMAGE_MODEL` and uses the dedicated `generate_images` pipeline
  instead — Google has flagged the Imagen line for deprecation in favor of
  Nano Banana, so that stays the default.
- Video/reels: Veo (currently the 3.1 family) via `generate_videos`, a
  long-running operation that is polled until done, then downloaded as
  bytes via `files.download`. This is a paid, metered API — see
  backend/.env.example.

Both paths run against `client.aio` (the SDK's native async surface) so
neither blocks the FastAPI/Celery event loop with a synchronous HTTP call.
"""
import asyncio

from google import genai
from google.genai import types

from app.ai.base import ImageProvider, ImageResult, VideoProvider, VideoResult
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_IMAGEN_ASPECT_RATIOS = {"1:1": 1.0, "3:4": 3 / 4, "4:3": 4 / 3, "9:16": 9 / 16, "16:9": 16 / 9}
_VEO_ALLOWED_DURATIONS = (4, 6, 8)


def _closest_aspect_ratio(width: int, height: int) -> str:
    target = width / height if height else 1.0
    return min(_IMAGEN_ASPECT_RATIOS, key=lambda ratio: abs(_IMAGEN_ASPECT_RATIOS[ratio] - target))


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to backend/.env to use the Gemini "
            "image/video providers, or set IMAGE_PROVIDER/VIDEO_PROVIDER back to 'mock'."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


class GeminiImageProvider(ImageProvider):
    def __init__(self, model: str | None = None):
        self.model = model or settings.GEMINI_IMAGE_MODEL

    async def generate(self, prompt: str, *, width: int = 1024, height: int = 1024, **kwargs) -> ImageResult:
        client = _get_client()
        logger.info("gemini_image_generate", model=self.model, width=width, height=height)

        if self.model.startswith("imagen-"):
            return await self._generate_imagen(client, prompt, width, height)
        return await self._generate_native(client, prompt)

    async def _generate_imagen(
        self, client: genai.Client, prompt: str, width: int, height: int
    ) -> ImageResult:
        response = await client.aio.models.generate_images(
            model=self.model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=_closest_aspect_ratio(width, height),
            ),
        )
        if not response.generated_images:
            raise RuntimeError("Gemini (Imagen) returned no images — the prompt may have been filtered.")

        image = response.generated_images[0].image
        return ImageResult(
            image_bytes=image.image_bytes,
            content_type=image.mime_type or "image/png",
            raw={"model": self.model, "prompt": prompt},
        )

    async def _generate_native(self, client: genai.Client, prompt: str) -> ImageResult:
        response = await client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
        for part in response.parts or []:
            if part.inline_data and part.inline_data.data:
                return ImageResult(
                    image_bytes=part.inline_data.data,
                    content_type=part.inline_data.mime_type or "image/png",
                    raw={"model": self.model, "prompt": prompt},
                )
        raise RuntimeError("Gemini returned no image data — the prompt may have been filtered.")


class GeminiVideoProvider(VideoProvider):
    def __init__(self, model: str | None = None, poll_interval_seconds: float = 10.0):
        self.model = model or settings.GEMINI_VIDEO_MODEL
        self.poll_interval_seconds = poll_interval_seconds

    async def generate(self, prompt: str, *, duration_seconds: int = 8, **kwargs) -> VideoResult:
        client = _get_client()
        closest_duration = min(_VEO_ALLOWED_DURATIONS, key=lambda d: abs(d - duration_seconds))
        aspect_ratio = kwargs.get("aspect_ratio", "9:16")  # 9:16 fits Reels/Shorts by default

        logger.info("gemini_video_generate", model=self.model, duration_seconds=closest_duration, aspect_ratio=aspect_ratio)

        operation = await client.aio.models.generate_videos(
            model=self.model,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                duration_seconds=closest_duration,
            ),
        )

        while not operation.done:
            await asyncio.sleep(self.poll_interval_seconds)
            operation = await client.aio.operations.get(operation)

        if operation.error:
            raise RuntimeError(f"Veo video generation failed: {operation.error}")
        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError("Veo returned no video — the prompt may have been filtered.")

        generated_video = operation.response.generated_videos[0]
        video_bytes = await client.aio.files.download(file=generated_video.video)

        return VideoResult(
            video_bytes=video_bytes,
            content_type=generated_video.video.mime_type or "video/mp4",
            raw={"model": self.model, "prompt": prompt, "duration_seconds": closest_duration},
        )
