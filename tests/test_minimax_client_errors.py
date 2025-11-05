from __future__ import annotations

import requests

from src.minimax.client import MiniMaxClient, MiniMaxError
from src.minimax.config import MiniMaxConfig


class DummyResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data
        self.text = ""

    def json(self):
        return self._data


def test_api_error_raises_minimax_error(monkeypatch):
    cfg = MiniMaxConfig(
        base_url="https://api.minimax.io",
        api_key="KEY",
        chat_model="MiniMax-M2",
        image_model="image-01",
        tts_model="speech-2.6-hd",
        music_model="music-2.0",
        video_model="MiniMax-Hailuo-2.3",
        rate_limit_rpm=1000,
        max_retries=1,
        timeout_sec=5,
    )

    def fake_request(self: requests.Session, method: str, url: str, json, timeout):  # type: ignore[override]
        return DummyResponse(200, {"base_resp": {"status_code": 123, "status_msg": "quota exceeded"}})

    monkeypatch.setattr(requests.Session, "request", fake_request)

    client = MiniMaxClient(cfg)
    try:
        client.chat_completions([{"role": "user", "content": "hi"}])
    except MiniMaxError as e:
        assert e.status_code == 123
        assert "quota exceeded" in str(e)
    else:
        assert False, "Expected MiniMaxError"

