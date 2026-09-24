import secrets
from urllib.parse import urlencode

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
async def steam_login(request: Request):
    """Инициирует процесс авторизации через Steam OpenID"""
    state = secrets.token_urlsafe(32)
    request.session["steam_login_state"] = state
    return_url = f"{settings.base_url}/auth/steam/callback?{urlencode({'state': state})}"
    login_url = SteamService.get_login_url(return_url)
    logger.info("Generated Steam login URL")
    return {"login_url": login_url}


@router.get("/steam/callback")
async def steam_callback(request: Request, db: Session = Depends(get_db)):
    """Обрабатывает callback от Steam после авторизации"""
    params = dict(request.query_params)
    state = request.session.pop("steam_login_state", None)
    expected_return_to = (
        f"{settings.base_url}/auth/steam/callback?{urlencode({'state': state})}"
        if state else None
    )

    steam_id = None
    if state and params.get("state") == state:
        steam_id = await SteamService.verify_openid(params, expected_return_to)

    if not steam_id:
        logger.warning("Invalid Steam OpenID response received")
        return RedirectResponse(f"{settings.frontend_url}/auth/callback?error=invalid_response", status_code=303)

    # Получаем информацию о пользователе
    player_data = await SteamService.get_player_summary(steam_id)

    if not player_data:
        logger.error(f"Failed to fetch player data for steam_id={steam_id}")
        return RedirectResponse(f"{settings.frontend_url}/auth/callback?error=steam_unavailable", status_code=303)

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

    request.session["user_id"] = db_user.id
    return RedirectResponse(f"{settings.frontend_url}/auth/callback", status_code=303)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Session user not found")
    return user


@router.get("/me", response_model=schemas.PublicUser)
def get_me(user=Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}
