from __future__ import annotations

from typing import Any

from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository,
)
from advanced_alchemy.service import (
    ModelDictT,
    SQLAlchemyAsyncRepositoryService,
)
from litestar.exceptions import PermissionDeniedException

from app.db import models as m
from app.lib import crypt


class UserService(SQLAlchemyAsyncRepositoryService[m.User]):
    """Handles database operations for users."""

    class UserRepository(SQLAlchemyAsyncRepository[m.User]):
        """User SQLAlchemy Repository."""

        model_type = m.User

    repository_type = UserRepository
    match_fields = ["email"]

    async def to_model_on_create(self, data: ModelDictT[m.User]) -> ModelDictT[m.User]:
        return await self._populate_model(data)

    async def to_model_on_update(self, data: ModelDictT[m.User]) -> ModelDictT[m.User]:
        return await self._populate_model(data)

    async def to_model_on_upsert(self, data: ModelDictT[m.User]) -> ModelDictT[m.User]:
        return await self._populate_model(data)

    async def authenticate(self, username: str, password: bytes | str) -> m.User:
        """Authenticate a user against the stored hashed password."""
        db_obj = await self.get_one_or_none(email=username)
        if db_obj is None:
            msg = "User not found or password invalid"
            raise PermissionDeniedException(detail=msg)
        if db_obj.hashed_password is None:
            msg = "User not found or password invalid."
            raise PermissionDeniedException(detail=msg)
        if not await crypt.verify_password(password, db_obj.hashed_password):
            msg = "User not found or password invalid"
            raise PermissionDeniedException(detail=msg)
        return db_obj

    async def update_password(self, data: dict[str, Any], db_obj: m.User) -> None:
        """Modify stored user password."""
        if db_obj.hashed_password is None:
            msg = "User not found or password invalid."
            raise PermissionDeniedException(detail=msg)
        if not await crypt.verify_password(data["current_password"], db_obj.hashed_password):
            msg = "User not found or password invalid."
            raise PermissionDeniedException(detail=msg)
        db_obj.hashed_password = await crypt.get_password_hash(data["new_password"])
        await self.repository.update(db_obj)
