from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    steam_id = Column(BigInteger, unique=True, index=True, nullable=False)
    persona_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    profile_url = Column(String, nullable=True)

    games = relationship("Game", back_populates="user", cascade="all, delete-orphan")


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        Index("idx_user_app", "user_id", "app_id", unique=True),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    app_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    playtime_forever = Column(Integer, default=0)
    img_icon_url = Column(String, nullable=True)

    user = relationship("User", back_populates="games")
