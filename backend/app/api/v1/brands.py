import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_any_member, require_editor
from app.db.session import get_db
from app.models.workspace_member import WorkspaceMember
from app.schemas.brand import BrandProfileOut, BrandProfileUpsert
from app.services.brand_service import BrandService

router = APIRouter(prefix="/workspaces/{workspace_id}/brand", tags=["brand"])


@router.get("", response_model=BrandProfileOut | None)
async def get_brand_profile(
    workspace_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_any_member),
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)
    profile = await service.get(workspace_id)
    return profile


@router.put("", response_model=BrandProfileOut)
async def upsert_brand_profile(
    workspace_id: uuid.UUID,
    data: BrandProfileUpsert,
    _membership: WorkspaceMember = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)
    return await service.upsert(workspace_id, data)
