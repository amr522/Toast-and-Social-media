from __future__ import annotations

from pathlib import Path

import src.pipeline.enhance as orch
import src.minimax.image as image_module
import src.minimax.content as content_module
import src.minimax.audio as audio_module
import src.minimax.video as video_module
import src.menu.utils as utils


def test_orchestrator_end_to_end_stubbed(tmp_path, monkeypatch):
    # Setup paths
    build = tmp_path / "build"
    data = tmp_path / "data"
    build.mkdir(parents=True)
    data.mkdir(parents=True)
    monkeypatch.setattr(utils, "BUILD_DIR", build)
    monkeypatch.setattr(utils, "DATA_DIR", data)
    # Also patch orchestrator's cached paths
    monkeypatch.setattr(orch, "BUILD_DIR", build)
    monkeypatch.setattr(orch, "PLATFORM_ASSETS_DIR", build / "platform_assets")

    slug = "test-dish"
    (data / f"{slug}.jpg").write_bytes(b"RAW")

    # Stub image enhancement to produce an enhanced image
    def fake_enhance_image(s, **k):  # type: ignore[no-untyped-def]
        out_dir = build / "enhanced_images"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s}_1.jpg").write_bytes(b"IMG")
        return {"outputs": [str((out_dir / f"{s}_1.jpg").relative_to(build.parent))]}

    # Patch both module and orchestrator references
    monkeypatch.setattr(image_module, "enhance_image", fake_enhance_image)
    monkeypatch.setattr(orch, "enhance_image", fake_enhance_image)

    # Stub content generation
    def fake_script(s, **k):  # type: ignore[no-untyped-def]
        out_dir = build / "content"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s}.json").write_text("{\"narration_script\": \"Welcome\"}", encoding="utf-8")
        return {"path": str(out_dir / f"{s}.json")}

    def fake_copy(s, **k):  # type: ignore[no-untyped-def]
        out_dir = build / "content"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s}.json").write_text("{\"platforms\": {\"instagram_feed\": {\"caption\": \"Hi\"}}}", encoding="utf-8")
        return {"path": str(out_dir / f"{s}.json")}

    monkeypatch.setattr(content_module, "generate_narration_script", fake_script)
    monkeypatch.setattr(content_module, "write_seo_copy", fake_copy)
    monkeypatch.setattr(orch, "generate_narration_script", fake_script)
    monkeypatch.setattr(orch, "write_seo_copy", fake_copy)

    # Stub audio
    def fake_tts(s, **k):  # type: ignore[no-untyped-def]
        out_dir = build / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s}_voice.mp3").write_bytes(b"VOICE")
        return {}

    def fake_music(s, **k):  # type: ignore[no-untyped-def]
        out_dir = build / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s}_music.mp3").write_bytes(b"MUSIC")
        return {}

    monkeypatch.setattr(audio_module, "synthesize_voice_for_slug", fake_tts)
    monkeypatch.setattr(audio_module, "compose_music_for_slug", fake_music)
    monkeypatch.setattr(orch, "synthesize_voice_for_slug", fake_tts)
    monkeypatch.setattr(orch, "compose_music_for_slug", fake_music)

    # Stub video
    def fake_video(s, **k):  # type: ignore[no-untyped-def]
        out_dir = build / "videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s}.mp4").write_bytes(b"VIDEO")
        (out_dir / f"{s}.json").write_text("{}", encoding="utf-8")
        return {}

    monkeypatch.setattr(video_module, "render_video_for_slug", fake_video)
    monkeypatch.setattr(orch, "render_video_for_slug", fake_video)

    # Run orchestrator
    statuses = orch.orchestrate_enhancement(slug, platforms=["instagram_feed"]) 
    assert statuses.get("image") == "ok"
    assert statuses.get("content") == "ok"
    assert statuses.get("audio") == "ok"
    assert statuses.get("video") == "ok"

    # Check platform bundle copy
    bundle = build / "platform_assets" / "instagram_feed" / slug
    assert (bundle / "image.jpg").exists()
    assert (bundle / "video.mp4").exists()
    assert (bundle / "content.json").exists()
