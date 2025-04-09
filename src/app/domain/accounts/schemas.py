from __future__ import annotations

import msgspec

from app.lib.schema import CamelizedBaseStruct

__all__ = (
    "AccountLogin",
    "AccountRegister",
    "User",
    "UserCreate",
    "UserUpdate",
)


class User(CamelizedBaseStruct):
    """User properties to use for a response."""

    id: int
    email: str
    name: str | None = None
    surname: str | None = None
    has_password: bool = False


class UserCreate(CamelizedBaseStruct):
    email: str
    password: str
    name: str | None = None
    surname: str | None = None


class UserUpdate(CamelizedBaseStruct, omit_defaults=True):
    email: str | None | msgspec.UnsetType = msgspec.UNSET
    password: str | None | msgspec.UnsetType = msgspec.UNSET
    name: str | None | msgspec.UnsetType = msgspec.UNSET
    surname: str | None | msgspec.UnsetType = msgspec.UNSET


class AccountLogin(CamelizedBaseStruct):
    username: str
    password: str


class AccountRegister(CamelizedBaseStruct):
    email: str
    password: str
    name: str | None = None
    surname: str | None = None
