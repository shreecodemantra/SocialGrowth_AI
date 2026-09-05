import pytest

from app.agents import content_agent, quality_agent, research_agent, seo_agent
from app.ai.providers.mock import MockLLMProvider
from app.models.brand_profile import BrandProfile
from app.models.enums import PlatformType
from app.schemas.agents import ResearchBrief


def _brand(**overrides) -> BrandProfile:
    defaults = dict(
        brand_name="Shree Code Mantra",
        industry="Education / Technology",
        target_audience=["Final-year students"],
        brand_tone="Friendly, expert, encouraging",
        brand_keywords=["Python", "FastAPI", "AI"],
        forbidden_words=[],
        cta_style="Direct, link in bio",
        preferred_hashtags=["#AI", "#Python"],
        brand_colors=["#4f46e5"],
    )
    defaults.update(overrides)
    return BrandProfile(**defaults)


@pytest.mark.asyncio
async def test_research_agent_falls_back_with_mock_llm():
    brief, prompt, raw = await research_agent.research(
        MockLLMProvider(), _brand(), "AI Projects for Students", "Brand Awareness", ["Students"]
    )
    assert isinstance(brief, ResearchBrief)
    assert brief.summary
    assert len(brief.key_points) >= 1
    assert "AI Projects for Students" in prompt


@pytest.mark.asyncio
async def test_content_agent_produces_distinct_content_per_platform():
    brand = _brand()
    research = ResearchBrief(
        summary="Students want practical AI project ideas.",
        key_points=["Build a resume-worthy project", "Use free tools", "Ship something real"],
        suggested_angle="Start with one small AI project this week.",
    )

    ig_content, _, _ = await content_agent.generate_platform_content(
        MockLLMProvider(), brand, "AI Projects for Students", research, PlatformType.INSTAGRAM
    )
    li_content, _, _ = await content_agent.generate_platform_content(
        MockLLMProvider(), brand, "AI Projects for Students", research, PlatformType.LINKEDIN
    )

    assert set(ig_content.keys()) == {"caption", "hook", "cta", "hashtags", "image_prompt", "alt_text", "reel_idea"}
    assert set(li_content.keys()) == {"hook", "post", "cta", "hashtags", "image_prompt"}
    assert ig_content["caption"] != li_content["post"]


def test_seo_agent_merges_and_caps_hashtags():
    brand = _brand(preferred_hashtags=["#AI", "#Python"])
    content = {"hashtags": ["#ai", "#coding"] + [f"#tag{i}" for i in range(30)]}

    enriched = seo_agent.enrich_hashtags(content, brand, PlatformType.INSTAGRAM)

    assert len(enriched["hashtags"]) <= 25
    # "#ai" (existing, different case) should be deduped against brand's "#AI"
    assert enriched["hashtags"].count("#ai") + enriched["hashtags"].count("#AI") == 1


def test_seo_agent_respects_linkedin_cap():
    brand = _brand(preferred_hashtags=[])
    content = {"hashtags": [f"#tag{i}" for i in range(10)]}
    enriched = seo_agent.enrich_hashtags(content, brand, PlatformType.LINKEDIN)
    assert len(enriched["hashtags"]) <= 5


def test_quality_agent_flags_forbidden_words():
    brand = _brand(forbidden_words=["guaranteed job"])
    content = {"caption": "This program offers a guaranteed job after graduation."}

    result = quality_agent.check_content(content, brand)

    assert result.passed is False
    assert any("guaranteed job" in v for v in result.violations)


def test_quality_agent_passes_clean_content():
    brand = _brand(forbidden_words=["guaranteed job"])
    content = {"caption": "Build real projects and grow your skills."}

    result = quality_agent.check_content(content, brand)

    assert result.passed is True
    assert result.violations == []
