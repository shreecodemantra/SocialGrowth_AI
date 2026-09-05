"""
Research Agent (spec section 6, step 1 of the pipeline).

Grounds the rest of the pipeline with a short brief before any platform
content is written, so Instagram/LinkedIn/Facebook/YouTube content all
argue the same underlying angle instead of improvising independently.
"""
from app.agents._shared import JSONExtractionError, extract_json
from app.ai.base import LLMProvider
from app.core.logging import get_logger
from app.models.brand_profile import BrandProfile
from app.schemas.agents import ResearchBrief

logger = get_logger(__name__)

AGENT_NAME = "research_agent"


def _build_prompt(brand: BrandProfile, topic: str, goal: str | None, audience: list[str]) -> str:
    audience_line = ", ".join(audience or brand.target_audience) or "general audience"
    return f"""You are a social media research analyst for the brand "{brand.brand_name}"
({brand.industry or "unspecified industry"}).

Brand tone: {brand.brand_tone or "not specified"}
Brand keywords: {", ".join(brand.brand_keywords) or "none"}
Target audience: {audience_line}

Topic to research: "{topic}"
Campaign goal: {goal or "brand awareness"}

Produce a short research brief a content writer can use to write platform-specific
posts about this topic. Respond with ONLY a JSON object matching this shape:
{{
  "summary": "2-3 sentence summary of the angle to take",
  "key_points": ["point 1", "point 2", "point 3"],
  "suggested_angle": "one sentence describing the hook/angle to lead with"
}}"""


def _fallback_brief(topic: str, audience: list[str]) -> ResearchBrief:
    """Used when the configured LLM provider doesn't return parseable JSON
    (always true for the mock provider) so the pipeline still completes."""
    return ResearchBrief(
        summary=f"A practical, audience-relevant take on '{topic}'.",
        key_points=[
            f"Why '{topic}' matters to {', '.join(audience) if audience else 'the target audience'}",
            "A concrete, actionable takeaway",
            "A call to action relevant to the brand",
        ],
        suggested_angle=f"Lead with a concrete benefit of '{topic}' before any promotional content.",
    )


async def research(
    llm: LLMProvider, brand: BrandProfile, topic: str, goal: str | None, audience: list[str]
) -> tuple[ResearchBrief, str, str]:
    """Returns (brief, prompt_sent, raw_response_text) — the latter two are for AIGeneration audit logging."""
    prompt = _build_prompt(brand, topic, goal, audience)
    result = await llm.generate(prompt)

    try:
        brief = ResearchBrief(**extract_json(result.text))
    except (JSONExtractionError, ValueError) as exc:
        logger.info("research_agent_fallback", reason=str(exc))
        brief = _fallback_brief(topic, audience)

    return brief, prompt, result.text
