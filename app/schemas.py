from pydantic import BaseModel
from typing import Optional, List


class UserBase(BaseModel):
    steam_id: int
    persona_name: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class GameBase(BaseModel):
    app_id: int
    name: str
    playtime_forever: int = 0
    img_icon_url: Optional[str] = None


class Game(GameBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class PlayerStatus(BaseModel):
    steam_id: int
    persona_name: str
    persona_state: int
    is_in_game: bool
    game_id: Optional[int] = None
    game_name: Optional[str] = None
    avatar_url: Optional[str] = None
