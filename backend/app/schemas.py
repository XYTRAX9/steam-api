from pydantic import BaseModel, field_validator
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


class PublicUser(BaseModel):
    id: int
    steam_id: str
    persona_name: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None

    @field_validator("steam_id", mode="before")
    @classmethod
    def stringify_steam_id(cls, value: int | str) -> str:
        return str(value)

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


class ImportGamesResponse(BaseModel):
    games_added: int
    games_updated: int
    games_removed: int


class PlayerStatus(BaseModel):
    user_id: int
    steam_id: str
    persona_name: str
    persona_state: int
    is_in_game: bool
    game_id: Optional[str] = None
    game_name: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
