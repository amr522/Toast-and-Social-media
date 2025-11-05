from __future__ import annotations

from src.platforms.specs import PLATFORM_SPECS


def test_platforms_have_20s_target_and_aspect_ratio():
    assert PLATFORM_SPECS, "No platform specs defined"
    for name, spec in PLATFORM_SPECS.items():
        assert "aspect_ratio" in spec and isinstance(spec["aspect_ratio"], str)
        assert spec.get("video_duration_sec_target") == 20

