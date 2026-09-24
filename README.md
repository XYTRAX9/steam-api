# Steam Integration API

Полнофункциональное приложение для интеграции с Steam API с современным Vue 3 фронтендом и FastAPI бэкендом.

## 🏗️ Структура проекта

```
steam-api/
├── app/                      # Backend (FastAPI)
│   ├── __init__.py
│   ├── config.py            # Конфигурация и настройки
│   ├── database.py          # Настройка БД и SQLAlchemy
│   ├── models.py            # ORM модели
│   ├── steam_service.py     # Сервис для работы с Steam API
│   └── routers/             # API роутеры
│       ├── auth.py          # Steam OAuth авторизация
│       ├── games.py         # Управление играми
│       └── status.py        # Статус игрока
├── frontend/                # Frontend (Vue 3 + TypeScript)
│   ├── index.html
│   └── src/
│       ├── main.ts          # Точка входа
│       ├── App.vue          # Корневой компонент
│       ├── assets/          # Стили и ресурсы
│       │   └── main.css
│       ├── api/             # API клиент
│       │   └── index.ts
│       ├── components/      # Vue компоненты
│       │   └── Header.vue
│       ├── views/           # Страницы
│       │   ├── Home.vue
│       │   ├── Games.vue
│       │   ├── Status.vue
│       │   └── Callback.vue
│       ├── stores/          # Pinia хранилища
│       │   ├── theme.ts
│       │   └── user.ts
│       └── router/          # Vue Router
│           └── index.ts
├── main.py                  # Точка входа backend
├── .env                     # Переменные окружения
├── requirements.txt         # Python зависимости
├── package.json            # Node.js зависимости
├── vite.config.ts          # Конфигурация Vite
├── tsconfig.json           # TypeScript конфигурация
└── README.md

```

## 🚀 Возможности

### Backend
- ✅ Steam OAuth авторизация
- ✅ Импорт игр из Steam библиотеки
- ✅ Отслеживание статуса игрока в реальном времени
- ✅ Устойчивая обработка ошибок с retry механизмом
- ✅ Connection pooling для оптимизации производительности
- ✅ Rate limiting для защиты от DDoS
- ✅ CORS настройки для безопасности
- ✅ Автоматическая документация API (Swagger/OpenAPI)

### Frontend
- ✅ Современный UI с glassmorphism эффектами
- ✅ Тёмная/светлая тема
- ✅ Полностью типизированный TypeScript
- ✅ Reactive state management (Pinia)
- ✅ Responsive дизайн
- ✅ Оптимизированная загрузка и кэширование
- ✅ Real-time обновление статуса

## 📦 Установка

### Backend

1. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте `.env` файл:
```env
STEAM_API_KEY=your_steam_api_key_here
DATABASE_URL=sqlite:///./steam.db
SECRET_KEY=your_secret_key_here_min_32_chars
BASE_URL=http://localhost:8000
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Frontend

1. Установите Node.js зависимости:
```bash
npm install
```

## 🎯 Запуск

### Режим разработки

1. **Запустите Backend** (порт 8000):
```bash
python main.py
```

2. **Запустите Frontend** (порт 3000):
```bash
npm run dev
```

3. Откройте браузер:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Production

1. **Build Frontend:**
```bash
npm run build
```

2. **Запуск с Gunicorn/Uvicorn:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔑 Получение Steam API ключа

1. Перейдите на https://steamcommunity.com/dev/apikey
2. Войдите через Steam аккаунт
3. Заполните форму регистрации
4. Скопируйте API ключ в `.env` файл

## 🛠️ Технологии

### Backend
- **FastAPI** - современный, быстрый веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **httpx** - асинхронный HTTP клиент
- **Pydantic** - валидация данных
- **python-dotenv** - управление переменными окружения

### Frontend
- **Vue 3** - прогрессивный JavaScript фреймворк
- **TypeScript** - типизированный JavaScript
- **Vite** - быстрый сборщик модулей
- **Pinia** - state management
- **Vue Router** - маршрутизация
- **Axios** - HTTP клиент

## 📚 API Endpoints

### Авторизация
- `GET /auth/steam/login` - Получить URL для входа через Steam
- `GET /auth/steam/callback` - Callback для Steam OAuth

### Игры
- `POST /games/import/{user_id}` - Импортировать игры из Steam
- `GET /games/{user_id}` - Получить список игр пользователя

### Статус
- `GET /status/{user_id}` - Получить текущий статус игрока

## 🎨 Дизайн

Приложение использует современный дизайн-подход:
- **Glassmorphism** эффекты для карточек
- **Тёмная/светлая** тема с плавными переходами
- **Inter** шрифт для интерфейса
- **JetBrains Mono** для технических данных
- Адаптивная верстка для всех устройств

## 🔒 Безопасность

- ✅ CORS политика для разрешенных доменов
- ✅ Rate limiting на уровне приложения
- ✅ Валидация всех входных данных
- ✅ Безопасное хранение секретов в `.env`
- ✅ Экспоненциальный backoff для retry логики
- ✅ Timeout настройки для всех запросов

## 📈 Оптимизация производительности

- Connection pooling для HTTP клиента
- Переиспользование соединений
- Асинхронные операции
- Кэширование на стороне клиента
- Lazy loading компонентов

## 🐛 Отладка

### Backend логи
```bash
tail -f logs/app.log  # если настроен file handler
```

### Frontend dev tools
Используйте Vue DevTools браузерное расширение

## 📝 Лицензия

MIT

## 👨‍💻 Разработка

При добавлении новых функций:
1. Создавайте отдельные ветки для функций
2. Следуйте существующей структуре кода
3. Добавляйте типы для TypeScript
4. Тестируйте на обеих темах (светлая/тёмная)
5. Проверяйте адаптивность на мобильных устройствах
# steam-api
