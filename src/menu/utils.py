from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
MENU_DIR = ROOT_DIR / "menu"
DATA_DIR = ROOT_DIR / "data"
BUILD_DIR = ROOT_DIR / "build"
ITEM_OUTPUT_DIR = MENU_DIR / "items"
PROCESSED_DIR = BUILD_DIR / "processed"

SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


@dataclass
class MenuItem:
    slug: str
    name: str
    description: str
    course: str
    section: str
    section_notes: Optional[str]
    ingredients: Optional[List[str]] = None
    options: Optional[List[str]] = None
    notes: Optional[str] = None
    source_file: Optional[Path] = None

    def to_dict(self, include_images: bool = True) -> dict:
        data = asdict(self)
        if self.ingredients is None:
            data.pop("ingredients")
        if self.options is None:
            data.pop("options")
        if self.notes is None:
            data.pop("notes")
        if self.section_notes is None:
            data.pop("section_notes")
        if include_images:
            images = [str(p.relative_to(ROOT_DIR)) for p in find_images_for_slug(self.slug)]
            data["images"] = images
            marker = marker_path(self.slug)
            data["status"] = "processed" if marker.exists() else ("new" if images else "missing-image")
            if marker.exists():
                data["last_processed_at"] = marker.read_text().strip()
        data["source_file"] = str(self.source_file.relative_to(ROOT_DIR)) if self.source_file else None
        return data


def load_menu_items() -> List[MenuItem]:
    items: List[MenuItem] = []
    for yaml_path in sorted(MENU_DIR.glob("*.yaml")):
        with yaml_path.open("r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle) or {}
        course = document.get("course") or yaml_path.stem
        for section in document.get("sections", []):
            section_name = section.get("name", "Unknown Section")
            section_notes = section.get("notes")
            for raw_item in section.get("items", []):
                slug = raw_item["slug"].strip()
                description = raw_item.get("description") or "Description forthcoming."
                item = MenuItem(
                    slug=slug,
                    name=raw_item.get("name", slug.replace("-", " ")).strip(),
                    description=description.strip(),
                    course=str(course),
                    section=str(section_name),
                    section_notes=section_notes,
                    ingredients=raw_item.get("ingredients"),
                    options=raw_item.get("options"),
                    notes=raw_item.get("notes"),
                    source_file=yaml_path,
                )
                items.append(item)
    return items


def find_images_for_slug(slug: str) -> List[Path]:
    matches: List[Path] = []
    for ext in SUPPORTED_IMAGE_EXTENSIONS:
        direct = DATA_DIR / f"{slug}{ext}"
        if direct.exists():
            matches.append(direct)
        matches.extend(sorted(DATA_DIR.glob(f"{slug}-*{ext}")))
    return sorted(set(matches))


def marker_path(slug: str) -> Path:
    return PROCESSED_DIR / f"{slug}.done"


def ensure_build_tree() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ITEM_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")