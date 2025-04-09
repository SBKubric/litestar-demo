# Litestar Webapp Demo

Небольшой шаблон на litestar, использующий SQLAlchemy 2.0, SQLAlchemyAdvanced, msgspeck, и Granian.
Основа проекта была взята из [litestar-fullstack](https://github.com/litestar-org/litestar-fullstack),
просто потому что хорошо продумана и удобна для старта нового проекта.

Реализованы следующие возможности:

- [x] Простой CRUD для пользователей
- [x] Авторизация и аутентификация при помощи JWT

## Quick Start

Чтобы запустить проект, выполните следующие команды:

```shell
make install-poetry
make install
. .venv/bin/activate
poetry run app run
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
