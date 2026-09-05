"""
Orchestrates the content generation pipeline (spec section 6):

    Campaign created
        -> Research Agent (once per campaign)
        -> per platform: Content Agent -> SEO Agent -> Quality Agent
        -> per platform (optional): Image Agent, Video Agent
        -> Post + PostPlatform rows land in PENDING_REVIEW

Approval-workflow methods (approve/reject/edit/regenerate) live here too,
since they operate on the same aggregate and need the same repositories.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import content_agent, image_agent, quality_agent, research_agent, seo_agent
from app.ai.base import ImageProvider, LLMProvider, VideoProvider
from app.core.logging import get_logger
from app.models.ai_generation import AIGeneration
from app.models.asset import Asset
from app.models.brand_profile import BrandProfile
from app.models.campaign import Campaign
from app.models.enums import AssetType, CampaignStatus, PlatformType, PostStatus
from app.models.post import Post
from app.models.post_platform import PostPlatform
from app.repositories.ai_generation_repository import AIGenerationRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.post_platform_repository import PostPlatformRepository
from app.repositories.post_repository import PostRepository
from app.schemas.campaign import CampaignCreateRequest
from app.schemas.content import PLATFORM_CONTENT_SCHEMAS
from app.services.exceptions import GenerationFailedError, NotFoundError, ValidationFailedError
from app.services.storage_service import ObjectStorage

logger = get_logger(__name__)

_VIDEO_ELIGIBLE_PLATFORMS = {PlatformType.INSTAGRAM, PlatformType.YOUTUBE}


class CampaignService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.campaigns = CampaignRepository(session)
        self.posts = PostRepository(session)
        self.post_platforms = PostPlatformRepository(session)
        self.assets = AssetRepository(session)
        self.ai_generations = AIGenerationRepository(session)

    # ---- read paths -----------------------------------------------------

    async def list_campaigns(self, workspace_id: uuid.UUID) -> list[Campaign]:
        return await self.campaigns.list_for_workspace(workspace_id)

    async def get_campaign_with_posts(self, workspace_id: uuid.UUID, campaign_id: uuid.UUID) -> Campaign:
        campaign = await self.campaigns.get_with_posts(campaign_id)
        if not campaign or campaign.workspace_id != workspace_id:
            raise NotFoundError("Campaign not found.")
        return campaign

    async def _get_owned_post(self, workspace_id: uuid.UUID, post_id: uuid.UUID) -> Post:
        post = await self.posts.get_with_platforms(post_id)
        if not post or post.workspace_id != workspace_id:
            raise NotFoundError("Post not found.")
        return post

    async def get_post(self, workspace_id: uuid.UUID, post_id: uuid.UUID) -> Post:
        return await self._get_owned_post(workspace_id, post_id)

    async def list_posts(self, workspace_id: uuid.UUID) -> list[Post]:
        return await self.posts.list_for_workspace(workspace_id)

    # ---- generation -------------------------------------------------------

    async def create_and_generate(
        self,
        *,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        brand: BrandProfile,
        request: CampaignCreateRequest,
        llm: LLMProvider,
        image_provider: ImageProvider,
        video_provider: VideoProvider,
        storage: ObjectStorage,
    ) -> Campaign:
        campaign = Campaign(
            workspace_id=workspace_id,
            created_by_id=user_id,
            title=request.title,
            goal=request.goal,
            target_audience=request.target_audience,
            platforms=[p.value for p in request.platforms],
            generate_images=request.generate_images,
            generate_video=request.generate_video,
            status=CampaignStatus.GENERATING,
        )
        await self.campaigns.add(campaign)

        post = Post(
            workspace_id=workspace_id,
            campaign_id=campaign.id,
            display_id=await self.posts.next_display_id(workspace_id),
            title=request.title,
            status=PostStatus.GENERATING,
        )
        await self.posts.add(post)
        await self.posts.add_status_history(post.id, PostStatus.GENERATING, "Generation started")
        await self.session.commit()  # persist the attempt before doing slow AI calls

        try:
            audience = request.target_audience or brand.target_audience
            brief, research_prompt, research_raw = await research_agent.research(
                llm, brand, request.title, request.goal, audience
            )
            await self._log_generation(
                workspace_id, research_agent.AGENT_NAME, llm, research_prompt, research_raw,
                campaign_id=campaign.id, post_id=post.id,
            )

            for platform in request.platforms:
                await self._generate_platform(
                    workspace_id=workspace_id,
                    campaign=campaign,
                    post=post,
                    platform=platform,
                    brand=brand,
                    research_brief=brief,
                    llm=llm,
                    image_provider=image_provider,
                    video_provider=video_provider,
                    storage=storage,
                    generate_images=request.generate_images,
                    generate_video=request.generate_video,
                )

            post.status = PostStatus.PENDING_REVIEW
            await self.posts.add_status_history(post.id, PostStatus.PENDING_REVIEW, "All platforms generated")
            campaign.status = CampaignStatus.READY
            await self.session.commit()

        except Exception as exc:  # noqa: BLE001 — deliberately broad: any agent/provider failure lands here
            logger.error("campaign_generation_failed", campaign_id=str(campaign.id), error=str(exc))
            await self.session.rollback()
            # Re-fetch in a fresh transaction so we can persist the failure state cleanly.
            campaign = await self.campaigns.get_by_id(campaign.id)
            post = await self.posts.get_by_id(post.id)
            campaign.status = CampaignStatus.FAILED
            campaign.failure_reason = str(exc)[:1000]
            post.status = PostStatus.FAILED
            await self.posts.add_status_history(post.id, PostStatus.FAILED, str(exc)[:1000])
            await self.session.commit()
            raise GenerationFailedError(f"Content generation failed: {exc}") from exc

        return await self.get_campaign_with_posts(workspace_id, campaign.id)

    async def _generate_platform(
        self,
        *,
        workspace_id: uuid.UUID,
        campaign: Campaign,
        post: Post,
        platform: PlatformType,
        brand: BrandProfile,
        research_brief,
        llm: LLMProvider,
        image_provider: ImageProvider,
        video_provider: VideoProvider,
        storage: ObjectStorage,
        generate_images: bool,
        generate_video: bool,
    ) -> PostPlatform:
        content, prompt, raw = await content_agent.generate_platform_content(
            llm, brand, post.title, research_brief, platform
        )
        await self._log_generation(
            workspace_id, content_agent.AGENT_NAME, llm, prompt, raw,
            campaign_id=campaign.id, post_id=post.id,
        )

        content = seo_agent.enrich_hashtags(content, brand, platform)
        quality = quality_agent.check_content(content, brand)
        if not quality.passed:
            logger.info("quality_agent_flagged", platform=platform.value, violations=quality.violations)

        post_platform = PostPlatform(
            post_id=post.id,
            platform=platform,
            content=content,
            status=PostStatus.PENDING_REVIEW,
            quality_violations=quality.violations,
        )
        await self.post_platforms.add(post_platform)

        if generate_images:
            asset = await self._generate_image_asset(
                workspace_id, campaign.id, post.id, post_platform, brand, content, platform, image_provider, storage
            )
            post_platform.primary_asset_id = asset.id

        if generate_video and platform in _VIDEO_ELIGIBLE_PLATFORMS:
            await self._generate_video_asset(
                workspace_id, campaign.id, post.id, post_platform, content, platform, video_provider, storage
            )

        return post_platform

    async def _generate_image_asset(
        self, workspace_id, campaign_id, post_id, post_platform, brand, content, platform, image_provider, storage
    ) -> Asset:
        generated = await image_agent.generate_for_platform(image_provider, storage, brand, content, platform)
        asset = Asset(
            workspace_id=workspace_id,
            campaign_id=campaign_id,
            post_id=post_id,
            post_platform_id=post_platform.id,
            asset_type=AssetType.IMAGE,
            storage_url=generated.storage_url,
            content_type=generated.content_type,
            width=generated.width,
            height=generated.height,
            generation_prompt=generated.prompt,
        )
        await self.assets.add(asset)
        await self._log_generation(
            workspace_id, image_agent.AGENT_NAME, image_provider, generated.prompt, None,
            campaign_id=campaign_id, post_id=post_id, post_platform_id=post_platform.id,
        )
        return asset

    async def _generate_video_asset(
        self, workspace_id, campaign_id, post_id, post_platform, content, platform, video_provider, storage
    ) -> Asset:
        prompt = content.get("reel_idea") or content.get("shorts_script") or ""
        result = await video_provider.generate(prompt, duration_seconds=8, aspect_ratio="9:16")
        storage_url = storage.upload_bytes(
            result.video_bytes, content_type=result.content_type, key_prefix=f"assets/{platform.value.lower()}"
        )
        asset = Asset(
            workspace_id=workspace_id,
            campaign_id=campaign_id,
            post_id=post_id,
            post_platform_id=post_platform.id,
            asset_type=AssetType.VIDEO,
            storage_url=storage_url,
            content_type=result.content_type,
            generation_prompt=prompt,
        )
        await self.assets.add(asset)
        await self._log_generation(
            workspace_id, "video_agent", video_provider, prompt, None,
            campaign_id=campaign_id, post_id=post_id, post_platform_id=post_platform.id,
        )
        return asset

    async def _log_generation(
        self, workspace_id, agent_name, provider, prompt, raw_text, *, campaign_id=None, post_id=None, post_platform_id=None
    ) -> None:
        self.session.add(
            AIGeneration(
                workspace_id=workspace_id,
                campaign_id=campaign_id,
                post_id=post_id,
                post_platform_id=post_platform_id,
                agent_name=agent_name,
                provider=type(provider).__name__,
                model=getattr(provider, "model", None),
                prompt=prompt,
                raw_response={"text": raw_text} if raw_text is not None else None,
            )
        )
        await self.session.flush()

    # ---- approval workflow ------------------------------------------------

    def _get_platform_or_raise(self, post: Post, platform: PlatformType) -> PostPlatform:
        for pp in post.platforms:
            if pp.platform == platform:
                return pp
        raise NotFoundError(f"Post has no {platform.value} content.")

    async def approve_platform(self, workspace_id: uuid.UUID, post_id: uuid.UUID, platform: PlatformType) -> PostPlatform:
        post = await self._get_owned_post(workspace_id, post_id)
        pp = self._get_platform_or_raise(post, platform)
        pp.status = PostStatus.APPROVED

        if all(p.status == PostStatus.APPROVED for p in post.platforms):
            post.status = PostStatus.APPROVED
            await self.posts.add_status_history(post.id, PostStatus.APPROVED, "All platforms approved")

        await self.session.commit()
        return pp

    async def reject_platform(self, workspace_id: uuid.UUID, post_id: uuid.UUID, platform: PlatformType) -> PostPlatform:
        post = await self._get_owned_post(workspace_id, post_id)
        pp = self._get_platform_or_raise(post, platform)
        pp.status = PostStatus.CANCELLED
        await self.session.commit()
        return pp

    async def update_platform_content(
        self, workspace_id: uuid.UUID, post_id: uuid.UUID, platform: PlatformType, brand: BrandProfile, new_content: dict
    ) -> PostPlatform:
        post = await self._get_owned_post(workspace_id, post_id)
        pp = self._get_platform_or_raise(post, platform)

        if pp.status in (PostStatus.PUBLISHING, PostStatus.PUBLISHED):
            raise ValidationFailedError("Cannot edit a post that has already been published.")

        schema = PLATFORM_CONTENT_SCHEMAS[platform.value]
        try:
            validated = schema(**new_content).model_dump()
        except Exception as exc:  # pydantic.ValidationError
            raise ValidationFailedError(f"Invalid content for {platform.value}: {exc}") from exc

        validated = seo_agent.enrich_hashtags(validated, brand, platform)
        quality = quality_agent.check_content(validated, brand)

        pp.content = validated
        pp.quality_violations = quality.violations
        pp.status = PostStatus.PENDING_REVIEW  # edited content needs re-review even if it was approved
        await self.session.commit()
        return pp

    async def regenerate_platform(
        self,
        workspace_id: uuid.UUID,
        post_id: uuid.UUID,
        platform: PlatformType,
        brand: BrandProfile,
        llm: LLMProvider,
        image_provider: ImageProvider,
        storage: ObjectStorage,
        *,
        regenerate_image: bool = True,
    ) -> PostPlatform:
        post = await self._get_owned_post(workspace_id, post_id)
        pp = self._get_platform_or_raise(post, platform)
        if pp.status in (PostStatus.PUBLISHING, PostStatus.PUBLISHED):
            raise ValidationFailedError("Cannot regenerate a post that has already been published.")

        brief, research_prompt, research_raw = await research_agent.research(
            llm, brand, post.title, None, brand.target_audience
        )
        await self._log_generation(
            workspace_id, research_agent.AGENT_NAME, llm, research_prompt, research_raw,
            campaign_id=post.campaign_id, post_id=post.id,
        )

        content, prompt, raw = await content_agent.generate_platform_content(llm, brand, post.title, brief, platform)
        await self._log_generation(
            workspace_id, content_agent.AGENT_NAME, llm, prompt, raw, campaign_id=post.campaign_id, post_id=post.id,
        )
        content = seo_agent.enrich_hashtags(content, brand, platform)
        quality = quality_agent.check_content(content, brand)

        pp.content = content
        pp.quality_violations = quality.violations
        pp.status = PostStatus.PENDING_REVIEW

        if regenerate_image:
            asset = await self._generate_image_asset(
                workspace_id, post.campaign_id, post.id, pp, brand, content, platform, image_provider, storage
            )
            pp.primary_asset_id = asset.id

        await self.posts.add_status_history(post.id, PostStatus.PENDING_REVIEW, f"Regenerated {platform.value} content")
        await self.session.commit()
        return pp
