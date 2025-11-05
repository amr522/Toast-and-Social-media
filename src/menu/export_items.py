from __future__ import annotations

import argparse
from pathlib import Path

from .utils import ITEM_OUTPUT_DIR, ensure_build_tree, load_menu_items, write_json


def export_menu_items(output_dir: Path | None = None) -> list[Path]:
    ensure_build_tree()
    out_dir = output_dir or ITEM_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    written_paths: list[Path] = []
    for item in load_menu_items():
        course_dir = out_dir / item.course
        course_dir.mkdir(parents=True, exist_ok=True)
        output_path = course_dir / f"{item.slug}.json"
        write_json(output_path, item.to_dict())
        written_paths.append(output_path)
    return written_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Export menu YAML into per-item JSON files.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Optional output directory for JSON files.")
    args = parser.parse_args()

    paths = export_menu_items(args.output_dir)
    print(f"Exported {len(paths)} menu item files.")


if __name__ == "__main__":
    main()
