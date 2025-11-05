from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.menu.export_items import export_menu_items
from src.menu.utils import (
    BUILD_DIR,
    PROCESSED_DIR,
    ensure_build_tree,
    find_images_for_slug,
    load_menu_items,
    marker_path,
)


def mark_processed(slug: str) -> Path:
    ensure_build_tree()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    marker = marker_path(slug)
    timestamp = datetime.now(timezone.utc).isoformat()
    marker.write_text(f"{timestamp}\n", encoding="utf-8")
    return marker


def write_manifest() -> Path:
    ensure_build_tree()
    manifest_path = BUILD_DIR / "manifest.csv"
    items = load_menu_items()
    fieldnames = ["slug", "course", "section", "image", "status", "last_processed_at"]

    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            images = find_images_for_slug(item.slug)
            marker = marker_path(item.slug)
            processed = marker.exists()
            last_processed = marker.read_text().strip() if processed else ""
            if not images:
                writer.writerow(
                    {
                        "slug": item.slug,
                        "course": item.course,
                        "section": item.section,
                        "image": "",
                        "status": "missing-image",
                        "last_processed_at": last_processed,
                    }
                )
            else:
                for image in images:
                    writer.writerow(
                        {
                            "slug": item.slug,
                            "course": item.course,
                            "section": item.section,
                            "image": str(image.relative_to(BUILD_DIR.parent)),
                            "status": "processed" if processed else "new",
                            "last_processed_at": last_processed,
                        }
                    )
    return manifest_path


def run_pipeline(slugs: Iterable[str] | None = None, dry_run: bool = False) -> None:
    ensure_build_tree()
    export_menu_items()

    items = load_menu_items()
    slug_filter = set(slugs or [])

    for item in items:
        if slug_filter and item.slug not in slug_filter:
            continue
        images = find_images_for_slug(item.slug)
        if not images:
            continue
        if dry_run:
            print(f"[dry-run] Would mark {item.slug} as processed with {len(images)} image(s).")
            continue
        mark_processed(item.slug)
        print(f"Marked {item.slug} as processed ({len(images)} image(s)).")

    manifest_path = write_manifest()
    print(f"Manifest updated at {manifest_path.relative_to(BUILD_DIR.parent)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prototype pipeline run that creates processed markers and manifest.")
    parser.add_argument("--slug", action="append", help="Process only the specified slug(s). Can be provided multiple times.")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing markers.")
    args = parser.parse_args()

    run_pipeline(slugs=args.slug, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
