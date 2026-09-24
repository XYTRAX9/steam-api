from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.steam_service import SteamService
from app import crud, schemas
from app.config import settings
from app.logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("routers.auth")


@router.get("/steam/login")
async def steam_login():
    """Инициирует процесс авторизации через Steam OpenID"""
    return_url = f"{settings.base_url}/auth/steam/callback"
    login_url = SteamService.get_login_url(return_url)
    logger.info("Generated Steam login URL")
    return {"login_url": login_url}


@router.get("/steam/callback")
async def steam_callback(request: Request, db: Session = Depends(get_db)):
    """Обрабатывает callback от Steam после авторизации"""
    params = dict(request.query_params)

    # Проверяем валидность ответа
    steam_id = await SteamService.verify_openid(params)

    if not steam_id:
        logger.warning("Invalid Steam OpenID response received")
        raise HTTPException(status_code=400, detail="Invalid Steam OpenID response")

    # Получаем информацию о пользователе
    player_data = await SteamService.get_player_summary(steam_id)

    if not player_data:
        logger.error(f"Failed to fetch player data for steam_id={steam_id}")
        raise HTTPException(status_code=500, detail="Failed to fetch player data")

    # Создаем или обновляем пользователя
    db_user = crud.get_user_by_steam_id(db, steam_id)

    if db_user:
        # Обновляем существующего
        user_data = {
            "persona_name": player_data.get("personaname"),
            "avatar_url": player_data.get("avatarfull"),
            "profile_url": player_data.get("profileurl")
        }
        db_user = crud.update_user(db, db_user.id, user_data)
        logger.info(f"Updated existing user: steam_id={steam_id}, user_id={db_user.id}")
    else:
        # Создаем нового
        user_create = schemas.UserCreate(
            steam_id=steam_id,
            persona_name=player_data.get("personaname"),
            avatar_url=player_data.get("avatarfull"),
            profile_url=player_data.get("profileurl")
        )
        db_user = crud.create_user(db, user_create)
        logger.info(f"Created new user: steam_id={steam_id}, user_id={db_user.id}")

    return {
        "message": "Successfully authenticated",
        "user": {
            "id": db_user.id,
            "steam_id": db_user.steam_id,
            "persona_name": db_user.persona_name,
            "avatar_url": db_user.avatar_url
        }
    }
