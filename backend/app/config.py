from pydantic_settings import BaseSettings
from pydantic import field_validator, SecretStr
import secrets
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    steam_api_key: SecretStr  # Защищенное хранение API ключа
    database_url: str = "sqlite:///./steam.db"
    secret_key: SecretStr  # Защищенное хранение secret key
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    # Дополнительные параметры безопасности
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # запросов на интервал
    rate_limit_window: int = 60  # секунд

    @field_validator("steam_api_key", "secret_key")
    @classmethod
    def validate_not_empty(cls, v: SecretStr, info) -> SecretStr:
        secret_value = v.get_secret_value() if isinstance(v, SecretStr) else v
        if not secret_value or not secret_value.strip():
            raise ValueError(f"{info.field_name} cannot be empty")

        # Предупреждение о коротком secret_key, но не блокируем запуск
        if info.field_name == "secret_key" and len(secret_value) < 32:
            import logging
            logging.warning(
                f"secret_key is only {len(secret_value)} characters. "
                "For production use at least 32 characters. "
                f"Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        return v

    @field_validator("base_url", "frontend_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, v: list[str]) -> list[str]:
        """Валидация CORS origins"""
        validated = []
        for origin in v:
            origin = origin.strip()
            if origin == "*":
                # Разрешаем * только для development
                validated.append(origin)
            elif origin.startswith(("http://", "https://")):
                validated.append(origin.rstrip("/"))
            else:
                raise ValueError(f"Invalid origin format: {origin}")
        return validated

    @classmethod
    def generate_secret_key(cls) -> str:
        """Генерирует криптографически безопасный secret key"""
        return secrets.token_urlsafe(32)

    class Config:
        env_file = BACKEND_DIR / ".env"


settings = Settings()
