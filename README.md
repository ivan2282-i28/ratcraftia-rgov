# RGOV

RGOV — Ratcraftia Government Web Portal. Проект собран как монорепозиторий:

- `frontend` — React + Material UI интерфейс на русском языке
- `backend` — FastAPI + Uvicorn backend с JWT, GovMail, законами, референдумами, парламентом, новостями и DID
- `RCS` — Ratcraftia Control Script для административных и законодательных операций

## Возможности

- JWT-авторизация:
  - единая форма: `логин или УИН` + `пароль или УАН`
- Профиль доступа:
  - смена логина
  - смена пароля
- GovMail:
  - `UIN@citizen`
  - `Initials.Organization@gov`
  - `login@fn`
- DID-карта:
  - фото слева
  - QR справа
  - JWT-токен на 10 минут
  - поля `ФИО`, `УИН`, `УАН`
- Иерархия власти:
  - Конституция
  - Референдум
  - Парламент
  - Исполнительная власть
- Народное волеизъявление:
  - выдвижение кандидатов в парламент через RGOV
  - сбор подписей за кандидатов и инициативы референдума
  - автоматический расчёт кворума и 4-дневного окна голосования
  - довыборы при появлении вакантных мест парламента
  - отзывы депутата и должностного лица через референдум
- Законодательный поток:
  - парламент может создавать и изменять законы
  - конституция меняется только через референдум
  - референдум может публиковать законы и поправки
- Исполнительный контур:
  - публикация и удаление новостей
  - создание организаций
  - организациям можно хранить собственный баланс Ratubles
  - приём на работу и увольнение
  - управление правами доступа через permissions
  - tree-интерфейс Ratcraftia для законов, пользователей, организаций, OAuth apps и журнала
  - `Overwrite mode` для прямой перезаписи законов и административных сущностей
- Внешние разработчики:
  - frontend-раздел "Разработчикам" для регистрации OAuth-приложений
  - отдельная публичная документация OpenAPI: `/api/public/docs`
  - OAuth authorization-code flow для входа через RGOV
  - каждое приложение должно быть одобрено администратором перед использованием

## Быстрый старт

### Через Docker Compose

```bash
docker compose up --build
```

После запуска:

- портал: `http://localhost:8800`
- backend API: `http://localhost:8800/api`
- Swagger: `http://localhost:8800/docs`
- Public OAuth docs: `http://localhost:8800/api/public/docs`

### Локально

Backend:

```bash
docker compose up postgres -d
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

Миграции схемы БД применяются автоматически при старте backend и через `RCS`.
По умолчанию backend ожидает PostgreSQL на `postgresql+psycopg://rgov:rgov@localhost:5432/rgov`.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Стартовая учётная запись

- `root` / `RGOV-DEFAULT_ROOT`
- у `root` всегда назначаются permissions `root` и `*`
- permission `root` открывает `Overwrite mode`, который позволяет напрямую менять законы, Конституцию, пользователей и другие сущности в обход обычных политик RGOV

Примеры адресов GovMail:

- `1.26.563372@citizen`
- `NAA.parlament@gov`
- `navaliniy@fn`

## RCS

Скрипт запускается из корня проекта:

```bash
./RCS list-users
./RCS create-bill --actor-uin 1.26.563372 --title "Закон" --text "Новый текст"
./RCS create-referendum --actor-uin 1.26.563372 --title "Поправка" --text "Статья..." --target-level constitution
./RCS send-mail --actor-uin 0.00.000001 --to navaliniy@fn --subject "Тест" --text "Привет"
```

Основные команды:

- `seed-demo`
- `list-users`
- `create-user`
- `create-org`
- `post-news`
- `delete-news`
- `change-permissions`
- `hire`
- `fire`
- `create-bill`
- `vote-bill`
- `publish-bill`
- `create-referendum`
- `vote-referendum`
- `publish-referendum`
- `send-mail`

## Замечания

- База данных по умолчанию — PostgreSQL.
- SQLite остаётся удобным режимом для локальных тестов и временных фикстур.
- Старые поля ролей автоматически мигрируются в `permissions` при запуске backend.
- УАН в списках пользователей маскируется, но остаётся доступен владельцу в профиле и DID.
- Смена логина ограничена одним разом в сутки по часовому поясу `Europe/Moscow`.
- Публичный OAuth flow начинается с `/api/public/oauth/authorize`, а обмен кода на токен выполняется через `/api/public/oauth/token`.
