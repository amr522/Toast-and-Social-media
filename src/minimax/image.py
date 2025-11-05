from __future__ import annotations

import logging
import os
from base64 import b64decode, b64encode
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

from src.menu.utils import BUILD_DIR, DATA_DIR, ensure_build_tree, find_images_for_slug, load_menu_items, write_json
from .client import MiniMaxClient


_LOG = logging.getLogger(__name__)
ENHANCED_DIR = BUILD_DIR / "enhanced_images"


def _read_b64(path: Path) -> str:
    data = path.read_bytes()
    return b64encode(data).decode("ascii")


def _extract_image_sources(response: Dict[str, Any]) -> List[Dict[str, str]]:
    """Best-effort extraction of image sources from MiniMax response.

    Returns a list of dicts with either {"b64": "..."} or {"url": "..."}.
    The schema can vary, so we look through common patterns.
    """
    out: List[Dict[str, str]] = []

    def add_url(u: Optional[str]):
        if u and isinstance(u, str):
            out.append({"url": u})

    def add_b64(b: Optional[str]):
        if b and isinstance(b, str):
            out.append({"b64": b})

    # Common patterns
    candidates = [
        response.get("data"),
        response.get("images"),
        response.get("result"),
        response.get("output"),
        response.get("items"),
    ]
    for c in candidates:
        if isinstance(c, list):
            for item in c:
                if not isinstance(item, dict):
                    continue
                # Known keys
                add_url(item.get("url") or item.get("image_url"))
                add_b64(item.get("b64_json") or item.get("image_base64") or item.get("base64"))
        elif isinstance(c, dict):
            add_url(c.get("url") or c.get("image_url"))
            add_b64(c.get("b64_json") or c.get("image_base64") or c.get("base64"))

    # Some responses might have urls field
    urls = response.get("urls")
    if isinstance(urls, list):
        for u in urls:
            if isinstance(u, str):
                add_url(u)

    # Deduplicate while preserving order
    seen = set()
    unique_out: List[Dict[str, str]] = []
    for item in out:
        key = ("url", item.get("url")) if "url" in item else ("b64", item.get("b64"))
        if key not in seen and key[1]:
            seen.add(key)
            unique_out.append(item)
    return unique_out


def _download(url: str) -> bytes:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content


def _save_variant(slug: str, index: int, content: bytes, ext: str = ".jpg") -> Path:
    ENHANCED_DIR.mkdir(parents=True, exist_ok=True)
    path = ENHANCED_DIR / f"{slug}_{index}{ext}"
    path.write_bytes(content)
    return path


def enhance_image_request(
    client: MiniMaxClient,
    image_path: Path,
    prompt: str,
    *,
    style_preset: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    n: int = 1,
) -> Dict[str, Any]:
    """Low-level call to MiniMax image generation API using base64 input image."""
    payload: Dict[str, Any] = {
        "prompt": prompt,
        "images": [
            {
                "type": "input_image",
                "image_base64": _read_b64(Path(image_path)),
            }
        ],
        "n": max(1, int(n)),
    }
    if style_preset:
        payload["style_preset"] = style_preset
    if width:
        payload["width"] = width
    if height:
        payload["height"] = height
    return client.image_generation(payload)


def _default_prompt_for_slug(slug: str) -> Tuple[str, Optional[str]]:
    """Create a simple enhancement prompt from menu metadata if available."""
    try:
        items = load_menu_items()
        for it in items:
            if it.slug == slug:
                name = it.name
                desc = (it.description or "").strip()
                system = None
                prompt = (
                    f"Enhance and stylize the food photo for '{name}' with an appetizing, modern Italian bistro look. "
                    f"Emphasize natural colors, sharp focus, and appealing plating."
                )
                if desc:
                    prompt += f" Description: {desc}"
                return prompt, system
    except Exception as e:  # noqa: BLE001
        if _LOG.isEnabledFor(logging.DEBUG):
            _LOG.debug("Failed to load menu items for prompt: %s", e)
    return (
        f"Enhance and stylize the food photo '{slug}' with appetizing presentation, sharp focus, and natural lighting.",
        None,
    )


def enhance_image(
    slug: str,
    *,
    client: Optional[MiniMaxClient] = None,
    style_preset: Optional[str] = None,
    prompt: Optional[str] = None,
    variants: int = 1,
) -> Dict[str, Any]:
    """
    High-level enhancement for a menu item slug.

    - Loads `data/{slug}.jpg|png` (or `slug-*.ext`), picks the first match
    - Calls MiniMax image generation API via MiniMaxClient
    - Saves outputs to `build/enhanced_images/{slug}_{i}.jpg`
    - Writes metadata to `build/enhanced_images/{slug}.json`

    Returns a metadata dict with fields: slug, source_image, outputs[], model, style_preset, prompt.
    Raises MiniMaxError on API failure or FileNotFoundError when no source image is found.
    """

    ensure_build_tree()
    ENHANCED_DIR.mkdir(parents=True, exist_ok=True)

    client = client or MiniMaxClient()
    use_style = style_preset or os.getenv("MINIMAX_STYLE_PRESET", "hero")

    images = find_images_for_slug(slug)
    if not images:
        raise FileNotFoundError(f"No image found for slug '{slug}' in {DATA_DIR}")
    src_image = images[0]

    use_prompt = prompt or _default_prompt_for_slug(slug)[0]

    if _LOG.isEnabledFor(logging.INFO):
        _LOG.info("Enhancing %s with style=%s variants=%s", slug, use_style, variants)

    resp = enhance_image_request(
        client=client,
        image_path=src_image,
        prompt=use_prompt,
        style_preset=use_style,
        n=max(1, int(variants)),
    )

    sources = _extract_image_sources(resp)
    if not sources:
        # If API returns a single image_base64 at top-level
        top_b64 = resp.get("image_base64") or resp.get("b64_json")
        if top_b64:
            sources = [{"b64": top_b64}]

    saved: List[str] = []
    idx = 1
    for s in sources:
        try:
            if "b64" in s:
                content = b64decode(s["b64"])  # may throw binascii.Error
            else:
                content = _download(s["url"])  # may raise on bad status
            out_path = _save_variant(slug, idx, content, ".jpg")
            saved.append(str(out_path.relative_to(BUILD_DIR.parent)))
            idx += 1
        except Exception as e:  # noqa: BLE001
            if _LOG.isEnabledFor(logging.WARNING):
                _LOG.warning("Failed to save variant %s: %s", idx, e)

    meta = {
        "slug": slug,
        "source_image": str(src_image.relative_to(BUILD_DIR.parent)),
        "model": client.config.image_model,
        "style_preset": use_style,
        "prompt": use_prompt,
        "outputs": saved,
    }
    # Store metadata alongside images
    meta_path = ENHANCED_DIR / f"{slug}.json"
    write_json(meta_path, meta)

    if _LOG.isEnabledFor(logging.INFO):
        _LOG.info("Enhanced %s -> %s file(s)", slug, len(saved))

    return meta
