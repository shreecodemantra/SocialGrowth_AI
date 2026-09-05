import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.workspace_member import WorkspaceRole


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)


class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    owner_id: uuid.UUID


class WorkspaceMemberInvite(BaseModel):
    email: str
    role: WorkspaceRole = WorkspaceRole.VIEWER


class WorkspaceMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    role: WorkspaceRole
