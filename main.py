from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.database import engine, Base
from app.routers import auth, games, status
from app.services.steam_service import SteamService
from app.config import settings
from app.logger import get_logger

logger = get_logger("main")

# Создаем таблицы
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

app = FastAPI(
    title="Steam Integration API",
    description="API для интеграции со Steam: авторизация, импорт игр и мониторинг активности",
    version="1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    session_cookie="steam_session",
    same_site="lax",
    https_only=settings.base_url.startswith("https://"),
    max_age=60 * 60 * 24 * 7,
)

# CORS middleware с ограниченными origins для безопасности
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(status.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Steam Integration API started")
    # Инициализируем HTTP client при старте приложения
    await SteamService.get_client()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Steam Integration API shutting down")
    # Закрываем HTTP client при остановке приложения
    await SteamService.close_client()
    logger.info("Steam Integration API stopped")


@app.get("/")
async def root():
    return {
        "message": "Steam Integration API",
        "endpoints": {
            "auth": "/auth/steam/login",
            "callback": "/auth/steam/callback",
            "import_games": "/games/import/{user_id}",
            "get_games": "/games/{user_id}",
            "player_status": "/status/{user_id}"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
