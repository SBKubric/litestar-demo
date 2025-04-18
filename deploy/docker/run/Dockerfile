ARG PYTHON_BUILDER_IMAGE=3.12-slim-bullseye

FROM python:${PYTHON_BUILDER_IMAGE} as python-base
ENV PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random  \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    POETRY_VERSION=1.8.3

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git tini curl build-essential \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache /var/apt/lists/* /var/cache/apt/* \
    && mkdir -p /workspace/app \
    && pip install --quiet --upgrade pip wheel setuptools cython virtualenv \
    && curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

FROM python-base AS build-base
WORKDIR /workspace/app

COPY pyproject.toml poetry.lock README.md .pre-commit-config.yaml LICENSE ./
RUN python -m venv --copies /workspace/app/.venv \
    && . /workspace/app/.venv/bin/activate \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root

COPY tools ./tools/
COPY src ./src/

RUN poetry install --no-interaction

VOLUME /workspace/app

FROM python-base as run-base
ARG ENV_SECRETS="runtime-secrets"
ENV ENV_SECRETS="${ENV_SECRETS}"

RUN addgroup --system --gid 65532 nonroot \
    && adduser --no-create-home --system --uid 65532 nonroot \
    && chown -R nonroot:nonroot /workspace \
    && python -m venv --copies /workspace/app/.venv

WORKDIR /workspace/app
COPY --from=build-base --chown=65532:65532 /workspace/app /workspace/app

FROM python-base as run-image
ARG ENV_SECRETS="runtime-secrets"
ARG CHIPSET_ARCH=x86_64-linux-gnu
ARG LITESTAR_APP="app.asgi:create_app"

ENV PATH="/workspace/app/.venv/bin:/bin:/usr/local/bin:$PATH" \
    ENV_SECRETS="${ENV_SECRETS}" \
    CHIPSET_ARCH="${CHIPSET_ARCH}" \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LITESTAR_APP="${LITESTAR_APP}"

COPY --from=run-base /usr/local/lib/ /usr/local/lib/
COPY --from=run-base /usr/local/bin/python /usr/local/bin/python
COPY --from=run-base /etc/ld.so.cache /etc/ld.so.cache
COPY --from=run-base /usr/bin/tini-static /usr/local/bin/tini
COPY --from=run-base /lib/${CHIPSET_ARCH}/libz.so.1 /lib/${CHIPSET_ARCH}/
COPY --from=run-base /lib/${CHIPSET_ARCH}/libbz2.so.1.0 /lib/${CHIPSET_ARCH}/
COPY --from=run-base /usr/lib/${CHIPSET_ARCH}/libffi* /usr/lib/${CHIPSET_ARCH}/
COPY --from=run-base /lib/${CHIPSET_ARCH}/libexpat* /lib/${CHIPSET_ARCH}/
COPY --from=run-base --chown=65532:65532 /workspace/app /workspace/app

WORKDIR /workspace/app/src
STOPSIGNAL SIGINT
EXPOSE 8000
ENTRYPOINT ["tini","--"]
CMD ["litestar", "run","--host","0.0.0.0","--port","8000"]
VOLUME /workspace/app
