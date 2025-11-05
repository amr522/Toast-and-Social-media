# MiniMax API Integration Guide

## Overview

This document outlines the MiniMax API endpoints and models used for the Toast & Social Media pipeline. All generative tasks are centralized on MiniMax's unified platform covering text, image, voice, music, and video generation.

## API Endpoints & Models

Note: In this project, all endpoint paths and model IDs are read from `.env` (see MINIMAX_BASE_URL and MINIMAX_*_MODEL variables). Values below are the defaults used if not overridden.

### 1. Text Generation (MiniMax-M2)
**Use Case:** Generate narration scripts, SEO copy, captions, hashtags, alt text
**API:** Chat completions (Anthropic-compatible schema)
**Models:** `MiniMax-M2`, `MiniMax-M2-Stable`
**Endpoint:** `https://api.minimax.io/v1/text/chat/completions`
**Rate Limit:** Not specified in docs
**Key Features:**
- 204,800 token context window
- Tool calling and function calling support
- Interleaved thinking capabilities

### 2. Image Generation (Text-to-Image)
**Use Case:** Enhance and style food photography
**API:** POST `/v1/image_generation`
**Model:** `image-01`
**Endpoint:** `https://api.minimax.io/v1/image_generation`
**Rate Limit:** Not specified
**Key Features:**
- Multiple aspect ratios (1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9)
- Resolution up to 2048x2048 (must be divisible by 8)
- Batch generation (up to 9 images per request)
- Prompt optimization available
- Response formats: URL (24h expiry) or base64

### 3. Speech Synthesis (T2A)
**Use Case:** Convert narration scripts to audio
**API:** POST `/v1/t2a_v2`
**Models:** `speech-2.6-hd`, `speech-2.6-turbo`, `speech-02-hd`, `speech-02-turbo`, `speech-01-hd`, `speech-01-turbo`
**Endpoint:** `https://api.minimax.io/v1/t2a_v2`
**Rate Limit:** Not specified
**Key Features:**
- 300+ system voices and custom cloned voices
- 40+ supported languages
- Streaming and non-streaming output
- Adjustable speed, pitch, volume
- Multiple audio formats (MP3, WAV, FLAC, PCM)
- Subtitle generation support
- Up to 10,000 characters per request

### 4. Music Generation
**Use Case:** Create background music for videos
**API:** POST `/v1/music_generation`
**Model:** `music-2.0`
**Endpoint:** `https://api.minimax.io/v1/music_generation`
**Rate Limit:** Not specified
**Key Features:**
- Lyrics-based song generation
- Style and mood specification
- Structured lyrics with tags ([Verse], [Chorus], etc.)
- Streaming output support
- Audio formats: MP3, etc.
- Lyrics: 10-3000 characters
- Prompt: 10-2000 characters describing style/mood

### 5. Video Generation (Text-to-Video)
**Use Case:** Create short-form videos from images and audio
**API:** POST `/v1/video_generation`
**Models:** `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-02`, `T2V-01-Director`, `T2V-01`
**Endpoint:** `https://api.minimax.io/v1/video_generation`
**Rate Limit:** Not specified
**Key Features:**
- Camera movement control with [command] syntax
- Multiple durations (6 or 10 seconds depending on model)
- Resolutions: 720P, 768P, 1080P
- Asynchronous processing with task IDs
- Callback URL support for status updates
- Prompt optimization available

## Authentication

All endpoints use Bearer token authentication:
```
Authorization: Bearer <MINIMAX_API_KEY>
Content-Type: application/json
```

API keys can be obtained from [MiniMax Account Management](https://platform.minimax.io/user-center/basic-information/interface-key).

## Function Mappings

| Pipeline Function | MiniMax API | Model | Endpoint |
|-------------------|-------------|-------|----------|
| `enhance_image()` | Image Generation | `image-01` | `/v1/image_generation` |
| `generate_narration_script()` | Text Generation | `MiniMax-M2` | Anthropic-compatible |
| `synthesize_voice()` | T2A Speech | `speech-2.6-hd` | `/v1/t2a_v2` |
| `compose_music()` | Music Generation | `music-2.0` | `/v1/music_generation` |
| `render_video()` | Video Generation | `MiniMax-Hailuo-2.3` | `/v1/video_generation` |
| `write_seo_copy()` | Text Generation | `MiniMax-M2` | Anthropic-compatible |

## Rate Limiting & Best Practices

- Implement exponential backoff for retries
- Monitor API usage and set up alerts at 80% quota
- Use streaming where available for large responses
- Cache successful generations to avoid duplicate API calls
- Configure `RATE_LIMIT_RPM` environment variable (default: 60)

## Error Handling

All APIs return structured error responses:
```json
{
  "base_resp": {
    "status_code": <error_code>,
    "status_msg": "<error_description>"
  }
}
```

Common status codes:
- `0`: Success
- Non-zero: Various error conditions

## Dependencies

```python
# requirements.txt additions
requests>=2.31.0
anthropic>=0.7.0  # For text generation
pytest>=7.0.0     # For testing
python-dotenv>=1.0.0
```

## Testing Strategy

- Use VCR.py or similar for API response mocking
- Test all endpoints with sample data
- Validate output formats and file structures
- Test error handling and retry logic
- Aim for ≥80% test coverage

## Configuration

Add to `.env`:
```
MINIMAX_API_KEY=your_api_key_here
RATE_LIMIT_RPM=60
MINIMAX_BASE_URL=https://api.minimax.io
```

## Next Steps

1. Obtain MiniMax API key
2. Implement client wrapper in `src/minimax/client.py`
3. Create prompt templates for each modality
4. Build integration tests with mock responses
5. Test end-to-end pipeline with sample data

---

*Last Updated: November 4, 2025*
*API Version: Latest available*
*Documentation: https://platform.minimax.io/docs*</content>
<parameter name="filePath">/Users/Heidak/Downloads/Toast-and-Social-media-main/docs/minimax_api.md
