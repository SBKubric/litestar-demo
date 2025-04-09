from __future__ import annotations

from typing import Any

import click


@click.group(name="users", invoke_without_command=False, help="Manage application users and roles.")
@click.pass_context
def user_management_group(_: dict[str, Any]) -> None:
    """Manage application users."""


async def load_database_fixtures() -> None:
    """Import/Synchronize Database Fixtures."""

    from pathlib import Path

    from advanced_alchemy.utils.fixtures import open_fixture_async
    from sqlalchemy import select
    from sqlalchemy.orm import load_only
    from structlog import get_logger

    from app.config import get_settings
    from app.config.app import alchemy
    from app.db.models import Role
    from app.domain.accounts.services import RoleService

    settings = get_settings()
    logger = get_logger()
    fixtures_path = Path(settings.db.FIXTURE_PATH)
    async with RoleService.new(
        statement=select(Role).options(load_only(Role.id, Role.slug, Role.name, Role.description)),
        config=alchemy,
    ) as service:
        fixture_data = await open_fixture_async(fixtures_path, "role")
        await service.upsert_many(match_fields=["name"], data=fixture_data, auto_commit=True)
        await logger.ainfo("loaded roles")


@user_management_group.command(name="create-user", help="Create a user")
@click.option(
    "--name",
    help="First name of the new user",
    type=click.STRING,
    required=False,
    show_default=False,
)
@click.option(
    "--surname",
    help="Surname of the new user",
    type=click.STRING,
    required=False,
    show_default=False,
)
@click.option(
    "--password",
    help="Password",
    type=click.STRING,
    required=False,
    show_default=False,
)
def create_user(
    name: str | None,
    surname: str | None,
    password: str | None,
) -> None:
    """Create a user."""
    from typing import cast

    import anyio
    import click
    from rich import get_console

    from app.config.app import alchemy
    from app.domain.accounts.deps import provide_users_service
    from app.domain.accounts.schemas import UserCreate

    console = get_console()

    async def _create_user(
        email: str,
        password: str,
        name: str | None = None,
        superuser: bool = False,
    ) -> None:
        obj_in = UserCreate(
            name=name,
            surname=name,
            password=password,
        )
        async with alchemy.get_session() as db_session:
            users_service = await anext(provide_users_service(db_session))
            user = await users_service.create(data=obj_in.to_dict(), auto_commit=True)
            console.print(f"User created: {user.email}")

    console.rule("Create a new application user.")
    name = name or click.prompt("First Name", show_default=False)
    surname = surname or click.prompt("Surname", show_default=False)
    password = password or click.prompt("Password", hide_input=True, confirmation_prompt=True)

    anyio.run(_create_user, cast("str", password), name, surname)
