from __future__ import annotations

from typing import Any

from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository,
)
from advanced_alchemy.service import (
    ModelDictT,
    SQLAlchemyAsyncRepositoryService,
    is_dict,
    schema_dump,
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

    async def create(self, data: ModelDictT[m.User], **kwargs: Any) -> m.User:
        print("HEELLO")
        data = await self._populate_model(data)
        return await super().create(data, **kwargs)

    async def update(self, data: ModelDictT[m.User], item_id: Any | None = None, **kwargs: Any) -> m.User:
        data = await self._populate_model(data)
        return await super().update(data=data, item_id=item_id, **kwargs)

    async def upsert(self, data: ModelDictT[m.User], item_id: Any | None = None, **kwargs: Any) -> m.User:
        data = await self._populate_model(data)
        return await super().upsert(data=data, item_id=item_id, **kwargs)

    async def authenticate(self, username: str, password: bytes | str) -> m.User:
        """Authenticate a user against the stored hashed password."""
        db_obj = await self.get_one_or_none(email=username)
        print(f"db_obj: {db_obj.email, db_obj.hashed_password}")
        if db_obj is None:
            msg = "User not found or password invalid"
            raise PermissionDeniedException(detail=msg)
        if db_obj.hashed_password is None:
            msg = "User not found or password invalid."
            raise PermissionDeniedException(detail=msg)
        print(f"pswd verify: {crypt.verify_password(password, db_obj.hashed_password)}")
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

    async def _populate_model(self, data: ModelDictT[m.User]) -> ModelDictT[m.User]:
        data = schema_dump(data)
        return await self._populate_with_hashed_password(data)

    async def _populate_with_hashed_password(self, data: ModelDictT[m.User]) -> ModelDictT[m.User]:
        if is_dict(data) and (password := data.pop("password", None)) is not None:
            data["hashed_password"] = await crypt.get_password_hash(password)
            print("PASS WAS HASHED", data)
        return data
