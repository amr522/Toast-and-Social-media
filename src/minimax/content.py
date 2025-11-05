from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.menu.utils import BUILD_DIR, ITEM_OUTPUT_DIR, ensure_build_tree, write_json
from .client import MiniMaxClient
from .text import generate_text
from src.platforms.specs import PLATFORM_SPECS


_LOG = logging.getLogger(__name__)
CONTENT_DIR = BUILD_DIR / "content"


def _load_item_json(slug: str) -> Dict[str, Any]:
    """Load per-item JSON from menu/items/**/{slug}.json"""
    for p in ITEM_OUTPUT_DIR.rglob(f"{slug}.json"):
        return _read_json(p)
    raise FileNotFoundError(f"menu item JSON not found for slug '{slug}' under {ITEM_OUTPUT_DIR}")


def _read_json(path: Path) -> Dict[str, Any]:
    import json

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _extract_text_from_response(resp: Dict[str, Any]) -> str:
    """Best-effort extraction of text from MiniMax chat completion response."""
    # Anthropic-like: { choices: [ { message: { content: "..." } } ] }
    try:
        choices = resp.get("choices") or resp.get("data")
        if isinstance(choices, list) and choices:
            first = choices[0]
            msg = first.get("message") if isinstance(first, dict) else None
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    return content
    except Exception:  # noqa: BLE001
        pass
    # Generic outputs
    for key in ("text", "output", "result"):
        val = resp.get(key)
        if isinstance(val, str):
            return val
        if isinstance(val, dict) and isinstance(val.get("text"), str):
            return val["text"]
    return ""


def _detect_allergens(ingredients: List[str] | None) -> List[str]:
    if not ingredients:
        return []
    ing = ", ".join(ingredients).lower()
    allergens = []
    if any(k in ing for k in ["shrimp", "clam", "mussel", "scallop", "oyster", "crab", "lobster"]):
        allergens.append("shellfish")
    if any(k in ing for k in ["salmon", "tuna", "cod", "anchovy", "fish"]):
        allergens.append("fish")
    if any(k in ing for k in ["milk", "cream", "butter", "cheese", "parmesan", "mozzarella", "ricotta"]):
        allergens.append("dairy")
    if any(k in ing for k in ["wheat", "flour", "pasta", "linguine", "penne", "bread", "breadcrumbs"]):
        allergens.append("gluten")
    if any(k in ing for k in ["egg", "eggs"]):
        allergens.append("egg")
    if any(k in ing for k in ["soy", "soy sauce", "tofu"]):
        allergens.append("soy")
    if any(k in ing for k in ["peanut", "almond", "walnut", "pistachio", "hazelnut", "pecan"]):
        allergens.append("tree-nuts")
    return sorted(set(allergens))


def _default_local_seo_context() -> Dict[str, Any]:
    """Best-effort Fort Myers context if online search is not configured."""
    return {
        "city": "Fort Myers, FL",
        "region": "Southwest Florida",
        "restaurant": "41 Bistro",
        "keywords": [
            "Fort Myers dining",
            "Italian restaurant Fort Myers",
            "best Italian food FL",
            "Southwest Florida food scene",
            "date night Fort Myers",
            "outdoor dining Fort Myers",
        ],
        "hashtags": [
            "#41Bistro",
            "#FortMyersEats",
            "#ItalianFoodFL",
            "#FortMyersDining",
            "#SWFL",
        ],
        "cta": [
            "Visit us at 41 Bistro",
            "Reserve your table",
            "Italian dining in Fort Myers",
        ],
    }


def _platform_template(platform: str) -> Dict[str, Any]:
    spec = PLATFORM_SPECS.get(platform, {})
    max_chars = spec.get("caption_recommended_chars", 150)
    return {
        "tone": "warm, welcoming, modern Italian bistro",
        "style": "concise, appetizing, sensory language",
        "caption_max": max_chars,
    }


