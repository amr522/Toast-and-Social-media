from __future__ import annotations

import os
from contextlib import contextmanager

from src.minimax.config import load_config


@contextmanager
def env(**kwargs):
    old = {k: os.environ.get(k) for k in kwargs}
    try:
        os.environ.update({k: str(v) for k, v in kwargs.items()})
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_model_aliases_are_canonicalized():
    with env(
        MINIMAX_BASE_URL="https://api.minimax.io",
        MINIMAX_CHAT_MODEL="minimax-m2",
        MINIMAX_IMAGE_MODEL="minimax-image-01",
        MINIMAX_TTS_MODEL="speech-02-hd",
        MINIMAX_MUSIC_MODEL="minimax-music-v1.5",
        MINIMAX_VIDEO_MODEL="minimax/hailuo-02",
        RATE_LIMIT_RPM="30",
        MAX_RETRIES="5",
    ):
        cfg = load_config()
        assert cfg.base_url == "https://api.minimax.io"
        assert cfg.chat_model == "MiniMax-M2"
        assert cfg.image_model == "image-01"
        assert cfg.tts_model == "speech-2.6-hd"
        assert cfg.music_model == "music-2.0"
        assert cfg.video_model == "MiniMax-Hailuo-02"
        assert cfg.rate_limit_rpm == 30
        assert cfg.max_retries == 5

