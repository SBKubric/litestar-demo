# Litestar Webapp Demo

Небольшой шаблон на litestar, использующий SQLAlchemy 2.0, SQLAlchemyAdvanced, msgspeck, и Granian.
Основа проекта была взята из [litestar-fullstack](https://github.com/litestar-org/litestar-fullstack),
просто потому что хорошо продумана и удобна для старта нового проекта.

## Quick Start

Чтобы запустить проект, выполните следующие команды:

```shell
make install
. .venv/bin/activate
```

### Local Development

```bash
cp .env.local.example .env
make start-infra # this starts a database

# to stop the database
make stop-infra
```

### Docker

Если есть желание запустить проект через docker, то можно воспользоваться следующей командой:

```bash
make start-app
```
