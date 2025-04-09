ARG PYTHON_BUILDER_IMAGE=3.12-slim-bookworm

## ---------------------------------------------------------------------------------- ##
## ------------------------- Python base -------------------------------------------- ##
## ---------------------------------------------------------------------------------- ##
FROM python:${PYTHON_BUILDER_IMAGE} AS python-base
ENV PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_ROOT_USER_ACTION=ignore \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends git tini curl build-essential \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* /root/.cache /var/cache/apt/* \
  && mkdir -p /workspace/app

# Install Poetry
ENV POETRY_VERSION=1.8.3
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Ensure Poetry uses the correct virtualenv location
ENV PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
  POETRY_VIRTUALENVS_PATH="/workspace/app/.venv" \
  POETRY_VIRTUALENVS_IN_PROJECT=true

## ---------------------------------------------------------------------------------- ##
## ------------------------- Python Dev Image --------------------------------------- ##
## ---------------------------------------------------------------------------------- ##
FROM python-base AS dev-image
ARG ENV_SECRETS="runtime-secrets"
ARG LITESTAR_APP="app.asgi:create_app"

ENV ENV_SECRETS="${ENV_SECRETS}"  \
  LITESTAR_APP="${LITESTAR_APP}" \
  PIP_NO_CACHE_DIR=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

# Setup working directory
WORKDIR /workspace/app

# Copy dependency-related files first (to take advantage of caching)
COPY pyproject.toml poetry.lock README.md .pre-commit-config.yaml LICENSE Makefile ./

# Copy scripts, tools, etc.
COPY tools ./tools/

ENV PATH="/opt/nodeenv/bin:$PATH"

# Install Python dependencies
RUN poetry config virtualenvs.create true \
  && poetry install --no-interaction --no-root --all-extras --with dev

# Copy remaining source
COPY docs/ docs/
COPY tests/ tests/
COPY src src/

# Re-run install in case source contains local packages
RUN poetry install --no-interaction --all-extras --with dev

# Entrypoint
STOPSIGNAL SIGINT
EXPOSE 8000
ENTRYPOINT ["tini", "--"]
CMD ["poetry", "run", "litestar", "run", "--host", "0.0.0.0", "--port", "8000"]
VOLUME /workspace/app
