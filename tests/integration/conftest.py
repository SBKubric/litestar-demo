from collections.abc import AsyncGenerator, AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from advanced_alchemy.base import BigIntAuditBase
from httpx import AsyncClient
from litestar import Litestar
from litestar.testing import AsyncTestClient
from pytest_databases.docker.postgres import PostgresService
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import app as config
from app.db.models import User
from app.domain.accounts.guards import auth
from app.domain.accounts.services import UserService

here = Path(__file__).parent
pytestmark = pytest.mark.anyio


@pytest.fixture(name="engine")
async def fx_engine(postgres_service: PostgresService) -> AsyncEngine:
    """Postgresql instance for end-to-end testing.

    Returns:
        Async SQLAlchemy engine instance.
    """
    return create_async_engine(
        URL(
            drivername="postgresql+asyncpg",
            username=postgres_service.user,
            password=postgres_service.password,
            host=postgres_service.host,
            port=postgres_service.port,
            database=postgres_service.database,
            query={},  # type:ignore[arg-type]
        ),
        echo=False,
        poolclass=NullPool,
    )


@pytest.fixture(name="sessionmaker")
async def fx_session_maker_factory(engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    yield async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(name="session")
async def fx_session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


@pytest.fixture(autouse=True)
async def _seed_db(
    engine: AsyncEngine,
    sessionmaker: async_sessionmaker[AsyncSession],
    raw_users: list[User | dict[str, Any]],
) -> AsyncGenerator[None, None]:
    """Populate test database with.

    Args:
        engine: The SQLAlchemy engine instance.
        sessionmaker: The SQLAlchemy sessionmaker factory.
        raw_users: Test users to add to the database

    """

    metadata = BigIntAuditBase.registry.metadata
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    async with UserService.new(sessionmaker()) as users_service:
        await users_service.create_many(raw_users, auto_commit=True)

    table_name = "user_account"
    pk_column = "id"
    seq_name = "user_account_id_seq"
    await sessionmaker().execute(
        text(f"SELECT setval('{seq_name}', (SELECT MAX({pk_column}) FROM {table_name}) + 1, false)")  # noqa: S608
    )
    yield


@pytest.fixture(autouse=True)
def _patch_db(
    app: "Litestar",
    engine: AsyncEngine,
    sessionmaker: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(config.alchemy, "session_maker", sessionmaker)
    monkeypatch.setattr(config.alchemy, "engine_instance", engine)


@pytest.fixture(name="client")
async def fx_client(app: Litestar) -> AsyncIterator[AsyncClient]:
    """Async client that calls requests on the app.

    ```text
    ValueError: The future belongs to a different loop than the one specified as the loop argument
    ```
    """
    async with AsyncTestClient(app) as client:
        yield client


@pytest.fixture(name="user_token_headers")
def fx_user_token_headers() -> dict[str, str]:
    """Valid user token.

    ```text
    ValueError: The future belongs to a different loop than the one specified as the loop argument
    ```
    """
    return {"Authorization": f"Bearer {auth.create_token(identifier='user@example.com')}"}
