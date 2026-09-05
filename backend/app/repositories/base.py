"""
Generic async repository providing basic CRUD over a SQLAlchemy model.
Concrete repositories subclass this and add domain-specific queries.
"""
import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, id_)

    async def list_all(self) -> list[ModelT]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()
