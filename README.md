# Litestar Webapp Demo

This is a reference application that you can use to get your next Litestar application running quickly.

It contains most of the boilerplate required for a production web API with features like:

-   Latest Litestar configured with best practices
-   Integration with [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [SAQ (Simple Asynchronous Queue)](https://saq-py.readthedocs.io/en/latest/), [Structlog](https://www.structlog.org/en/stable/), and [Granian](<(https://www.structlog.org/en/stable/)](https://github.com/emmett-framework/granian)>)
-   Extends built-in Litestar click CLI
-   Multi-stage Docker build using a Distroless base.

## Quick Start

To quickly get a development environment running, run the following:

```shell
make install
. .venv/bin/activate
```

### Local Development

```bash
cp .env.local.example .env
make start-infra # this starts a database and redis instance only
# this will start the SAQ worker, Vite development process, and Litestar
uv run app run

# to stop the database and redis, run
make stop-infra
```

### Docker

If you want to run the entire development environment containerized, you can run the following:

```bash
docker compose up
```
