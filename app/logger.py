import logging
import sys
from pathlib import Path

# Создаем директорию для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настраиваем форматирование
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Создаем форматтер
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

# Настраиваем handler для файла
file_handler = logging.FileHandler(LOG_DIR / "steam_api.log", encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Настраиваем handler для консоли
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Создаем основной логгер
logger = logging.getLogger("steam_api")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Предотвращаем дублирование логов
logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Получает логгер для конкретного модуля"""
    return logging.getLogger(f"steam_api.{name}")
