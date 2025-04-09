from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.security.jwt import JWTAuth

from app.config import constants
from app.config.app import alchemy
from app.config.base import get_settings
from app.db import models as m
from app.domain.accounts import urls
from app.domain.accounts.deps import provide_users_service

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.security.jwt import Token


__all__ = ("auth", "current_user_from_token")


settings = get_settings()


async def current_user_from_token(token: Token, connection: ASGIConnection[Any, Any, Any, Any]) -> m.User | None:
    """Lookup current user from local JWT token.

    Fetches the user information from the database


    Args:
        token (str): JWT Token Object
        connection (ASGIConnection[Any, Any, Any, Any]): ASGI connection.


    Returns:
        User: User record mapped to the JWT identifier
    """
    service = await anext(provide_users_service(alchemy.provide_session(connection.app.state, connection.scope)))
    return await service.get_one_or_none(email=token.sub)


auth = JWTAuth[m.User](
    retrieve_user_handler=current_user_from_token,
    token_secret=settings.app.SECRET_KEY,
    exclude=[
        constants.HEALTH_ENDPOINT,
        urls.ACCOUNT_LOGIN,
        urls.ACCOUNT_REGISTER,
        "^/schema",
        "^/public/",
    ],
)
