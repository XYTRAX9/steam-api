from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.steam_service import SteamService
from app import crud, schemas
from app.logger import get_logger
from app.routers.auth import get_current_user
from typing import List

router = APIRouter(prefix="/games", tags=["games"])
logger = get_logger("routers.games")


@router.post("/import/{user_id}", response_model=schemas.ImportGamesResponse)
async def import_games(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Импортирует библиотеку игр пользователя из Steam"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Получаем игры из Steam API
    games = await SteamService.get_owned_games(current_user.steam_id)

    if games is None:
        logger.error(f"Failed to fetch games from Steam for user_id={user_id}")
        raise HTTPException(status_code=500, detail="Failed to fetch games from Steam")

    # Сохраняем игры в базу
    result = crud.create_or_update_games(db, user_id, games)

    logger.info(f"Imported {len(games)} games for user_id={user_id}")
    return result


@router.get("/{user_id}", response_model=List[schemas.Game])
async def get_user_games(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Возвращает список игр пользователя"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    games = crud.get_user_games(db, user_id)
    logger.info(f"Retrieved {len(games)} games for user_id={user_id}")
    return games
