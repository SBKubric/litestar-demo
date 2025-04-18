"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from litestar import Controller, Request, Response, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body

from app.domain.accounts import urls
from app.domain.accounts.deps import provide_users_service
from app.domain.accounts.guards import auth
from app.domain.accounts.schemas import AccountLogin, AccountRegister, User

if TYPE_CHECKING:
    from app.db import models as m
    from app.domain.accounts.services import UserService


class AccessController(Controller):
    """User login and registration."""

    tags = ["Access"]
    dependencies = {
        "users_service": Provide(provide_users_service),
    }

    @post(operation_id="AccountLogin", path=urls.ACCOUNT_LOGIN, exclude_from_auth=True)
    async def login(
        self,
        users_service: UserService,
        data: Annotated[AccountLogin, Body(title="JWT Login", media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Response[User]:
        """Authenticate a user."""
        user = await users_service.authenticate(data.username, data.password)
        return auth.login(user.email)

    @post(operation_id="AccountRegister", path=urls.ACCOUNT_REGISTER)
    async def signup(
        self,
        request: Request,
        users_service: UserService,
        data: AccountRegister,
    ) -> User:
        """User Signup."""
        user_data = data.to_dict()
        user = await users_service.create(user_data)
        request.app.emit(event_id="user_created", user_id=user.id)
        return users_service.to_schema(user, schema_type=User)

    @get(operation_id="AccountProfile", path=urls.ACCOUNT_PROFILE)
    async def profile(self, current_user: m.User, users_service: UserService) -> User:
        """User Profile."""
        return users_service.to_schema(current_user, schema_type=User)
