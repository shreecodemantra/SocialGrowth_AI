import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_image_provider, get_llm_provider, get_video_provider
from app.api.deps import require_any_member, require_editor
from app.db.session import get_db
from app.models.workspace_member import WorkspaceMember
from app.schemas.campaign import CampaignCreateRequest, CampaignDetailOut, CampaignOut
from app.services.brand_service import BrandService
from app.services.campaign_service import CampaignService
from app.services.exceptions import DomainError
from app.services.storage_service import get_storage_service

router = APIRouter(prefix="/workspaces/{workspace_id}/campaigns", tags=["campaigns"])


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
                "message": "Set up a brand profile for this workspace before generating content.",
                "retryable": False,
            },
        },
    )


@router.post("", response_model=CampaignDetailOut, status_code=201)
async def create_campaign(
    workspace_id: uuid.UUID,
    data: CampaignCreateRequest,
    membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
    llm=Depends(get_llm_provider),
    image_provider=Depends(get_image_provider),
    video_provider=Depends(get_video_provider),
    storage=Depends(get_storage_service),
):
    brand = await BrandService(db).get(workspace_id)
    if not brand:
        raise _require_brand_profile_error()

    service = CampaignService(db)
    try:
        return await service.create_and_generate(
            workspace_id=workspace_id,
            user_id=membership.user_id,
            brand=brand,
            request=data,
            llm=llm,
            image_provider=image_provider,
            video_provider=video_provider,
            storage=storage,
        )
    except DomainError as exc:
        _raise_domain_error(exc)


@router.get("", response_model=list[CampaignOut])
async def list_campaigns(
    workspace_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_any_member),
    db: AsyncSession = Depends(get_db),
):
    service = CampaignService(db)
    return await service.list_campaigns(workspace_id)


@router.get("/{campaign_id}", response_model=CampaignDetailOut)
async def get_campaign(
    workspace_id: uuid.UUID,
    campaign_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_any_member),
    db: AsyncSession = Depends(get_db),
):
    service = CampaignService(db)
    try:
        return await service.get_campaign_with_posts(workspace_id, campaign_id)
    except DomainError as exc:
        _raise_domain_error(exc)


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    workspace_id: uuid.UUID,
    campaign_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    service = CampaignService(db)
    try:
        await service.delete_campaign(workspace_id, campaign_id)
    except DomainError as exc:
        _raise_domain_error(exc)
