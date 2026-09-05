"""
Deterministic, zero-cost providers used for local development, tests, and
CI. Selected whenever `LLM_PROVIDER=mock` / `IMAGE_PROVIDER=mock` /
`VIDEO_PROVIDER=mock` (the default) so the pipeline is exercisable without
any vendor API keys configured.
"""
import base64

from app.ai.base import ImageProvider, ImageResult, LLMProvider, LLMResult, VideoProvider, VideoResult


class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, *, system: str | None = None, **kwargs) -> LLMResult:
        preview = prompt.strip().splitlines()[0][:120] if prompt.strip() else ""
        return LLMResult(text=f"[mock-generated content for: {preview}]", raw={"prompt": prompt, "system": system})


# 1x1 transparent PNG, used as a stand-in "generated" image in mock mode.
_BLANK_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class MockImageProvider(ImageProvider):
    async def generate(self, prompt: str, *, width: int = 1024, height: int = 1024, **kwargs) -> ImageResult:
        return ImageResult(image_bytes=_BLANK_PNG, content_type="image/png", raw={"prompt": prompt, "width": width, "height": height})


class MockVideoProvider(VideoProvider):
    async def generate(self, prompt: str, *, duration_seconds: int = 15, **kwargs) -> VideoResult:
        return VideoResult(video_bytes=b"", content_type="video/mp4", raw={"prompt": prompt, "duration_seconds": duration_seconds, "note": "mock provider returns no real video bytes"})
