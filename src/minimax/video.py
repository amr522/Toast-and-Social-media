from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.menu.utils import BUILD_DIR, ensure_build_tree, write_json
from src.platforms.specs import PLATFORM_SPECS
from .client import MiniMaxClient


_LOG = logging.getLogger(__name__)
VIDEOS_DIR = BUILD_DIR / "videos"


def _read_b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _extract_job_or_result(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (job_id, video_url_or_b64, thumbnail_url_or_b64)."""
    job_id = data.get("task_id") or data.get("id")

    # Direct result
    video_b64 = data.get("video_base64") or data.get("b64") or data.get("b64_json")
    video_url = data.get("video_url") or data.get("url")

    thumb_b64 = data.get("thumbnail_base64") or data.get("thumb_b64")
    thumb_url = data.get("thumbnail_url")

    video = video_b64 or video_url
    thumb = thumb_b64 or thumb_url
    return str(job_id) if job_id else None, video, thumb


def _poll_video_until_ready(client: MiniMaxClient, job_id: str, timeout_sec: int = 120, interval_sec: int = 3) -> Dict[str, Any]:
    import time

    start = time.time()
    while time.time() - start < timeout_sec:
        resp = client.video_query(job_id)
        base = resp.get("base_resp") or {}
        if base.get("status_code") not in (None, 0):
            return resp
        status = resp.get("status") or resp.get("state") or ""
        if status.lower() in {"succeeded", "success", "done", "completed"}:
            return resp
        # Some APIs return result inline when done
        _, video, _ = _extract_job_or_result(resp)
        if video:
            return resp
        time.sleep(interval_sec)
    return {"base_resp": {"status_code": -1, "status_msg": "timeout waiting for video"}}


def render_video(
    client: MiniMaxClient,
    *,
    prompt: Optional[str] = None,
    image_b64s: Optional[List[str]] = None,
    audio_b64: Optional[str] = None,
    music_b64: Optional[str] = None,
    duration_sec: int = 20,
    resolution: str = "1080P",
    aspect_ratio: Optional[str] = None,
    seed: Optional[int] = None,
    async_timeout_sec: int = 180,
) -> Dict[str, Any]:
    """Low-level render call. Accepts base64 inputs to avoid external URLs.

    Returns the final API response (may include task id or direct result).
    """
    payload: Dict[str, Any] = {
        "duration": duration_sec,
        "resolution": resolution,
    }
    if prompt:
        payload["prompt"] = prompt
    if image_b64s:
        payload["images"] = [{"image_base64": b} for b in image_b64s]
    if audio_b64:
        payload["audio_base64"] = audio_b64
    if music_b64:
        payload["music_base64"] = music_b64
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if seed is not None:
        payload["seed"] = seed

    resp = client.video_generation(payload)

    job_id, video, _ = _extract_job_or_result(resp)
    if job_id and not video:
        # Poll until ready
        resp = _poll_video_until_ready(client, job_id, timeout_sec=async_timeout_sec)
    return resp


def render_video_for_slug(
    slug: str,
    *,
    client: Optional[MiniMaxClient] = None,
    platform: Optional[str] = None,
    duration_sec: int = 20,
    aspect_ratio: Optional[str] = None,
    resolution: Optional[str] = None,
) -> Dict[str, Any]:
    """High-level renderer that consumes enhanced image and audio artifacts and writes build/videos/{slug}.mp4.

    - Loads first enhanced image from build/enhanced_images/{slug}_*.jpg
    - Loads voice at build/audio/{slug}_voice.mp3 (optional) and music build/audio/{slug}_music.mp3 (optional)
    - Uses platform spec for aspect ratio/resolution if provided
    - Supports async polling using job ids
    - Saves video file and metadata; creates thumbnail if provided
    """
    ensure_build_tree()
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    client = client or MiniMaxClient()

    # Platform defaults
    if platform and platform in PLATFORM_SPECS:
        spec = PLATFORM_SPECS[platform]
        aspect_ratio = aspect_ratio or spec.get("aspect_ratio")
        if not resolution and isinstance(spec.get("resolution"), tuple):
            w, h = spec["resolution"]
            resolution = f"{max(w, h)}P" if max(w, h) in (512, 768, 1080) else "1080P"

    resolution = resolution or "1080P"

    # Gather assets
    enhanced_dir = BUILD_DIR / "enhanced_images"
    images = sorted(enhanced_dir.glob(f"{slug}_*.jpg"))
    if not images:
        raise FileNotFoundError(f"No enhanced images found for {slug} under {enhanced_dir}")
    image_b64s = [_read_b64(images[0])]

    audio_dir = BUILD_DIR / "audio"
    voice_path = audio_dir / f"{slug}_voice.mp3"
    music_path = audio_dir / f"{slug}_music.mp3"
    audio_b64 = _read_b64(voice_path) if voice_path.exists() else None
    music_b64 = _read_b64(music_path) if music_path.exists() else None

    resp = render_video(
        client,
        image_b64s=image_b64s,
        audio_b64=audio_b64,
        music_b64=music_b64,
        duration_sec=duration_sec,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
    )

    # Extract final video
    _, video, thumb = _extract_job_or_result(resp)
    if not video:
        raise RuntimeError("Video generation returned no result")

    if video.startswith("http"):
        import requests

        r = requests.get(video, timeout=120)
        r.raise_for_status()
        video_bytes = r.content
    else:
        video_bytes = base64.b64decode(video)

    out_path = VIDEOS_DIR / f"{slug}.mp4"
    out_path.write_bytes(video_bytes)

    thumb_path = None
    if thumb:
        try:
            if thumb.startswith("http"):
                import requests

                r = requests.get(thumb, timeout=60)
                r.raise_for_status()
                thumb_bytes = r.content
            else:
                thumb_bytes = base64.b64decode(thumb)
            thumb_path = VIDEOS_DIR / f"{slug}_thumb.jpg"
            thumb_path.write_bytes(thumb_bytes)
        except Exception as e:  # noqa: BLE001
            if _LOG.isEnabledFor(logging.WARNING):
                _LOG.warning("Failed to save thumbnail: %s", e)

    meta = {
        "slug": slug,
        "file": str(out_path.relative_to(BUILD_DIR.parent)),
        "thumbnail": str(thumb_path.relative_to(BUILD_DIR.parent)) if thumb_path else None,
        "model": client.config.video_model,
        "duration_sec": duration_sec,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "platform": platform,
    }
    write_json(VIDEOS_DIR / f"{slug}.json", meta)
    if _LOG.isEnabledFor(logging.INFO):
        _LOG.info("Rendered video for %s -> %s", slug, out_path)
    return meta
