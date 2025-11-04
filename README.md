# Minimax-Centric Media Prep Pipeline — 41 Bistro

## Purpose
This repository documents a lean content-preparation workflow where **MiniMax** is the sole multi-modal provider. MiniMax handles image enhancement, video generation, narration, music, and SEO copy while automated posting remains paused until the asset library is complete.

## Source Inputs
- `data/`: raw food and ambiance images (JPEG/PNG). After processing, each file moves to `archive/raw_processed/` so the pipeline never ingests the same photo twice.
- `menu/`: text snippets whose filenames match the images (e.g., `bruschetta.txt` pairs with `bruschetta.jpg`). Each file starts with a menu headline followed by ingredient bullets or tasting notes.
- File basenames must match case-insensitively; orphaned files are flagged for manual review.

## Target Outputs
1. **Enhanced imagery** stored under `build/enhanced_images/` (master variants) and platform-optimized versions under `build/platform_assets/<platform>/images/`.
2. **Short-form videos** rendered by MiniMax, archived under `build/videos/` (master cuts) and `build/platform_assets/<platform>/videos/` for platform-specific timing/aspect ratios.
3. **SEO content packs** in `build/content/` (master metadata) plus per-platform copies in `build/platform_assets/<platform>/content/` containing captions, hashtags, alt text, and allergen notes.
4. **Google Drive bundles** organized by platform: `Drive/41-Bistro/<platform>/<YYYY-MM-DD>/<dish>/` (or the matching Sheet tab) with the generated image, video, and copy side-by-side to streamline future scheduling.

## MiniMax Capability Map
| Capability | MiniMax Product | Usage in Pipeline |
|------------|-----------------|-------------------|
| Text       | MiniMax Chat API | SEO copy, metadata manifests, voiceover scripts |
| Image      | MiniMax Vision/Image | Upscaling, brand stylization, plate cleanup |
| Voice      | MiniMax TTS | Narration for generated videos |
| Music      | MiniMax Music | Ambient background tracks |
| Video      | MiniMax Video | Motion assets built from enhanced stills and narration |

## High-Level Flow
1. **Ingest**: monitor `data/` and `menu/` for new pairs, validate filename parity, and ensure menu text meets schema requirements.
2. **Enhance image**: call MiniMax Image to produce multiple styled variants; store masters and platform-specific crops. Move the raw file to `archive/raw_processed/` immediately after successful enhancement.
3. **Generate media**: ask MiniMax to craft narration scripts, synthesize voiceovers, compose background music, and produce short-form videos.
4. **Author copy**: prompt MiniMax Chat for SEO captions, hashtags, and alt text tailored to each social platform.
5. **Package & QA**: build platform-specific bundles, append metadata (dish, allergens, platform, timestamps), create `build/processed/<dish>.done` markers, and verify no files remain in `data/` without matching outputs.
6. **Sync to Drive**: upload each platform bundle to its corresponding Drive folder or Sheet tab so the marketing team can stage manual posts.

## Implementation Plan (Current Sprint)
1. **Data hygiene**
   - Enforce filename parity between `data/` and `menu/`.
   - Move processed originals into `archive/raw_processed/` and emit `build/processed/<dish>.done` markers.
   - Add schema validation for menu text (name, blurb, ingredient list).
2. **MiniMax integration layer**
   - Wrap MiniMax auth, retries, and rate limiting in `src/minimax/client.py`.
   - Implement helpers: `enhance_image`, `render_video`, `generate_voiceover`, `compose_music`, `write_copy`.
3. **Asset pipeline service**
   - Build a Celery task or cron job that scans for new dish pairs and runs the end-to-end flow.
   - Persist intermediate artifacts under `build/` with deterministic names, including per-platform derivatives.
4. **Google Drive sync**
   - Use a Drive service account to upload packaged bundles and write share links to a manifest JSON.
   - Mirror per-platform folder structure or update dedicated Sheet tabs.
5. **QA & governance**
   - Generate a summary report per batch (ingredients, allergens, caption review status).
   - Maintain a manual approval checklist since posting stays disabled.

## Deferred Features
- **Social platform posting**: Automatic publishing (e.g., Make.com webhooks) remains paused until the marketing team signs off on asset quality.
- **External model mix**: Kling, Seedream, Qwen, etc., are out-of-scope unless MiniMax coverage gaps emerge.

## Repo Structure Highlights
```
data/                   # raw images awaiting processing
archive/raw_processed/  # processed originals moved here automatically
menu/                   # text descriptions matching image filenames
build/
  processed/            # marker files documenting completed dishes
  enhanced_images/      # MiniMax-enhanced stills (master variants)
  videos/               # MiniMax-produced MP4s (master variants)
  content/              # JSON + markdown SEO packs (master metadata)
  platform_assets/
    instagram_feed/
    instagram_story/
    tiktok/
    pinterest/
    google_business/
    ...                 # each platform gets tailored images/videos/copy
src/
  minimax/              # API client and prompt helpers (to be implemented)
  pipeline/             # Task orchestrators and Drive sync logic
```

## Environment & Secrets
- `MINIMAX_API_KEY`: grants access to all MiniMax endpoints used in the pipeline.
- `GDRIVE_SERVICE_ACCOUNT`: service-account JSON for Drive uploads (store via Secret Manager or `.env`).
- Optional tunables: `PIPELINE_BATCH_SIZE`, `MINIMAX_STYLE_PRESET`, `VOICE_PROFILE` for flexible runs without code edits.

## Next Steps for Engineers
1. Scaffold the MiniMax client and add smoke tests targeting sandbox endpoints.
2. Design the artifact manifest schema (`build/content/<dish>.json`) with per-platform metadata.
3. Implement a CLI entry point `python -m src.pipeline.run_once --dish <name>` for ad-hoc processing.
4. Document the manual QA checklist in `docs/qa.md` (future task).

Questions? Open an issue before adjusting prompts to keep brand tone consistent.
