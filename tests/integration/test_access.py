import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    ("username", "password", "expected_status_code"),
    (
        ("superuser@example1.com", "Test_Password1!", 403),
        ("superuser@example.com", "Test_Password1!", 201),
        ("user@example.com", "Test_Password1!", 403),
        ("user@example.com", "Test_Password2!", 201),
        ("test@test.com", "Test_Password3!", 201),
    ),
)
async def test_user_login(client: AsyncClient, username: str, password: str, expected_status_code: int) -> None:
    response = await client.post("/api/access/login", data={"username": username, "password": password})
    assert response.status_code == expected_status_code
