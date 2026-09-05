import pytest

from app.ai.providers.gemini import GeminiImageProvider, GeminiVideoProvider, _closest_aspect_ratio
from app.core.config import settings


def test_closest_aspect_ratio_picks_portrait_for_reels():
    assert _closest_aspect_ratio(1080, 1920) == "9:16"
    assert _closest_aspect_ratio(1920, 1080) == "16:9"
    assert _closest_aspect_ratio(1080, 1080) == "1:1"


@pytest.mark.asyncio
async def test_gemini_image_provider_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    provider = GeminiImageProvider()
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is not set"):
        await provider.generate("A robot holding a red skateboard")


@pytest.mark.asyncio
async def test_gemini_video_provider_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    provider = GeminiVideoProvider()
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is not set"):
        await provider.generate("A 15-second reel about AI projects for students")


def test_factory_routes_to_gemini(monkeypatch):
    from app.ai.factory import get_image_provider, get_video_provider

    monkeypatch.setattr(settings, "IMAGE_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "VIDEO_PROVIDER", "gemini")

    assert isinstance(get_image_provider(), GeminiImageProvider)
    assert isinstance(get_video_provider(), GeminiVideoProvider)
