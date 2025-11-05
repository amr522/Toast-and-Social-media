from __future__ import annotations

import logging
import os
from base64 import b64decode
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from src.menu.utils import BUILD_DIR, ensure_build_tree, write_json
from .client import MiniMaxClient


_LOG = logging.getLogger(__name__)
AUDIO_DIR = BUILD_DIR / "audio"


def synthesize_voice(
    client: MiniMaxClient,
    text: str,
    *,
    voice_profile: Optional[str] = None,
    format: str = "mp3",
    speed: float = 1.0,
    pitch: float = 1.0,
) -> Dict[str, Any]:
    """Low-level TTS call. Returns raw API response."""
    payload: Dict[str, Any] = {
        "input": text,
        "output_format": format,
        "speed": speed,
        "pitch": pitch,
    }
    if voice_profile:
        payload["voice"] = voice_profile
    return client.text_to_speech(payload)


def compose_music(
    client: MiniMaxClient,
    *,
    prompt: str,
    lyrics: Optional[str] = None,
    duration_sec: Optional[int] = None,
    style: Optional[str] = None,
    format: str = "mp3",
) -> Dict[str, Any]:
    """Low-level music generation call. Returns raw API response."""
    payload: Dict[str, Any] = {
        "prompt": prompt,
        "output_format": format,
    }
    if lyrics:
        payload["lyrics"] = lyrics
    if duration_sec:
        payload["duration"] = duration_sec
    if style:
        payload["style"] = style
    return client.music_generation(payload)


def _extract_audio_bytes(resp: Dict[str, Any]) -> bytes:
    """Best-effort extraction of audio bytes from MiniMax responses.

    Looks for base64 or URL fields in common locations.
    """
    # Known shapes: { audio_url }, { data: [{url}] }, { audio: <b64> }, { b64: ... }
    b64 = (
        resp.get("audio")
        or resp.get("b64")
        or resp.get("b64_audio")
        or resp.get("b64_json")
    )
    if isinstance(b64, str):
        return b64decode(b64)

    url = resp.get("audio_url") or resp.get("url")
    if isinstance(url, str):
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return r.content

    data = resp.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            if isinstance(first.get("b64"), str):
                return b64decode(first["b64"])
            if isinstance(first.get("url"), str):
                r = requests.get(first["url"], timeout=60)
                r.raise_for_status()
                return r.content

    raise ValueError("Could not find audio content in MiniMax response")


def synthesize_voice_for_slug(
    slug: str,
    *,
    script: Optional[str] = None,
    client: Optional[MiniMaxClient] = None,
    voice_profile: Optional[str] = None,
    format: str = "mp3",
    speed: float = 1.0,
    pitch: float = 1.0,
) -> Dict[str, Any]:
    """Create narration audio from a prepared script in build/content/{slug}.json (or provided script).

    Saves audio to build/audio/{slug}_voice.{format} and a metadata JSON alongside it.
    Returns a dict with file path and meta info.
    """
    ensure_build_tree()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    client = client or MiniMaxClient()
    voice = voice_profile or os.getenv("VOICE_PROFILE", "warm")

    # Load narration script if not provided
    if not script:
        content_path = BUILD_DIR / "content" / f"{slug}.json"
        if not content_path.exists():
            raise FileNotFoundError(f"Narration script not found: {content_path}")
        import json

        with content_path.open("r", encoding="utf-8") as f:
            content = json.load(f)
            script = (content.get("narration_script") or "").strip()
        if not script:
            raise ValueError("narration_script is empty; run generate_narration_script first or pass script explicitly")

    resp = synthesize_voice(client, script, voice_profile=voice, format=format, speed=speed, pitch=pitch)
    audio_bytes = _extract_audio_bytes(resp)

    audio_path = AUDIO_DIR / f"{slug}_voice.{format}"
    audio_path.write_bytes(audio_bytes)

    meta = {
        "slug": slug,
        "file": str(audio_path.relative_to(BUILD_DIR.parent)),
        "model": client.config.tts_model,
        "voice_profile": voice,
        "format": format,
    }
    write_json(AUDIO_DIR / f"{slug}_voice.json", meta)
    if _LOG.isEnabledFor(logging.INFO):
        _LOG.info("Synthesized voice for %s -> %s", slug, audio_path)
    return meta


def compose_music_for_slug(
    slug: str,
    *,
    vibe: Optional[str] = None,
    duration_sec: int = 20,
    client: Optional[MiniMaxClient] = None,
    format: str = "mp3",
) -> Dict[str, Any]:
    """Generate a background music track to pair with the video, saved under build/audio/{slug}_music.{format}."""
    ensure_build_tree()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    client = client or MiniMaxClient()
    mood = vibe or os.getenv("MUSIC_VIBE", "ambient")

    prompt = (
        f"Compose {mood} instrumental background music for a short Italian bistro video about '{slug}'. "
        f"Warm, inviting, modern; duration ~{duration_sec} seconds."
    )
    resp = compose_music(client, prompt=prompt, duration_sec=duration_sec, format=format, style=mood)
    audio_bytes = _extract_audio_bytes(resp)

    audio_path = AUDIO_DIR / f"{slug}_music.{format}"
    audio_path.write_bytes(audio_bytes)

    meta = {
        "slug": slug,
        "file": str(audio_path.relative_to(BUILD_DIR.parent)),
        "model": client.config.music_model,
        "vibe": mood,
        "duration_sec": duration_sec,
        "format": format,
    }
    write_json(AUDIO_DIR / f"{slug}_music.json", meta)
    if _LOG.isEnabledFor(logging.INFO):
        _LOG.info("Composed music for %s -> %s", slug, audio_path)
    return meta
