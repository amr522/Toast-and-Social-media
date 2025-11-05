from __future__ import annotations

import base64
from pathlib import Path
import json

from src.minimax.audio import compose_music_for_slug, synthesize_voice_for_slug
from src.minimax.client import MiniMaxClient
from src.minimax.config import MiniMaxConfig


def _mk_client() -> MiniMaxClient:
    return MiniMaxClient(
        MiniMaxConfig(
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
    )


def test_tts_and_music_save_files(tmp_path, monkeypatch):
    # Create stub content JSON for narration
    content_dir = tmp_path / "build" / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "test-dish.json").write_text(
        json.dumps({"narration_script": "Welcome to 41 Bistro"}), encoding="utf-8"
    )

    # Monkeypatch BUILD_DIR to tmp_path/build via environment by patching module constant
    import src.minimax.audio as audio_module
    old_build = audio_module.BUILD_DIR
    audio_module.BUILD_DIR = tmp_path / "build"
    audio_module.AUDIO_DIR = audio_module.BUILD_DIR / "audio"
    try:
        # Monkeypatch client methods to return base64 audio
        b64 = base64.b64encode(b"FAKEAUDIO").decode("ascii")

        client = _mk_client()

        def fake_tts(prompt):  # type: ignore[no-untyped-def]
            return {"audio": b64, "base_resp": {"status_code": 0}}

        def fake_music(prompt):  # type: ignore[no-untyped-def]
            return {"audio": b64, "base_resp": {"status_code": 0}}

        client.text_to_speech = fake_tts  # type: ignore[assignment]
        client.music_generation = fake_music  # type: ignore[assignment]

        meta_tts = synthesize_voice_for_slug("test-dish", client=client)
        meta_music = compose_music_for_slug("test-dish", client=client)

        tts_file = Path(tmp_path, "build", "audio", "test-dish_voice.mp3")
        music_file = Path(tmp_path, "build", "audio", "test-dish_music.mp3")
        assert tts_file.exists() and tts_file.read_bytes() == b"FAKEAUDIO"
        assert music_file.exists() and music_file.read_bytes() == b"FAKEAUDIO"
        assert meta_tts["file"].endswith("test-dish_voice.mp3")
        assert meta_music["file"].endswith("test-dish_music.mp3")
    finally:
        audio_module.BUILD_DIR = old_build
