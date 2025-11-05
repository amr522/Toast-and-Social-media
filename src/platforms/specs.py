from __future__ import annotations

# Platform specifications used for rendering/video duration and caption guidance.

PLATFORM_SPECS = {
    # Instagram
    "instagram_feed": {
        "aspect_ratio": "1:1",
        "resolution": (1080, 1080),
        "video_duration_sec_target": 20,
        "caption_recommended_chars": 125,
        "caption_max_chars": 2200,
    },
    "instagram_reel": {
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "video_duration_sec_target": 20,
        "caption_recommended_chars": 150,
        "caption_max_chars": 2200,
    },
    # TikTok
    "tiktok": {
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "video_duration_sec_target": 20,
        "caption_recommended_chars": 150,
        "caption_max_chars": 2200,
    },
    # Pinterest
    "pinterest": {
        "aspect_ratio": "2:3",
        "resolution": (1000, 1500),
        "video_duration_sec_target": 20,
        "caption_recommended_chars": 100,
        "caption_max_chars": 500,
    },
    # Facebook (square as a safe default for feed)
    "facebook": {
        "aspect_ratio": "1:1",
        "resolution": (1080, 1080),
        "video_duration_sec_target": 20,
        "caption_recommended_chars": 125,
        "caption_max_chars": 63206,
    },
}

