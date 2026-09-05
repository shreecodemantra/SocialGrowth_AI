"""
Test fixtures: an in-memory SQLite database (async, via aiosqlite) wired in
place of Postgres so unit/integration tests never touch a real database or
external service. Postgres-only features (native UUID/ENUM/JSONB) are
avoided in app code specifically so this works — see models/mixins.py.
"""
import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base_all import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
