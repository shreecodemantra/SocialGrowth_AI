"""
Provider-agnostic AI interfaces.

The rest of the application (content agents, image generation, scoring)
depends only on these abstractions, never on a specific vendor SDK. Swapping
OpenAI for Anthropic, or adding Stability/Runway, means writing one new
adapter class here — no business logic elsewhere changes.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    raw: dict | None = None


@dataclass
class ImageResult:
    image_bytes: bytes
    content_type: str = "image/png"
    raw: dict | None = None


@dataclass
class VideoResult:
    video_bytes: bytes
    content_type: str = "video/mp4"
    raw: dict | None = None


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, system: str | None = None, **kwargs) -> LLMResult:
        """Generate text (or JSON, if the caller instructs it in the prompt)."""


class ImageProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, width: int = 1024, height: int = 1024, **kwargs) -> ImageResult:
        """Generate a single image for the given prompt and target dimensions."""


class VideoProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, duration_seconds: int = 15, **kwargs) -> VideoResult:
        """Generate a short-form video/script-driven clip for the given prompt."""
