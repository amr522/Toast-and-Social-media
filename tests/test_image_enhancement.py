from __future__ import annotations

import base64
from pathlib import Path

import src.minimax.image as image_module
from src.minimax.image import enhance_image
import src.menu.utils as utils


def test_enhance_image_saves_variants(tmp_path, monkeypatch):
    # Arrange directories
    data_dir = tmp_path / "data"
    build_dir = tmp_path / "build"
    data_dir.mkdir(parents=True)
    build_dir.mkdir(parents=True)

    # Monkeypatch module constants
    monkeypatch.setattr(utils, "DATA_DIR", data_dir)
    monkeypatch.setattr(utils, "BUILD_DIR", build_dir)
    monkeypatch.setattr(image_module, "ENHANCED_DIR", build_dir / "enhanced_images")
    monkeypatch.setattr(image_module, "BUILD_DIR", build_dir)

    # Create a dummy source image
    slug = "test-dish"
    (data_dir / f"{slug}.jpg").write_bytes(b"RAWIMG")

    # Stub the low-level API call to return base64 image
    b64 = base64.b64encode(b"ENHANCED").decode("ascii")
    monkeypatch.setattr(image_module, "enhance_image_request", lambda **kwargs: {"base_resp": {"status_code": 0}, "b64_json": b64})

    meta = enhance_image(slug, variants=1)

    out_file = build_dir / "enhanced_images" / f"{slug}_1.jpg"
    assert out_file.exists() and out_file.read_bytes() == b"ENHANCED"
    # Metadata JSON
    meta_path = build_dir / "enhanced_images" / f"{slug}.json"
    assert meta_path.exists()
