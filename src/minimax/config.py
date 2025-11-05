from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _canonical_model(name: Optional[str], kind: str) -> Optional[str]:
    if not name:
        return None
    raw = name.strip()
    # Canonicalization map for common aliases seen in docs/env
    aliases = {
        # Image
        "minimax-image-01": "image-01",
        # Video
        "minimax/hailuo-02": "MiniMax-Hailuo-02",
        "hailuo-02": "MiniMax-Hailuo-02",
        # TTS/Speech
        "speech-02-hd": "speech-2.6-hd",
        "speech-02-turbo": "speech-2.6-turbo",
        # Music
        "minimax-music-v1.5": "music-2.0",
        # Chat
        "minimax-m2": "MiniMax-M2",
    }
    canon = aliases.get(raw.lower(), raw)
    return canon


@dataclass(frozen=True)
class MiniMaxConfig:
    base_url: str
    api_key: str
    # Models
    chat_model: str
    image_model: str
    tts_model: str
    music_model: str
    video_model: str
    # Client behavior
    rate_limit_rpm: int = 60
    max_retries: int = 3
    timeout_sec: int = 60
    # Endpoint paths (override via env if needed)
    text_path: str = "/v1/text/chat/completions"
    image_path: str = "/v1/image_generation"
    tts_path: str = "/v1/t2a_v2"
    music_path: str = "/v1/music_generation"
    video_path: str = "/v1/video_generation"
    video_query_path: str = "/v1/video_generation/query"


def load_config() -> MiniMaxConfig:
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io").rstrip("/")
    api_key = os.getenv("MINIMAX_API_KEY", "").strip()

    chat_model = _canonical_model(os.getenv("MINIMAX_CHAT_MODEL", "MiniMax-M2"), "chat") or "MiniMax-M2"
    image_model = _canonical_model(os.getenv("MINIMAX_IMAGE_MODEL", "image-01"), "image") or "image-01"
    tts_model = _canonical_model(os.getenv("MINIMAX_TTS_MODEL", "speech-2.6-hd"), "tts") or "speech-2.6-hd"
    music_model = _canonical_model(os.getenv("MINIMAX_MUSIC_MODEL", "music-2.0"), "music") or "music-2.0"
    video_model = _canonical_model(os.getenv("MINIMAX_VIDEO_MODEL", "MiniMax-Hailuo-2.3"), "video") or "MiniMax-Hailuo-2.3"

    rate_limit_rpm = _int_env("RATE_LIMIT_RPM", 60)
    max_retries = _int_env("MAX_RETRIES", 3)
    timeout_sec = _int_env("MINIMAX_TIMEOUT_SEC", 60)

    text_path = os.getenv("MINIMAX_TEXT_PATH", "/v1/text/chat/completions")
    image_path = os.getenv("MINIMAX_IMAGE_PATH", "/v1/image_generation")
    tts_path = os.getenv("MINIMAX_TTS_PATH", "/v1/t2a_v2")
    music_path = os.getenv("MINIMAX_MUSIC_PATH", "/v1/music_generation")
    video_path = os.getenv("MINIMAX_VIDEO_PATH", "/v1/video_generation")
    video_query_path = os.getenv("MINIMAX_VIDEO_QUERY_PATH", "/v1/video_generation/query")

    return MiniMaxConfig(
        base_url=base_url,
        api_key=api_key,
        chat_model=chat_model,
        image_model=image_model,
        tts_model=tts_model,
        music_model=music_model,
        video_model=video_model,
        rate_limit_rpm=rate_limit_rpm,
        max_retries=max_retries,
        timeout_sec=timeout_sec,
        text_path=text_path,
        image_path=image_path,
        tts_path=tts_path,
        music_path=music_path,
        video_path=video_path,
        video_query_path=video_query_path,
    )
