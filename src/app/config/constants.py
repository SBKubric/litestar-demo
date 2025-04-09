from __future__ import annotations

"""The name of the key used for dependency injection of the database
session."""
DB_SESSION_DEPENDENCY_KEY = "db_session"
"""The name of the key used for dependency injection of the database
session."""
USER_DEPENDENCY_KEY = "current_user"
"""The name of the key used for storing DTO information."""
DTO_INFO_KEY = "info"
"""Default page size to use."""
DEFAULT_PAGINATION_SIZE = 20
"""The name of the default role assigned to all users."""
CACHE_EXPIRATION: int = 60
"""The endpoint to use for the the service health check."""
HEALTH_ENDPOINT = "/health"
"""The site index URL."""
SITE_INDEX = "/"
"""The URL path to use for the OpenAPI documentation."""
OPENAPI_SCHEMA = "/schema"
