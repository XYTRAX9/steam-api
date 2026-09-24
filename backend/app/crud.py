from sqlalchemy.orm import Session
from app import models, schemas
from app.logger import get_logger
from typing import Optional, List

logger = get_logger("crud")


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Получает пользователя по ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_steam_id(db: Session, steam_id: int) -> Optional[models.User]:
    """Получает пользователя по Steam ID"""
    return db.query(models.User).filter(models.User.steam_id == steam_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Создает нового пользователя"""
    db_user = models.User(
        steam_id=user.steam_id,
        persona_name=user.persona_name,
        avatar_url=user.avatar_url,
        profile_url=user.profile_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Created user: steam_id={user.steam_id}, id={db_user.id}")
    return db_user


def update_user(db: Session, user_id: int, user_data: dict) -> Optional[models.User]:
    """Обновляет данные пользователя"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Updated user: id={user_id}")
    else:
        logger.warning(f"User not found for update: id={user_id}")
    return db_user


def create_or_update_games(db: Session, user_id: int, games: List[dict]) -> dict:
    """
    Создает или обновляет игры пользователя.
    Удаляет игры, которых больше нет в списке Steam.
    """
    # Получаем существующие игры пользователя
    existing_games = db.query(models.Game).filter(models.Game.user_id == user_id).all()
    existing_games_dict = {game.app_id: game for game in existing_games}

    # Новые app_id из Steam
    new_app_ids = {game.get("appid") for game in games}

    # Удаляем игры, которых больше нет
    games_to_remove = set(existing_games_dict.keys()) - new_app_ids
    if games_to_remove:
        db.query(models.Game).filter(
            models.Game.user_id == user_id,
            models.Game.app_id.in_(games_to_remove)
        ).delete(synchronize_session=False)
        logger.info(f"Removed {len(games_to_remove)} games for user_id={user_id}")

    # Обновляем существующие и добавляем новые игры
    games_added = 0
    games_updated = 0

    for game in games:
        app_id = game.get("appid")

        if app_id in existing_games_dict:
            # Обновляем существующую игру
            existing_game = existing_games_dict[app_id]
            existing_game.name = game.get("name", "Unknown")
            existing_game.playtime_forever = game.get("playtime_forever", 0)
            existing_game.img_icon_url = game.get("img_icon_url")
            games_updated += 1
        else:
            # Добавляем новую игру
            db_game = models.Game(
                user_id=user_id,
                app_id=app_id,
                name=game.get("name", "Unknown"),
                playtime_forever=game.get("playtime_forever", 0),
                img_icon_url=game.get("img_icon_url")
            )
            db.add(db_game)
            games_added += 1

    db.commit()
    logger.info(f"Updated {games_updated} and added {games_added} games for user_id={user_id}")
    return {
        "games_added": games_added,
        "games_updated": games_updated,
        "games_removed": len(games_to_remove),
    }


def get_user_games(db: Session, user_id: int) -> List[models.Game]:
    """Получает список игр пользователя"""
    return db.query(models.Game).filter(models.Game.user_id == user_id).all()
