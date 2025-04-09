from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from litestar import Litestar
    from pytest import MonkeyPatch

    from app.db.models import User

pytestmark = pytest.mark.anyio


@pytest.fixture(name="app")
def fx_app(pytestconfig: pytest.Config, monkeypatch: MonkeyPatch) -> Litestar:
    """App fixture.

    Returns:
        An application instance, configured via plugin.
    """
    from app.asgi import create_app

    return create_app()


@pytest.fixture(name="raw_users")
def fx_raw_users() -> list[User | dict[str, Any]]:
    """Unstructured user representations."""

    return [
        {
            "id": 1,
            "email": "superuser@example.com",
            "name": "Super User",
            "surname": "Super User Surname",
            "password": "Test_Password1!",
        },
        {
            "id": 2,
            "email": "user@example.com",
            "name": "Example User",
            "surname": "Example User Surname",
            "password": "Test_Password2!",
        },
        {
            "id": 3,
            "email": "test@test.com",
            "name": "Test User",
            "surname": "Test User Surname",
            "password": "Test_Password3!",
        },
        {
            "id": 4,
            "email": "another@example.com",
            "name": "The User",
            "surname": "The User Surname",
            "password": "Test_Password3!",
        },
    ]
