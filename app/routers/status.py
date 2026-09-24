from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.steam_service import SteamService
from app import crud, schemas
from app.logger import get_logger

router = APIRouter(prefix="/status", tags=["status"])
logger = get_logger("routers.status")


@router.get("/{user_id}", response_model=schemas.PlayerStatus)
async def get_player_status(user_id: int, db: Session = Depends(get_db)):
    """
    Получает текущий статус пользователя и информацию о текущей игре
    (если он в данный момент играет)
    """
    # Получаем пользователя
    db_user = crud.get_user_by_id(db, user_id)

    if not db_user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем информацию о статусе из Steam
    player_data = await SteamService.get_player_summary(db_user.steam_id)

    if not player_data:
        logger.error(f"Failed to fetch player status for user_id={user_id}")
        raise HTTPException(status_code=500, detail="Failed to fetch player status")

    # Формируем ответ
    status = schemas.PlayerStatus(
        steam_id=db_user.steam_id,
        persona_name=player_data.get("personaname", ""),
        persona_state=player_data.get("personastate", 0),
        is_in_game="gameid" in player_data,
        game_id=player_data.get("gameid"),
        game_name=player_data.get("gameextrainfo"),
        avatar_url=player_data.get("avatarfull")
    )

    logger.info(f"Retrieved player status for user_id={user_id}, is_in_game={status.is_in_game}")
    return status
