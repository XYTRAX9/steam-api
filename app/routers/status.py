from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.steam_service import SteamService
from app import crud, schemas
from app.logger import get_logger
from app.routers.auth import get_current_user

router = APIRouter(prefix="/status", tags=["status"])
logger = get_logger("routers.status")


@router.get("/{user_id}", response_model=schemas.PlayerStatus)
async def get_player_status(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Получает текущий статус пользователя и информацию о текущей игре
    (если он в данный момент играет)
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Получаем информацию о статусе из Steam
    player_data = await SteamService.get_player_summary(current_user.steam_id)

    if not player_data:
        logger.error(f"Failed to fetch player status for user_id={user_id}")
        raise HTTPException(status_code=500, detail="Failed to fetch player status")

    # Формируем ответ
    status = schemas.PlayerStatus(
        user_id=current_user.id,
        steam_id=str(current_user.steam_id),
        persona_name=player_data.get("personaname", ""),
        persona_state=player_data.get("personastate", 0),
        is_in_game=bool(player_data.get("gameid")),
        game_id=str(player_data["gameid"]) if player_data.get("gameid") else None,
        game_name=player_data.get("gameextrainfo"),
        avatar_url=player_data.get("avatarfull"),
        profile_url=player_data.get("profileurl") or current_user.profile_url,
    )

    logger.info(f"Retrieved player status for user_id={user_id}, is_in_game={status.is_in_game}")
    return status
