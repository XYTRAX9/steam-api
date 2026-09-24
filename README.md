# Steam Integration API

Приложение для входа через Steam, импорта своей библиотеки игр и просмотра текущего статуса игрока. Бэкенд написан на FastAPI и SQLAlchemy, интерфейс на Vue 3, TypeScript и Vite.

## Быстрый запуск

Нужны Python 3.12, Node.js 18+ и [ключ Steam Web API](https://steamcommunity.com/dev/apikey). В корне находятся два приложения: `backend/` и `frontend/`.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Заполните `STEAM_API_KEY` и `SECRET_KEY` в `.env`. Для `SECRET_KEY` сгенерируйте случайное значение:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Запустите API из `backend/`:

```bash
python -m uvicorn main:app --reload
```

Интерфейс запустите в другом терминале из `frontend/`:

```bash
cd frontend
npm ci
npm run dev
```

Интерфейс доступен на `http://localhost:3000`, документация API на `http://localhost:8000/docs`. Vite отправляет запросы `/api/*` на бэкенд и убирает префикс `/api`.

## Конфигурация

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `STEAM_API_KEY` | Ключ Steam Web API, обязателен | нет |
| `SECRET_KEY` | Ключ подписи cookie, обязателен | нет |
| `DATABASE_URL` | Адрес базы данных | `sqlite:///./steam.db` |
| `BASE_URL` | Публичный адрес API для Steam OpenID callback | `http://localhost:8000` |
| `FRONTEND_URL` | Адрес интерфейса после входа | `http://localhost:3000` |
| `ALLOWED_ORIGINS` | Разрешённые CORS origins, JSON-массив | localhost:3000 и localhost:8000 |

Проект использует SQLite. Относительный путь в `DATABASE_URL` разрешается относительно `backend/`, поэтому база хранится в `backend/steam.db` независимо от каталога запуска. Таблицы создаются при старте приложения через `create_all`. Миграции Alembic пока не настроены, поэтому изменение существующей схемы требует отдельной миграции.

Для развёртывания по HTTPS задайте HTTPS-адреса в `BASE_URL` и `FRONTEND_URL`: cookie сессии тогда получает флаг `Secure`. Интерфейс должен направлять `/api/*` на бэкенд по тому же принципу, что и Vite в разработке. `BASE_URL` должен быть доступен браузеру при возврате из Steam.

## Как работает вход

1. `GET /auth/steam/login` создаёт состояние входа в подписанной HTTP-only cookie и возвращает URL Steam OpenID.
2. Steam перенаправляет браузер на `GET /auth/steam/callback`. Бэкенд проверяет состояние, поля ответа и подтверждение Steam, затем создаёт или обновляет пользователя.
3. Бэкенд сохраняет ID пользователя в сессии и перенаправляет на `/auth/callback` интерфейса. Интерфейс получает пользователя через `GET /auth/me`.
4. Запросы библиотеки и статуса требуют эту сессию. ID в URL должен совпадать с ID пользователя в cookie. `POST /auth/logout` завершает сессию.

Сессия хранится в подписанной cookie сроком до семи дней. Секрет подписи должен быть одинаковым у всех экземпляров API и не должен попадать в репозиторий.

## API

| Метод и путь | Результат |
| --- | --- |
| `GET /auth/steam/login` | URL для входа через Steam |
| `GET /auth/steam/callback` | Проверка ответа Steam и переход в интерфейс |
| `GET /auth/me` | Текущий пользователь |
| `POST /auth/logout` | Выход |
| `POST /games/import/{user_id}` | Синхронизация библиотеки; числа добавленных, обновлённых и удалённых игр |
| `GET /games/{user_id}` | Сохранённые игры пользователя |
| `GET /status/{user_id}` | Текущий статус из Steam Web API |

SteamID64 возвращается строкой, поскольку JavaScript теряет точность при чтении 17-значного числа. Статус обновляется при открытии страницы и по кнопке «Обновить»; автоматического опроса или WebSocket пока нет.

При успешном импорте пустого списка сохранённая библиотека очищается. Steam может вернуть пустой список и для закрытой библиотеки, поэтому перед использованием синхронизации для таких профилей это поведение нужно уточнить.

## Проверки

Из `backend/`:

```bash
python -m unittest discover -s tests -v
```

Из `frontend/`:

```bash
npm run build
```

Тесты API подменяют ответы Steam и проверяют вход, сессию, запрет доступа к чужому ID, импорт и контракт статуса. Реальный вход требует рабочего Steam API key и доступного callback URL. Логи бэкенда пишутся в `backend/logs/steam_api.log`.

## Что осталось

- Настроить миграции БД для существующих установок SQLite.
- Добавить ограничение частоты запросов; параметры `rate_limit_*` в конфигурации пока не применяются.
- Решить, как отличать закрытую библиотеку Steam от действительно пустой.
- Добавить автоматическое обновление статуса, если нужен именно непрерывный мониторинг.

Основные файлы: `backend/main.py` (FastAPI), `backend/app/routers/` (маршруты), `backend/app/services/steam_service.py` (Steam Web API), `backend/app/crud.py` (база данных), `frontend/src/` (интерфейс). Предыдущие технические заметки находятся в `backend/docs/`.
