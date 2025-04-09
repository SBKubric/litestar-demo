"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.domain.accounts.services import UserService
from app.lib.deps import create_service_provider

if TYPE_CHECKING:
    from litestar import Request

    from app.db import models as m

# create a hard reference to this since it's used often
provide_users_service = create_service_provider(
    UserService,
    error_messages={"duplicate_key": "This user already exists.", "integrity": "User operation failed."},
)


async def provide_user(request: Request[m.User, Any, Any]) -> m.User:
    """Get the user from the request.

    Args:
        request: current Request.

    Returns:
        User
    """
    return request.user
