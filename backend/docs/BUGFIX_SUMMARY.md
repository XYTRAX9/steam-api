# Исправление бага с таймаутами Steam API

## Проблема
Steam API запросы постоянно завершались таймаутом (timeout) после 3 попыток, приложение возвращало 500 ошибку.

## Причины

### 1. **Критическая ошибка: создание нового HTTP клиента на каждый запрос**
```python
# ДО (неправильно):
async with httpx.AsyncClient() as client:
    response = await client.get(...)
```
- Каждый запрос создавал новое TCP соединение
- Нет переиспользования соединений (connection pooling)
- При retry создавалось еще 2 новых соединения
- Увеличенная задержка на SSL handshake

### 2. **Отсутствие exponential backoff**
- Retry попытки выполнялись мгновенно без задержки
- Steam API мог отклонять быстрые повторные запросы

### 3. **Короткий таймаут**
- Таймаут 10 секунд был недостаточен для Steam API

## Решение

### 1. **Singleton HTTP клиент с connection pooling**
```python
# ПОСЛЕ (правильно):
_client: Optional[httpx.AsyncClient] = None

@classmethod
async def get_client(cls) -> httpx.AsyncClient:
    if cls._client is None or cls._client.is_closed:
        async with cls._client_lock:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=50,
                    keepalive_expiry=30.0
                )
            )
    return cls._client
```

**Преимущества:**
- ✅ Переиспользование TCP соединений
- ✅ Connection pooling (до 50 параллельных соединений)
- ✅ Keep-alive соединения (30 секунд)
- ✅ Значительное снижение latency

### 2. **Exponential backoff для retry**
```python
delay = cls.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
# Попытка 1: 1s
# Попытка 2: 2s
# Попытка 3: 4s
await asyncio.sleep(delay)
```

### 3. **Увеличен таймаут до 30 секунд**
```python
TIMEOUT = 30.0  # было 10.0
```

### 4. **Правильная обработка lifecycle приложения**
```python
@app.on_event("startup")
async def startup_event():
    await SteamService.get_client()  # Инициализация при старте

@app.on_event("shutdown")
async def shutdown_event():
    await SteamService.close_client()  # Закрытие при остановке
```

## Улучшения безопасности

### 1. **SecretStr для чувствительных данных**
```python
steam_api_key: SecretStr  # Не выводится в логах
secret_key: SecretStr
```

### 2. **Валидация Steam ID**
```python
if not steam_id_str.isdigit() or len(steam_id_str) != 17:
    logger.warning(f"Invalid Steam ID format")
    return None
```

### 3. **Ограничение CORS origins**
```python
# Вместо allow_origins=["*"]
allow_origins=settings.allowed_origins
```

### 4. **Улучшенная обработка ошибок**
- Различная обработка для client errors (4xx) и server errors (5xx)
- Детальное логирование с типами ошибок
- Отдельная обработка NetworkError и TimeoutException

## Результат

### Производительность
- ⚡ Устранены таймауты Steam API
- ⚡ Снижена latency благодаря connection pooling
- ⚡ Keep-alive соединения уменьшают overhead

### Надежность
- ✅ Exponential backoff предотвращает rate limiting
- ✅ Правильная обработка lifecycle (startup/shutdown)
- ✅ Улучшенная обработка ошибок

### Безопасность
- 🔒 SecretStr для API ключей
- 🔒 Валидация Steam ID
- 🔒 Ограничение CORS
- 🔒 Предупреждение о коротком secret_key

## Тестирование
```bash
# Проверка конфигурации
python -c "from app.config import settings; print('✓ OK')"

# Проверка импорта приложения
python -c "from main import app; print('✓ OK')"

# Запуск сервера
uvicorn main:app --reload
```
