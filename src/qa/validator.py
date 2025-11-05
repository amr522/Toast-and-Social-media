from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.menu.utils import BUILD_DIR
from src.platforms.specs import PLATFORM_SPECS


REQUIRED_BRAND = "41 Bistro"
REQUIRED_LOCAL_TERMS = ["Fort Myers", "Southwest Florida"]

MIN_IMAGE_BYTES = int(os.getenv("QA_MIN_IMAGE_BYTES", str(10 * 1024)))
MIN_AUDIO_BYTES = int(os.getenv("QA_MIN_AUDIO_BYTES", str(1 * 1024)))
MIN_VIDEO_BYTES = int(os.getenv("QA_MIN_VIDEO_BYTES", str(50 * 1024)))


@dataclass
class QAResult:
    slug: str
    issues: List[str]
    score: int
    metrics: Dict[str, int]


def _size_ok(path: Path, min_bytes: int) -> bool:
    try:
        return path.exists() and path.stat().st_size >= min_bytes
    except Exception:
        return False


def _has_terms(text: str, terms: List[str]) -> bool:
    t = text or ""
    return any(term.lower() in t.lower() for term in terms)


def _load_platform_content(slug: str, platform: str) -> Optional[Dict]:
    import json

    path = BUILD_DIR / "platform_assets" / platform / slug / "content.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def validate_slug(slug: str) -> QAResult:
    issues: List[str] = []
    metrics: Dict[str, int] = {}

    enhanced = list((BUILD_DIR / "enhanced_images").glob(f"{slug}_*.jpg"))
    if not enhanced:
        issues.append("missing enhanced image(s)")
    else:
        ok_sizes = sum(1 for p in enhanced if _size_ok(p, MIN_IMAGE_BYTES))
        if ok_sizes < len(enhanced):
            issues.append("enhanced image too small")
        metrics["enhanced_images"] = len(enhanced)

    content_path = BUILD_DIR / "content" / f"{slug}.json"
    if not content_path.exists():
        issues.append("missing content json")
    else:
        import json

        try:
            content = json.loads(content_path.read_text(encoding="utf-8"))
        except Exception:
            content = {}
            issues.append("content json unreadable")

        if isinstance(content, dict):
            platforms = content.get("platforms") or {}
            if not platforms:
                issues.append("content missing platform entries")

            # Brand and local terms checks across captions and alt text
            for platform, entry in platforms.items():
                cap = str((entry or {}).get("caption") or "")
                alt = str((entry or {}).get("alt_text") or "")
                if not _has_terms(cap + " " + alt, [REQUIRED_BRAND]):
                    issues.append(f"{platform}: missing brand mention")
                if not _has_terms(cap + " " + alt, REQUIRED_LOCAL_TERMS):
                    issues.append(f"{platform}: missing local mention")

    voice = BUILD_DIR / "audio" / f"{slug}_voice.mp3"
    if not _size_ok(voice, MIN_AUDIO_BYTES):
        issues.append("missing or tiny voice audio")

    music = BUILD_DIR / "audio" / f"{slug}_music.mp3"
    if not _size_ok(music, MIN_AUDIO_BYTES):
        issues.append("missing or tiny music audio")

    video = BUILD_DIR / "videos" / f"{slug}.mp4"
    if not _size_ok(video, MIN_VIDEO_BYTES):
        issues.append("missing or tiny video file")

    # Platform bundles
    for platform in PLATFORM_SPECS.keys():
        bundle = BUILD_DIR / "platform_assets" / platform / slug
        if not (bundle / "image.jpg").exists():
            issues.append(f"{platform} bundle missing image.jpg")
        if not _size_ok(bundle / "video.mp4", MIN_VIDEO_BYTES):
            issues.append(f"{platform} bundle missing or tiny video.mp4")
        pcontent = _load_platform_content(slug, platform)
        if not pcontent:
            issues.append(f"{platform} bundle missing content.json")
        else:
            cap = str(pcontent.get("caption") or "")
            alt = str(pcontent.get("alt_text") or "")
            if not _has_terms(cap + " " + alt, [REQUIRED_BRAND]):
                issues.append(f"{platform} bundle missing brand mention")
            if not _has_terms(cap + " " + alt, REQUIRED_LOCAL_TERMS):
                issues.append(f"{platform} bundle missing local mention")

    # Score: start 100, minus 5 per issue (cap at 0)
    score = max(0, 100 - 5 * len(issues))
    return QAResult(slug=slug, issues=issues, score=score, metrics=metrics)


def validate_many(slugs: List[str]) -> Dict[str, QAResult]:
    return {slug: validate_slug(slug) for slug in slugs}

