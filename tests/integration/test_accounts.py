from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_update_user_no_auth(client: "AsyncClient") -> None:
    response = await client.patch("/api/users/112344", json={"name": "TEST UPDATE"})
    assert response.status_code == 401
    response = await client.post(
        "/api/users/",
        json={"name": "A User", "surname": "A User Surname", "email": "new-user@example.com", "password": "S3cret!"},
    )
    assert response.status_code == 401
    response = await client.get("/api/users/112344")
    assert response.status_code == 401
    response = await client.get("/api/users")
    assert response.status_code == 401
    response = await client.delete("/api/users/112344")
    assert response.status_code == 401


async def test_accounts_list(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/users", headers=user_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_accounts_get(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/users/1", headers=user_token_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "superuser@example.com"


async def test_accounts_create(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/users",
        json={"name": "A User", "email": "foobar@example.com", "password": "S3cret!"},
        headers=user_token_headers,
    )
    assert response.status_code == 201


async def test_accounts_update(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.patch(
        "/api/users/1",
        json={
            "name": "Name Changed",
        },
        headers=user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Name Changed"


async def test_accounts_delete(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.delete(
        "/api/users/2",
        headers=user_token_headers,
    )
    assert response.status_code == 204
