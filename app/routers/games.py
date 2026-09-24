from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.steam_service import SteamService
from app import crud, schemas
from app.logger import get_logger
from typing import List

router = APIRouter(prefix="/games", tags=["games"])
logger = get_logger("routers.games")


@router.post("/import/{user_id}")
async def import_games(user_id: int, db: Session = Depends(get_db)):
    """Импортирует библиотеку игр пользователя из Steam"""
    # Получаем пользователя
    db_user = crud.get_user_by_id(db, user_id)

    if not db_user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем игры из Steam API
    games = await SteamService.get_owned_games(db_user.steam_id)

    if games is None:
        logger.error(f"Failed to fetch games from Steam for user_id={user_id}")
        raise HTTPException(status_code=500, detail="Failed to fetch games from Steam")

    # Сохраняем игры в базу
    crud.create_or_update_games(db, user_id, games)

    logger.info(f"Imported {len(games)} games for user_id={user_id}")
    return {
        "message": f"Successfully imported {len(games)} games",
        "count": len(games)
    }


@router.get("/{user_id}", response_model=List[schemas.Game])
async def get_user_games(user_id: int, db: Session = Depends(get_db)):
    """Возвращает список игр пользователя"""
    db_user = crud.get_user_by_id(db, user_id)

    if not db_user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    games = crud.get_user_games(db, user_id)
    logger.info(f"Retrieved {len(games)} games for user_id={user_id}")
    return games