def _clip(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    return text[: max(1, limit - 1)].rstrip() + "…"


def _hashtags_from(item: Dict[str, Any], local: Dict[str, Any]) -> List[str]:
    base = [
        "#Italian",
        "#Pasta",
        "#Bistro",
    ]
    slug = item.get("slug", "")
    name = (item.get("name") or slug).replace(" ", "")
    dynamic = [
        f"#{name}",
    ]
    local_tags = list(local.get("hashtags", []))
    # Remove duplicates, keep order
    seen = set()
    out: List[str] = []
    for tag in base + dynamic + local_tags:
        if tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def _build_system_prompt() -> str:
    return (
        "You are a marketing copywriter for a modern Italian bistro named '41 Bistro' in Fort Myers, FL. "
        "Write engaging, on-brand copy with local SEO keywords. Avoid false local facts if no source info is provided."
    )


def _build_narration_user_prompt(item: Dict[str, Any], local: Dict[str, Any]) -> str:
    parts = [
        f"Menu item: {item.get('name')} ({item.get('slug')})",
        f"Description: {item.get('description', '')}",
        f"Ingredients: {', '.join(item.get('ingredients') or [])}",
        f"Location: {local.get('city')}, {local.get('region')}",
        "Voice and style: warm, inviting, natural; 20s read time.",
        "Include the restaurant name '41 Bistro' and a gentle call to action.",
    ]
    return "\n".join(parts)


def _build_caption_user_prompt(platform: str, item: Dict[str, Any], local: Dict[str, Any], limit: int) -> str:
    keywords = ", ".join(local.get("keywords", []))
    parts = [
        f"Platform: {platform}",
        f"Menu item: {item.get('name')} ({item.get('slug')})",
        f"Description: {item.get('description', '')}",
        f"Ingredients: {', '.join(item.get('ingredients') or [])}",
        f"Local SEO keywords: {keywords}",
        "Include: '41 Bistro', 'Fort Myers, FL', 'Southwest Florida'.",
        "Tone: warm, modern Italian bistro. Use sensory words.",
        f"Length: concise, <= {limit} characters for the main caption (hashtags appended separately).",
        "End with a short call to action.",
    ]
    return "\n".join(parts)


def generate_narration_script(
    slug: str,
    *,
    client: Optional[MiniMaxClient] = None,
    local_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a voiceover script for a menu item and save to build/content/{slug}.json (merged)."""
    ensure_build_tree()
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    item = _load_item_json(slug)
    local = local_context or _default_local_seo_context()
    client = client or MiniMaxClient()

    sys_prompt = _build_system_prompt()
    user_prompt = _build_narration_user_prompt(item, local)

    resp = generate_text(
        client,
        messages=[{"role": "user", "content": user_prompt}],
        system=sys_prompt,
        temperature=0.7,
        max_tokens=300,
    )
    script = _extract_text_from_response(resp).strip()

    out_path = CONTENT_DIR / f"{slug}.json"
    data = {}
    if out_path.exists():
        data = _read_json(out_path)
    data.setdefault("slug", slug)
    data.setdefault("platforms", {})
    data["narration_script"] = script
    data["meta"] = {
        **(data.get("meta") or {}),
        "model": client.config.chat_model,
        "local_context_used": True,
    }
    write_json(out_path, data)
    return {"slug": slug, "script": script, "path": str(out_path)}


def write_seo_copy(
    slug: str,
    *,
    platforms: Optional[List[str]] = None,
    client: Optional[MiniMaxClient] = None,
    local_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate platform-specific captions, hashtags, and alt text; save to build/content/{slug}.json."""
    ensure_build_tree()
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    item = _load_item_json(slug)
    allergens = _detect_allergens(item.get("ingredients"))
    local = local_context or _default_local_seo_context()
    client = client or MiniMaxClient()
    targets = platforms or list(PLATFORM_SPECS.keys())

    sys_prompt = _build_system_prompt()

    outputs: Dict[str, Any] = {}
    for platform in targets:
        spec = PLATFORM_SPECS.get(platform, {})
        template = _platform_template(platform)
        limit = int(template.get("caption_max", 150))

        user_prompt = _build_caption_user_prompt(platform, item, local, limit)
        resp = generate_text(
            client,
            messages=[{"role": "user", "content": user_prompt}],
            system=sys_prompt,
            temperature=0.7,
            max_tokens=300,
        )
        caption = _clip(_extract_text_from_response(resp).strip(), limit)
        hashtags = _hashtags_from(item, local)
        alt_text = f"{item.get('name')} at 41 Bistro in Fort Myers, FL: {item.get('description', '').strip()}"
        outputs[platform] = {
            "caption": caption,
            "hashtags": hashtags,
            "alt_text": alt_text,
        }

    warnings = [f"Contains: {', '.join(allergens)}"] if allergens else []

    out_path = CONTENT_DIR / f"{slug}.json"
    data = {}
    if out_path.exists():
        data = _read_json(out_path)
    data.update(
        {
            "slug": slug,
            "platforms": outputs,
            "allergen_warnings": warnings,
            "meta": {
                "model": client.config.chat_model,
                "local_context_used": True,
            },
        }
    )
    write_json(out_path, data)
    return {"slug": slug, "path": str(out_path), "platforms": outputs, "allergens": allergens}

