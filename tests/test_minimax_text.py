from __future__ import annotations

from src.minimax.client import MiniMaxClient
from src.minimax.config import MiniMaxConfig
from src.minimax.text import generate_text


class DummyResponse:
    def __init__(self, status_code: int, data):
        self.status_code = status_code
        self._data = data
        self.text = ""

    def json(self):
        return self._data


def test_generate_text_includes_system(monkeypatch):
    called = {}

    def fake_request(self, method, url, json, timeout):  # type: ignore[override]
        called["json"] = json
        return DummyResponse(200, {"base_resp": {"status_code": 0}, "choices": []})

    import requests

    monkeypatch.setattr(requests.Session, "request", fake_request)

    cfg = MiniMaxConfig(
        base_url="https://api.minimax.io",
        api_key="KEY",
        chat_model="MiniMax-M2",
        image_model="image-01",
        tts_model="speech-2.6-hd",
        music_model="music-2.0",
        video_model="MiniMax-Hailuo-2.3",
    )
    client = MiniMaxClient(cfg)

    generate_text(
        client,
        messages=[{"role": "user", "content": "hi"}],
        system="YOU ARE SYSTEM",
    )
    msgs = called["json"]["messages"]
    assert msgs[0]["role"] == "system"
    assert "YOU ARE SYSTEM" in msgs[0]["content"]

