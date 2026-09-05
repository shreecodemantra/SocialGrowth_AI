import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_image_provider, get_llm_provider
from app.api.deps import require_any_member, require_editor
from app.db.session import get_db
from app.models.enums import PlatformType
from app.models.workspace_member import WorkspaceMember
from app.schemas.campaign import PostOut, PostPlatformOut, PostPlatformUpdateRequest
from app.services.brand_service import BrandService
from app.services.campaign_service import CampaignService
from app.services.exceptions import DomainError
from app.services.storage_service import get_storage_service

router = APIRouter(prefix="/workspaces/{workspace_id}/posts", tags=["posts"])


def _raise_domain_error(exc: DomainError):
    raise HTTPException(
        status_code=exc.status_code,
        detail={"success": False, "error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable}},
    )


def _require_brand_profile_error() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "success": False,
            "error": {
                "code": "BRAND_PROFILE_REQUIRED",
                "message": "Set up a brand profile for this workspace first.",
                "retryable": False,
            },
        },
    )


@router.get("", response_model=list[PostOut])
async def list_posts(
    workspace_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_any_member),
    db: AsyncSession = Depends(get_db),
):
    return await CampaignService(db).list_posts(workspace_id)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    workspace_id: uuid.UUID,
    post_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_any_member),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await CampaignService(db).get_post(workspace_id, post_id)
    except DomainError as exc:
        _raise_domain_error(exc)


@router.post("/{post_id}/platforms/{platform}/approve", response_model=PostPlatformOut)
async def approve_platform(
    workspace_id: uuid.UUID,
    post_id: uuid.UUID,
    platform: PlatformType,
    _membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await CampaignService(db).approve_platform(workspace_id, post_id, platform)
    except DomainError as exc:
        _raise_domain_error(exc)


@router.post("/{post_id}/platforms/{platform}/reject", response_model=PostPlatformOut)
async def reject_platform(
    workspace_id: uuid.UUID,
    post_id: uuid.UUID,
    platform: PlatformType,
    _membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await CampaignService(db).reject_platform(workspace_id, post_id, platform)
    except DomainError as exc:
        _raise_domain_error(exc)


@router.patch("/{post_id}/platforms/{platform}", response_model=PostPlatformOut)
async def update_platform_content(
    workspace_id: uuid.UUID,
    post_id: uuid.UUID,
    platform: PlatformType,
    data: PostPlatformUpdateRequest,
    _membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    brand = await BrandService(db).get(workspace_id)
    if not brand:
        raise _require_brand_profile_error()
    try:
        return await CampaignService(db).update_platform_content(workspace_id, post_id, platform, brand, data.content)
    except DomainError as exc:
        _raise_domain_error(exc)


@router.post("/{post_id}/platforms/{platform}/regenerate", response_model=PostPlatformOut)
async def regenerate_platform(
    workspace_id: uuid.UUID,
    post_id: uuid.UUID,
    platform: PlatformType,
    _membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
    llm=Depends(get_llm_provider),
    image_provider=Depends(get_image_provider),
    storage=Depends(get_storage_service),
):
    brand = await BrandService(db).get(workspace_id)
    if not brand:
        raise _require_brand_profile_error()
    try:
        return await CampaignService(db).regenerate_platform(
            workspace_id, post_id, platform, brand, llm, image_provider, storage
        )
    except DomainError as exc:
        _raise_domain_error(exc)
