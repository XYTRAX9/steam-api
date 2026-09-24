import httpx
import asyncio
import re
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from app.config import settings
from app.logger import get_logger

logger = get_logger("steam_service")


class SteamService:
    STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
    STEAM_API_BASE = "https://api.steampowered.com"
    TIMEOUT = 30.0  # Увеличен таймаут
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 1.0  # Базовая задержка для exponential backoff

    # Singleton httpx client для переиспользования соединений
    _client: Optional[httpx.AsyncClient] = None
    _client_lock = asyncio.Lock()

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """Получает или создает singleton AsyncClient с connection pooling"""
        if cls._client is None or cls._client.is_closed:
            async with cls._client_lock:
                if cls._client is None or cls._client.is_closed:
                    cls._client = httpx.AsyncClient(
                        timeout=httpx.Timeout(cls.TIMEOUT),
                        limits=httpx.Limits(
                            max_keepalive_connections=20,
                            max_connections=50,
                            keepalive_expiry=30.0
                        ),
                        follow_redirects=True
                    )
                    logger.info("Created new httpx.AsyncClient with connection pooling")
        return cls._client

    @classmethod
    async def close_client(cls):
        """Закрывает HTTP клиент (вызывается при shutdown приложения)"""
        if cls._client is not None and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None
            logger.info("Closed httpx.AsyncClient")

    @staticmethod
    def get_login_url(return_url: str) -> str:
        """Генерирует URL для авторизации через Steam OpenID"""
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": return_url,
            "openid.realm": settings.base_url,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        return f"{SteamService.STEAM_OPENID_URL}?{urlencode(params)}"

    @classmethod
    async def verify_openid(cls, params: Dict[str, Any], expected_return_to: str) -> Optional[int]:
        """
        Проверяет подлинность ответа Steam OpenID.
        Возвращает SteamID64 при успешной проверке или None при ошибке.
        """
        claimed_id = params.get("openid.claimed_id", "")
        if (
            params.get("openid.ns") != "http://specs.openid.net/auth/2.0"
            or params.get("openid.mode") != "id_res"
            or params.get("openid.op_endpoint") != cls.STEAM_OPENID_URL
            or params.get("openid.return_to") != expected_return_to
            or params.get("openid.identity") != claimed_id
            or not re.fullmatch(r"https?://steamcommunity\.com/openid/id/\d{17}", claimed_id)
        ):
            logger.warning("Invalid Steam OpenID assertion fields")
            return None

        # Изменяем mode на check_authentication для валидации
        verify_params = dict(params)
        verify_params["openid.mode"] = "check_authentication"

        client = await cls.get_client()

        try:
            response = await client.post(
                cls.STEAM_OPENID_URL,
                data=verify_params,
                timeout=cls.TIMEOUT
            )

            if response.status_code != 200:
                logger.warning(f"OpenID verification failed with status {response.status_code}")
                return None

            # Проверяем, что Steam подтвердил валидность
            if not any(line.strip() == "is_valid:true" for line in response.text.splitlines()):
                logger.warning("OpenID verification returned is_valid:false")
                return None

            # Извлекаем SteamID64 из claimed_id
            # SteamID находится в конце URL - валидация формата
            steam_id_str = claimed_id.split("/")[-1]

            # Проверка что это действительно числовой Steam ID
            if not steam_id_str.isdigit() or len(steam_id_str) != 17:
                logger.warning(f"Invalid Steam ID format: {steam_id_str}")
                return None

            steam_id = int(steam_id_str)
            logger.info(f"Successfully verified Steam ID: {steam_id}")
            return steam_id

        except httpx.TimeoutException:
            logger.error("OpenID verification timeout")
            return None
        except ValueError as e:
            logger.error(f"Invalid Steam ID value: {e}")
            return None
        except Exception as e:
            logger.error(f"OpenID verification error: {e}", exc_info=True)
            return None

    @classmethod
    async def _make_steam_api_request(cls, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Выполняет запрос к Steam API с повторными попытками и exponential backoff"""
        client = await cls.get_client()

        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Steam API request successful (attempt {attempt}/{cls.MAX_RETRIES})")
                    return data

                # Логируем ошибки HTTP
                logger.warning(
                    f"Steam API request failed with status {response.status_code} "
                    f"(attempt {attempt}/{cls.MAX_RETRIES})"
                )

                # Retry только для server errors (5xx)
                if response.status_code >= 500 and attempt < cls.MAX_RETRIES:
                    delay = cls.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue

                # Для client errors (4xx) не делаем retry
                if 400 <= response.status_code < 500:
                    logger.error(f"Client error {response.status_code}: {response.text[:200]}")
                    return None

            except httpx.TimeoutException:
                logger.warning(
                    f"Steam API request timeout (attempt {attempt}/{cls.MAX_RETRIES})"
                )
                if attempt < cls.MAX_RETRIES:
                    delay = cls.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                return None

            except httpx.NetworkError as e:
                logger.error(
                    f"Steam API network error: {e} (attempt {attempt}/{cls.MAX_RETRIES})"
                )
                if attempt < cls.MAX_RETRIES:
                    delay = cls.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                return None

            except Exception as e:
                logger.error(
                    f"Steam API request error: {e} (attempt {attempt}/{cls.MAX_RETRIES})",
                    exc_info=True
                )
                if attempt < cls.MAX_RETRIES:
                    delay = cls.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
                    continue
                return None

        return None

    @classmethod
    async def get_owned_games(cls, steam_id: int) -> Optional[list]:
        """Получает список игр пользователя из Steam API"""
        url = f"{cls.STEAM_API_BASE}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": settings.steam_api_key.get_secret_value(),
            "steamid": steam_id,
            "include_appinfo": True,
            "include_played_free_games": True,
            "format": "json"
        }

        logger.info(f"Fetching owned games for Steam ID: {steam_id}")
        data = await cls._make_steam_api_request(url, params)

        if data:
            games = data.get("response", {}).get("games", [])
            logger.info(f"Retrieved {len(games)} games for Steam ID: {steam_id}")
            return games

        logger.error(f"Failed to fetch owned games for Steam ID: {steam_id}")
        return None

    @classmethod
    async def get_player_summary(cls, steam_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о профиле и текущей активности игрока"""
        url = f"{cls.STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            "key": settings.steam_api_key.get_secret_value(),
            "steamids": steam_id,
            "format": "json"
        }

        logger.info(f"Fetching player summary for Steam ID: {steam_id}")
        data = await cls._make_steam_api_request(url, params)

        if data:
            players = data.get("response", {}).get("players", [])

            if not players:
                logger.warning(f"No player data found for Steam ID: {steam_id}")
                return None

            logger.info(f"Retrieved player summary for Steam ID: {steam_id}")
            return players[0]

        logger.error(f"Failed to fetch player summary for Steam ID: {steam_id}")
        return None
