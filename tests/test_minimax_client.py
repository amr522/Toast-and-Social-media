from __future__ import annotations

from typing import Any, Dict

import requests

from src.minimax.client import MiniMaxClient
from src.minimax.config import MiniMaxConfig


class DummyResponse:
    def __init__(self, status_code: int, data: Dict[str, Any]):
        self.status_code = status_code
        self._data = data
        self.text = ""

    def json(self) -> Dict[str, Any]:
        return self._data


def test_headers_and_url_join(monkeypatch):
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

    called = {}

    def fake_request(self: requests.Session, method: str, url: str, json, timeout: int):  # type: ignore[override]
        called["method"] = method
        called["url"] = url
        called["json"] = json
        called["headers"] = dict(self.headers)
        return DummyResponse(200, {"base_resp": {"status_code": 0}, "data": {"ok": True}})

    monkeypatch.setattr(requests.Session, "request", fake_request)

    client = MiniMaxClient(cfg)
    out = client.chat_completions([
        {"role": "user", "content": "hello"}
    ])
    assert called["method"] == "POST"
    assert called["url"] == "https://api.minimax.io/v1/text/chat/completions"
    assert called["json"]["model"] == "MiniMax-M2"
    assert called["headers"]["Authorization"].startswith("Bearer ")
    assert out.get("data", {}).get("ok") is True

