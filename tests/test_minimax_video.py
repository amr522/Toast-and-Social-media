from __future__ import annotations

import base64
from pathlib import Path

from src.minimax.config import MiniMaxConfig
from src.minimax.client import MiniMaxClient
from src.minimax.video import render_video_for_slug


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


def test_render_video_for_slug_with_base64(monkeypatch, tmp_path):
    # Arrange build dirs with assets
    enhanced_dir = tmp_path / "build" / "enhanced_images"
    audio_dir = tmp_path / "build" / "audio"
    video_dir = tmp_path / "build" / "videos"
    enhanced_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    (enhanced_dir / "dish_1.jpg").write_bytes(b"IMG")
    (audio_dir / "dish_voice.mp3").write_bytes(b"VOICE")
    (audio_dir / "dish_music.mp3").write_bytes(b"MUSIC")

    # Monkeypatch module constants to use tmp build dir
    import src.minimax.video as video_module
    import src.menu.utils as utils

    old_build = utils.BUILD_DIR
    utils.BUILD_DIR = tmp_path / "build"
    video_module.BUILD_DIR = utils.BUILD_DIR
    video_module.VIDEOS_DIR = utils.BUILD_DIR / "videos"

    # Prepare fake MiniMax client returning base64 video and thumb
    client = _mk_client()
    v_b64 = base64.b64encode(b"FAKEVIDEO").decode("ascii")
    t_b64 = base64.b64encode(b"FAKETHUMB").decode("ascii")

    def fake_video_generation(payload):  # type: ignore[no-untyped-def]
        return {"base_resp": {"status_code": 0}, "video_base64": v_b64, "thumbnail_base64": t_b64}

    client.video_generation = fake_video_generation  # type: ignore[assignment]

    try:
        meta = render_video_for_slug("dish", client=client, platform="instagram_reel")
        # Assert files
        assert (video_dir / "dish.mp4").exists()
        assert (video_dir / "dish.json").exists()
        assert meta["file"].endswith("dish.mp4")
        assert (video_dir / "dish_thumb.jpg").exists()
    finally:
        utils.BUILD_DIR = old_build

