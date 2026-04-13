# RGOV

RGOV — Ratcraftia Government Web Portal. Проект собран как монорепозиторий:

- `frontend` — Flutter Web интерфейс на русском языке
- `backend` — FastAPI + Uvicorn backend с JWT, GovMail, законами, референдумами, парламентом, новостями и DID
- `RCS` — Ratcraftia Control Script для административных и законодательных операций

## Возможности

- JWT-авторизация:
  - единая форма: `логин или УИН` + `пароль или УАН`
- Профиль доступа:
  - смена логина
  - смена пароля
- Внешняя авторизация для сторонних сервисов:
  - запрос приложения через API
  - OAuth 2.0 authorization code flow с browser redirect и consent
  - выпуск OAuth-токенов только после одобрения приложения администратором
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

## Быстрый старт

### Через Docker Compose

```bash
docker compose up --build
```

После запуска:

- портал: `http://localhost:8800`
- backend API: `http://localhost:8800/api`
- Swagger: `http://localhost:8800/docs`

### Локально

Backend:

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

Миграции схемы БД применяются автоматически при старте backend и через `RCS`.

Frontend:

```bash
cd frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api
```

## Стартовая учётная запись

- `root` / `RGOV-DEFAULT_ROOT`
- у `root` всегда назначается permission `*`

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

- База данных по умолчанию — SQLite.
- Старые поля ролей автоматически мигрируются в `permissions` при запуске backend.
- УАН в списках пользователей маскируется, но остаётся доступен владельцу в профиле и DID.
- Смена логина ограничена одним разом в сутки по часовому поясу `Europe/Moscow`.
- Внешняя авторизация:
  - `POST /api/oauth/apps/request` — регистрация внешнего приложения с `redirect_uri`
  - `GET /api/oauth/apps/{client_id}/status` — проверка статуса одобрения
  - `GET /api/oauth/authorize` — browser redirect/consent страница
  - `POST /api/oauth/token` — обмен authorization code на access token
  - `GET /api/oauth/me` — минимальный профиль по внешнему токену
  - в web UI есть публичная форма для создания `client_id` и `client_secret`
  - одобрение и отключение выполняются через раздел управления или admin API
