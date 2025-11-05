from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from src.menu.utils import (
    DATA_DIR,
    SUPPORTED_IMAGE_EXTENSIONS,
    ensure_build_tree,
    find_images_for_slug,
    load_menu_items,
)


def validate_assets(verbose: bool = False) -> int:
    ensure_build_tree()
    items = load_menu_items()
    slugs = {item.slug for item in items}

    missing_images: list[str] = []
    for item in items:
        images = find_images_for_slug(item.slug)
        if not images:
            missing_images.append(item.slug)
        elif verbose:
            print(f"{item.slug}: {', '.join(str(img.relative_to(DATA_DIR.parent)) for img in images)}")

    # detect stray images that do not map to any menu slug prefix
    stray_images: list[Path] = []
    for image in DATA_DIR.glob("*"):
        if not image.is_file() or image.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            continue
        stem = image.stem
        if any(stem == slug or stem.startswith(f"{slug}-") for slug in slugs):
            continue
        stray_images.append(image)

    if missing_images:
        print("Menu items missing images:")
        for slug in missing_images:
            print(f"  - {slug}")
    else:
        print("All menu items have at least one image or are pending capture.")

    if stray_images:
        print("Images without matching menu entries:")
        for image in stray_images:
            print(f"  - {image.name}")

    print(f"Total items: {len(items)} | Missing images: {len(missing_images)} | Unmatched images: {len(stray_images)}")
    return 1 if stray_images else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate parity between menu entries and data images.")
    parser.add_argument("--verbose", action="store_true", help="Show image matches for each item.")
    args = parser.parse_args()
    exit_code = validate_assets(verbose=args.verbose)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
