"""
Content Agent (spec section 6). Dispatches to a dedicated prompt + schema
per platform (spec section 5) — Instagram, LinkedIn, Facebook, and YouTube
each get their own strategy, never a copy of another platform's output.
"""
from app.agents._shared import JSONExtractionError, extract_json
from app.ai.base import LLMProvider
from app.core.logging import get_logger
from app.models.brand_profile import BrandProfile
from app.models.enums import PlatformType
from app.schemas.agents import ResearchBrief
from app.schemas.content import (
    FacebookContent,
    InstagramContent,
    LinkedInContent,
    PLATFORM_CONTENT_SCHEMAS,
    YouTubeContent,
)

logger = get_logger(__name__)

AGENT_NAME = "content_agent"


def _brand_context(brand: BrandProfile) -> str:
    return f"""Brand: {brand.brand_name} ({brand.industry or "unspecified industry"})
Tone: {brand.brand_tone or "not specified"}
CTA style: {brand.cta_style or "not specified"}
Preferred hashtags to weave in where relevant: {", ".join(brand.preferred_hashtags) or "none"}
Never use these words/phrases: {", ".join(brand.forbidden_words) or "none"}"""


def _research_context(research: ResearchBrief) -> str:
    return f"""Research brief:
Summary: {research.summary}
Key points: {"; ".join(research.key_points)}
Suggested angle: {research.suggested_angle}"""


def _prompt_for(platform: PlatformType, brand: BrandProfile, topic: str, research: ResearchBrief) -> str:
    header = f"""{_brand_context(brand)}

{_research_context(research)}

Topic: "{topic}"
"""
    if platform == PlatformType.INSTAGRAM:
        return (
            header
            + """Write Instagram content for this topic. Respond with ONLY a JSON object:
{
  "caption": "full caption, 2-4 short paragraphs, conversational",
  "hook": "first line only — must stop the scroll",
  "cta": "one sentence call to action",
  "hashtags": ["#tag1", "#tag2", "... 15-25 relevant hashtags"],
  "image_prompt": "detailed prompt for a 4:5 portrait feed image",
  "alt_text": "accessibility alt text describing the image",
  "reel_idea": "one sentence concept for a companion Reel"
}"""
        )
    if platform == PlatformType.LINKEDIN:
        return (
            header
            + """Write LinkedIn content for this topic — professional, insight-led, no emoji spam.
Respond with ONLY a JSON object:
{
  "hook": "first line — a professional pattern-interrupt or bold claim",
  "post": "full post, 3-6 short paragraphs with line breaks, professional tone",
  "cta": "one sentence professional call to action",
  "hashtags": ["#tag1", "... 3-5 relevant hashtags, LinkedIn style"],
  "image_prompt": "detailed prompt for a 1.91:1 feed graphic, professional/editorial style"
}"""
        )
    if platform == PlatformType.FACEBOOK:
        return (
            header
            + """Write Facebook content for this topic — warm, community-oriented, easy to skim.
Respond with ONLY a JSON object:
{
  "post": "full post, 2-3 short paragraphs, conversational and community-focused",
  "cta": "one sentence call to action",
  "hashtags": ["#tag1", "... 3-8 relevant hashtags"],
  "image_prompt": "detailed prompt for a Facebook feed image"
}"""
        )
    if platform == PlatformType.YOUTUBE:
        return (
            header
            + """Write YouTube content for this topic. Respond with ONLY a JSON object:
{
  "video_title": "SEO-friendly, under 70 characters, curiosity-driven",
  "description": "2-3 paragraphs, keyword-rich, includes a call to action",
  "tags": ["tag1", "... 10-15 SEO tags"],
  "keywords": ["keyword1", "... 5-10 target search keywords"],
  "thumbnail_text": "3-5 words of bold overlay text for the thumbnail",
  "thumbnail_prompt": "detailed prompt for a 16:9 thumbnail image, bold and high-contrast",
  "shorts_script": "30-45 second vertical short-form script with scene beats",
  "longform_script": "full long-form video script outline with section headers"
}"""
        )
    raise ValueError(f"Unsupported platform: {platform}")


def _fallback_content(platform: PlatformType, brand: BrandProfile, topic: str, research: ResearchBrief) -> dict:
    """Deterministic content used when the LLM doesn't return parseable JSON
    (always true for the mock provider) so the pipeline still completes end
    to end without a real LLM key configured."""
    cta = brand.cta_style or "Learn more — link in bio."
    hashtags = list(brand.preferred_hashtags) or [f"#{brand.brand_name.replace(' ', '')}"]

    if platform == PlatformType.INSTAGRAM:
        return InstagramContent(
            caption=f"{research.suggested_angle}\n\n{research.summary}",
            hook=research.suggested_angle,
            cta=cta,
            hashtags=hashtags,
            image_prompt=f"A clean, professional 4:5 portrait social graphic about '{topic}' for {brand.brand_name}, "
            f"{brand.brand_tone or 'friendly, modern'} tone, bold headline text, brand colors "
            f"{', '.join(brand.brand_colors) or 'blue and white'}.",
            alt_text=f"Graphic illustrating {topic} for {brand.brand_name}.",
            reel_idea=f"Quick-cut reel walking through: {'; '.join(research.key_points[:3])}",
        ).model_dump()
    if platform == PlatformType.LINKEDIN:
        return LinkedInContent(
            hook=research.suggested_angle,
            post=f"{research.summary}\n\n" + "\n".join(f"→ {p}" for p in research.key_points),
            cta=cta,
            hashtags=hashtags[:5],
            image_prompt=f"A professional 1.91:1 editorial-style graphic about '{topic}' for {brand.brand_name}.",
        ).model_dump()
    if platform == PlatformType.FACEBOOK:
        return FacebookContent(
            post=f"{research.summary}\n\n{research.suggested_angle}",
            cta=cta,
            hashtags=hashtags[:8],
            image_prompt=f"A warm, community-focused feed image about '{topic}' for {brand.brand_name}.",
        ).model_dump()
    if platform == PlatformType.YOUTUBE:
        return YouTubeContent(
            video_title=f"{topic} — What {brand.brand_name} Wants You To Know"[:70],
            description=f"{research.summary}\n\n{cta}",
            tags=[topic] + brand.brand_keywords,
            keywords=brand.brand_keywords or [topic],
            thumbnail_text=topic.split()[0] if topic.split() else topic,
            thumbnail_prompt=f"A bold, high-contrast 16:9 YouTube thumbnail about '{topic}' for {brand.brand_name}.",
            shorts_script=f"Hook: {research.suggested_angle}\n" + "\n".join(research.key_points[:3]),
            longform_script=f"Intro\n{research.summary}\n\nBody\n"
            + "\n".join(f"- {p}" for p in research.key_points)
            + f"\n\nOutro\n{cta}",
        ).model_dump()
    raise ValueError(f"Unsupported platform: {platform}")


async def generate_platform_content(
    llm: LLMProvider,
    brand: BrandProfile,
    topic: str,
    research: ResearchBrief,
    platform: PlatformType,
) -> tuple[dict, str, str]:
    """Returns (content_dict, prompt_sent, raw_response_text)."""
    prompt = _prompt_for(platform, brand, topic, research)
    result = await llm.generate(prompt)

    schema = PLATFORM_CONTENT_SCHEMAS[platform.value]
    try:
        content = schema(**extract_json(result.text)).model_dump()
    except (JSONExtractionError, ValueError) as exc:
        logger.info("content_agent_fallback", platform=platform.value, reason=str(exc))
        content = _fallback_content(platform, brand, topic, research)

    return content, prompt, result.text
