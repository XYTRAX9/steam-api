import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi.testclient import TestClient

_test_dir = tempfile.TemporaryDirectory()
os.environ["STEAM_API_KEY"] = "test-api-key"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"
os.environ["DATABASE_URL"] = f"sqlite:///{_test_dir.name}/test.db"
os.environ["BASE_URL"] = "http://localhost:8000"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

from app.database import Base, engine  # noqa: E402
from app.services.steam_service import SteamService  # noqa: E402
from main import app  # noqa: E402


class ApiTests(unittest.TestCase):
    steam_id = 76561198000000001

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def login(self):
        login_url = self.client.get("/auth/steam/login").json()["login_url"]
        return_to = parse_qs(urlsplit(login_url).query)["openid.return_to"][0]
        state = parse_qs(urlsplit(return_to).query)["state"][0]
        profile = {
            "personaname": "Test player",
            "avatarfull": "https://example.com/avatar.jpg",
            "profileurl": "https://steamcommunity.com/id/test",
        }
        with patch.object(SteamService, "verify_openid", new_callable=AsyncMock, return_value=self.steam_id) as verify, \
             patch.object(SteamService, "get_player_summary", new_callable=AsyncMock, return_value=profile):
            response = self.client.get(
                "/auth/steam/callback", params={"state": state}, follow_redirects=False
            )
            verify.assert_awaited_once_with({"state": state}, return_to)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "http://localhost:3000/auth/callback")
        self.assertIn("steam_session=", response.headers["set-cookie"])
        self.assertIn("httponly", response.headers["set-cookie"].lower())
        return self.client.get("/auth/me").json()

    def test_login_me_and_logout(self):
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        user = self.login()
        self.assertEqual(user["steam_id"], str(self.steam_id))
        self.assertEqual(user["persona_name"], "Test player")
        self.assertEqual(self.client.post("/auth/logout").status_code, 200)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_callback_rejects_missing_state(self):
        response = self.client.get("/auth/steam/callback", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertIn("error=invalid_response", response.headers["location"])
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_games_are_private_and_empty_import_clears_library(self):
        self.assertEqual(self.client.get("/games/1").status_code, 401)
        self.assertEqual(self.client.post("/games/import/1").status_code, 401)
        user = self.login()
        user_id = user["id"]
        self.assertEqual(self.client.get(f"/games/{user_id + 1}").status_code, 403)
        self.assertEqual(self.client.post(f"/games/import/{user_id + 1}").status_code, 403)

        games = [{"appid": 10, "name": "Test game", "playtime_forever": 120}]
        with patch.object(SteamService, "get_owned_games", new_callable=AsyncMock, side_effect=[games, games, None, []]):
            first = self.client.post(f"/games/import/{user_id}")
            second = self.client.post(f"/games/import/{user_id}")
            failed = self.client.post(f"/games/import/{user_id}")
            self.assertEqual(failed.status_code, 500)
            self.assertEqual(len(self.client.get(f"/games/{user_id}").json()), 1)
            empty = self.client.post(f"/games/import/{user_id}")
        self.assertEqual(first.json(), {"games_added": 1, "games_updated": 0, "games_removed": 0})
        self.assertEqual(second.json(), {"games_added": 0, "games_updated": 1, "games_removed": 0})
        self.assertEqual(empty.json(), {"games_added": 0, "games_updated": 0, "games_removed": 1})
        self.assertEqual(self.client.get(f"/games/{user_id}").json(), [])

    def test_status_matches_frontend_contract(self):
        self.assertEqual(self.client.get("/status/1").status_code, 401)
        user = self.login()
        self.assertEqual(self.client.get(f"/status/{user['id'] + 1}").status_code, 403)
        profile = {
            "personaname": "Test player",
            "personastate": 1,
            "gameid": "570",
            "gameextrainfo": "Dota 2",
            "profileurl": "https://steamcommunity.com/id/test",
        }
        with patch.object(SteamService, "get_player_summary", new_callable=AsyncMock, return_value=profile):
            response = self.client.get(f"/status/{user['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], user["id"])
        self.assertEqual(response.json()["steam_id"], str(self.steam_id))
        self.assertEqual(response.json()["game_id"], "570")
        self.assertEqual(response.json()["profile_url"], profile["profileurl"])

    def test_openid_checks_assertion_fields_before_contacting_steam(self):
        claimed_id = f"https://steamcommunity.com/openid/id/{self.steam_id}"
        expected_return_to = "http://localhost:8000/auth/steam/callback?state=test"
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "id_res",
            "openid.op_endpoint": SteamService.STEAM_OPENID_URL,
            "openid.return_to": expected_return_to,
            "openid.identity": claimed_id,
            "openid.claimed_id": claimed_id,
        }
        with patch.object(SteamService, "get_client", new_callable=AsyncMock) as get_client:
            invalid = asyncio.run(SteamService.verify_openid({**params, "openid.return_to": "https://other.example"}, expected_return_to))
            self.assertIsNone(invalid)
            get_client.assert_not_awaited()

        transport = httpx.MockTransport(lambda request: httpx.Response(200, text="is_valid:true\n"))
        async def check_valid():
            async with httpx.AsyncClient(transport=transport) as client:
                with patch.object(SteamService, "get_client", new_callable=AsyncMock, return_value=client):
                    return await SteamService.verify_openid(params, expected_return_to)
        self.assertEqual(asyncio.run(check_valid()), self.steam_id)


if __name__ == "__main__":
    unittest.main()
