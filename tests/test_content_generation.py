from __future__ import annotations

import json
from pathlib import Path

import src.minimax.content as content_module
import src.menu.utils as utils


def test_content_generation_writes_build_json(tmp_path, monkeypatch):
    build_dir = tmp_path / "build"
    items_dir = tmp_path / "menu" / "items" / "dinner"
    build_dir.mkdir(parents=True)
    items_dir.mkdir(parents=True)

    # Monkeypatch utils/content paths
    monkeypatch.setattr(utils, "BUILD_DIR", build_dir)
    monkeypatch.setattr(utils, "ITEM_OUTPUT_DIR", tmp_path / "menu" / "items")
    monkeypatch.setattr(content_module, "CONTENT_DIR", build_dir / "content")
    monkeypatch.setattr(content_module, "ITEM_OUTPUT_DIR", tmp_path / "menu" / "items")

    # Create a dummy item JSON
    slug = "test-dish"
    item_path = items_dir / f"{slug}.json"
    item_path.write_text(
        json.dumps({
            "slug": slug,
            "name": "Test Dish",
            "description": "A delicious sample.",
            "ingredients": ["Pasta", "Butter"],
        }),
        encoding="utf-8",
    )

    # Stub generate_text to return a predictable caption/script
    monkeypatch.setattr(content_module, "generate_text", lambda *a, **k: {"choices": [{"message": {"content": "Hello 41 Bistro"}}]})

    # Generate narration and platform copy
    content_module.generate_narration_script(slug)
    content_module.write_seo_copy(slug, platforms=["instagram_feed"]) 

    out = build_dir / "content" / f"{slug}.json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "narration_script" in data and data["narration_script"]
    assert "platforms" in data and "instagram_feed" in data["platforms"]
    assert "allergen_warnings" in data
