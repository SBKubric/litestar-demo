# pylint: disable=[invalid-name,import-outside-toplevel]
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from litestar.config.response_cache import default_cache_key_builder
from litestar.di import Provide
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol

if TYPE_CHECKING:
    from click import Group
    from litestar import Request
    from litestar.config.app import AppConfig


T = TypeVar("T")


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    """Application core configuration plugin.

    This class is responsible for configuring the main Litestar application with our routes, guards, and various plugins

    """

    __slots__ = ("app_slug",)
    app_slug: str

    def on_cli_init(self, cli: Group) -> None:
        from app.cli.commands import user_management_group
        from app.config import get_settings

        settings = get_settings()
        self.app_slug = settings.app.slug
        cli.add_command(user_management_group)

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure application for use with SQLAlchemy.

        Args:
            app_config: The :class:`AppConfig <litestar.config.app.AppConfig>` instance.
        """

        from uuid import UUID

        from advanced_alchemy.exceptions import RepositoryError
        from litestar.enums import RequestEncodingType
        from litestar.params import Body
        from litestar.security.jwt import Token

        from app.__about__ import __version__ as current_version
        from app.config import app as config
        from app.config import get_settings
        from app.db import models as m
        from app.domain.accounts.controllers import UserController
        from app.domain.accounts.deps import provide_user
        from app.domain.accounts.guards import auth as jwt_auth
        from app.domain.accounts.services import UserService
        from app.domain.system.controllers import SystemController
        from app.lib.exceptions import ApplicationError, exception_to_http_response
        from app.server import plugins

        settings = get_settings()
        self.app_slug = settings.app.slug
        app_config.debug = settings.app.DEBUG
        # openapi
        app_config.openapi_config = OpenAPIConfig(
            title=settings.app.NAME,
            version=current_version,
            components=[jwt_auth.openapi_components],
            security=[jwt_auth.security_requirement],
            use_handler_docstrings=True,
            render_plugins=[ScalarRenderPlugin(version="latest")],
        )
        # jwt auth (updates openapi config)
        app_config = jwt_auth.on_app_init(app_config)
        # security
        app_config.cors_config = config.cors
        # plugins
        app_config.plugins.extend(
            [
                plugins.structlog,
                plugins.granian,
                plugins.alchemy,
                plugins.problem_details,
            ],
        )

        # routes
        app_config.route_handlers.extend(
            [
                UserController,
                SystemController,
            ],
        )
        # signatures
        app_config.signature_namespace.update(
            {
                "Token": Token,
                "RequestEncodingType": RequestEncodingType,
                "Body": Body,
                "m": m,
                "UUID": UUID,
                "UserService": UserService,
            },
        )
        # exception handling
        app_config.exception_handlers = {
            ApplicationError: exception_to_http_response,
            RepositoryError: exception_to_http_response,
        }
        # dependencies
        dependencies = {"current_user": Provide(provide_user)}
        app_config.dependencies.update(dependencies)
        return app_config

    def _cache_key_builder(self, request: Request) -> str:
        """App name prefixed cache key builder.

        Args:
            request (Request): Current request instance.

        Returns:
            str: App slug prefixed cache key.
        """

        return f"{self.app_slug}:{default_cache_key_builder(request)}"
