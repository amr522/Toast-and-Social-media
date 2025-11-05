from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from src.menu.utils import (
    BUILD_DIR,
    ensure_build_tree,
    find_images_for_slug,
    load_menu_items,
)
from src.platforms.specs import PLATFORM_SPECS
from src.pipeline.run_once import mark_processed, write_manifest
from src.minimax.image import enhance_image
from src.minimax.content import generate_narration_script, write_seo_copy
from src.minimax.audio import compose_music_for_slug, synthesize_voice_for_slug
from src.minimax.video import render_video_for_slug
from src.drive.sync import get_service as drive_get_service, sync_platform_assets as drive_sync_platform_assets


PLATFORM_ASSETS_DIR = BUILD_DIR / "platform_assets"


def _platform_dir(platform: str, slug: str) -> Path:
    return PLATFORM_ASSETS_DIR / platform / slug


def _first_enhanced_image(slug: str) -> Optional[Path]:
    enhanced_dir = BUILD_DIR / "enhanced_images"
    candidates = sorted(enhanced_dir.glob(f"{slug}_*.jpg"))
    return candidates[0] if candidates else None


def _load_content_json(slug: str) -> Dict:
    path = BUILD_DIR / "content" / f"{slug}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _copy_platform_bundle(slug: str, platform: str) -> Path:
    """Package assets per platform under build/platform_assets/<platform>/<slug>/"""
    out_dir = PLATFORM_ASSETS_DIR / platform / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy image
    img = _first_enhanced_image(slug)
    if img and img.exists():
        shutil.copy2(img, out_dir / "image.jpg")

    # Copy video (platform-specific one should have just been generated)
    video_src = BUILD_DIR / "videos" / f"{slug}.mp4"
    if video_src.exists():
        shutil.copy2(video_src, out_dir / "video.mp4")

    # Write platform-specific content
    content = _load_content_json(slug)
    platforms = content.get("platforms") or {}
    if platform in platforms:
        with (out_dir / "content.json").open("w", encoding="utf-8") as f:
            json.dump(platforms[platform], f, indent=2, ensure_ascii=False)
            f.write("\n")

    return out_dir


def orchestrate_enhancement(
    slug: str,
    *,
    platforms: Optional[List[str]] = None,
    skip_image: bool = False,
    skip_content: bool = False,
    skip_audio: bool = False,
    skip_video: bool = False,
    sync_drive: bool = False,
) -> Dict[str, str]:
    """Run the full pipeline for a single slug with graceful error handling.

    Returns a dict of step statuses.
    """
    ensure_build_tree()
    statuses: Dict[str, str] = {}

    # Validate source image existence early
    if not find_images_for_slug(slug):
        statuses["validate"] = "missing-image"
        return statuses
    statuses["validate"] = "ok"

    # Image enhancement
    if not skip_image:
        try:
            enhance_image(slug, variants=1)
            statuses["image"] = "ok"
        except Exception as e:  # noqa: BLE001
            statuses["image"] = f"error: {e}"
            return statuses
    else:
        statuses["image"] = "skipped"

    # Content generation
    if not skip_content:
        try:
            generate_narration_script(slug)
            write_seo_copy(slug)
            statuses["content"] = "ok"
        except Exception as e:  # noqa: BLE001
            statuses["content"] = f"error: {e}"
            return statuses
    else:
        statuses["content"] = "skipped"

    # Audio generation
    if not skip_audio:
        try:
            synthesize_voice_for_slug(slug)
            compose_music_for_slug(slug)
            statuses["audio"] = "ok"
        except Exception as e:  # noqa: BLE001
            statuses["audio"] = f"error: {e}"
            return statuses
    else:
        statuses["audio"] = "skipped"

    # Video generation + platform bundles
    if not skip_video:
        try:
            targets = platforms or list(PLATFORM_SPECS.keys())
            drive_service = drive_get_service() if sync_drive else None
            for platform in targets:
                # Render a platform-appropriate cut then copy to bundle
                render_video_for_slug(slug, platform=platform)
                _copy_platform_bundle(slug, platform)
                if sync_drive and drive_service is not None:
                    try:
                        drive_sync_platform_assets(slug, platform, service=drive_service)
                    except Exception as e:  # noqa: BLE001
                        # record but do not fail the entire video step
                        pass
            statuses["video"] = "ok"
        except Exception as e:  # noqa: BLE001
            statuses["video"] = f"error: {e}"
            return statuses
    else:
        statuses["video"] = "skipped"

    # Mark processed and update manifest
    try:
        mark_processed(slug)
        write_manifest()
        statuses["finalize"] = "ok"
    except Exception as e:  # noqa: BLE001
        statuses["finalize"] = f"error: {e}"

    return statuses


def _iter_target_slugs(all_items: bool, selected: List[str] | None) -> List[str]:
    if all_items:
        items = load_menu_items()
        # Only process those with at least one source image
        return [it.slug for it in items if find_images_for_slug(it.slug)]
    return selected or []


def main() -> None:
    parser = argparse.ArgumentParser(description="MiniMax enhancement orchestrator")
    parser.add_argument("--slug", action="append", help="Slug(s) to process; can be specified multiple times.")
    parser.add_argument("--all", action="store_true", help="Process all items that have images available.")
    parser.add_argument("--platforms", help="Comma-separated platform keys (default: all in specs).")
    parser.add_argument("--skip-image", action="store_true")
    parser.add_argument("--skip-content", action="store_true")
    parser.add_argument("--skip-audio", action="store_true")
    parser.add_argument("--skip-video", action="store_true")
    parser.add_argument("--sync-drive", action="store_true", help="Upload platform bundles to Google Drive after render")
    args = parser.parse_args()

    platforms: Optional[List[str]] = None
    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    slugs = _iter_target_slugs(args.all, args.slug)
    if not slugs:
        raise SystemExit("No slugs provided or found.")

    for slug in slugs:
        print(f"[orchestrator] Processing {slug}…")
        statuses = orchestrate_enhancement(
            slug,
            platforms=platforms,
            skip_image=args.skip_image,
            skip_content=args.skip_content,
            skip_audio=args.skip_audio,
            skip_video=args.skip_video,
            sync_drive=args.sync_drive,
        )
        print(f"[orchestrator] {slug} → {statuses}")


if __name__ == "__main__":
    main()
