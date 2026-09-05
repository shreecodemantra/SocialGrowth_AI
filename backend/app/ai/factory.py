"""
Provider factory: reads `settings.LLM_PROVIDER` / `IMAGE_PROVIDER` /
`VIDEO_PROVIDER` and returns the configured adapter. Real vendor adapters
(OpenAI, Anthropic, Stability, ...) are added in Phase 2 alongside content
generation and registered here — business logic always depends on the
`app.ai.base` interfaces, never on these concrete classes.
"""
from app.ai.base import ImageProvider, LLMProvider, VideoProvider
from app.ai.providers.mock import MockImageProvider, MockLLMProvider, MockVideoProvider
from app.core.config import settings

# Imported lazily inside the functions below so `google-genai` is only
# required when GEMINI_* providers are actually selected.


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER == "mock":
        return MockLLMProvider()
    raise NotImplementedError(
        f"LLM provider '{settings.LLM_PROVIDER}' is not implemented yet. "
        "Add an adapter under app/ai/providers/ and register it here."
    )


def get_image_provider() -> ImageProvider:
    if settings.IMAGE_PROVIDER == "mock":
        return MockImageProvider()
    if settings.IMAGE_PROVIDER == "gemini":
        from app.ai.providers.gemini import GeminiImageProvider

        return GeminiImageProvider()
    raise NotImplementedError(
        f"Image provider '{settings.IMAGE_PROVIDER}' is not implemented yet. "
        "Add an adapter under app/ai/providers/ and register it here."
    )


def get_video_provider() -> VideoProvider:
    if settings.VIDEO_PROVIDER == "mock":
        return MockVideoProvider()
    if settings.VIDEO_PROVIDER == "gemini":
        from app.ai.providers.gemini import GeminiVideoProvider

        return GeminiVideoProvider()
    raise NotImplementedError(
        f"Video provider '{settings.VIDEO_PROVIDER}' is not implemented yet. "
        "Add an adapter under app/ai/providers/ and register it here."
    )
