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

## Current Status (Updated November 4, 2025)

### ✅ Completed
- **Menu structuring**: Converted all menu text from `data/` to structured YAML files (`menu/dinner.yaml`, `menu/lunch.yaml`) with 119 total items
- **Asset organization**: Renamed 36 existing images to slug-based format for automated matching
- **JSON export system**: Built `src/menu/export_items.py` to generate per-item JSON files under `menu/items/` with metadata, image references, and processing status
- **Validation tooling**: Created `src/tools/validate_assets.py` to check menu-image parity and report missing assets
- **Pipeline scaffolding**: Implemented `src/pipeline/run_once.py` with processed markers (`build/processed/*.done`) and manifest generation (`build/manifest.csv`)
- **Documentation**: Updated all docs to reflect MiniMax-only workflow and current architecture
- **Missing asset tracking**: Generated `MISSING_IMAGES.md` listing 83 items needing photography
- **Environment template**: Created `.env.example` with all API keys and configuration options

### 🔄 In Progress
- **Image capture**: 83 menu items still require photography (see `MISSING_IMAGES.md`)
- **MiniMax integration**: API client and enhancement pipeline not yet implemented

### 📋 Next Steps
1. **Capture missing images** (priority: dinner entrees, popular lunch items)
2. **Implement MiniMax client** (`src/minimax/client.py`) with auth and rate limiting
3. **Build enhancement pipeline** for image upscaling and video generation
4. **Google Drive sync** service for asset distribution
5. **QA workflow** and manual approval checklist

## Implementation Plan (Current Sprint)
1. **Data hygiene** ✅ COMPLETED
   - ✅ Enforce filename parity between `data/` and `menu/`.
   - ✅ Emit `build/processed/<dish>.done` markers.
   - ✅ Schema validation for menu text (YAML structure with name, description, ingredients).
   - 🔄 Move processed originals into `archive/raw_processed/` (pending MiniMax processing).
2. **MiniMax integration layer** 🔜 NEXT
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

## Repo Structure
```
data/                   # raw images (36 currently, 83 missing - see MISSING_IMAGES.md)
archive/raw_processed/  # processed originals moved here automatically
menu/
  dinner.yaml           # 79 dinner menu items with descriptions & ingredients
  lunch.yaml            # 40 lunch menu items
  items/                # 119 generated JSON files (one per menu item)
build/
  processed/            # 119 marker files (.done) documenting item status
  manifest.csv          # tracking spreadsheet: slug → image → processed status
  enhanced_images/      # MiniMax-enhanced stills (master variants) [future]
  videos/               # MiniMax-produced MP4s (master variants) [future]
  content/              # JSON + markdown SEO packs (master metadata) [future]
  platform_assets/      # platform-specific derivatives [future]
    instagram_feed/
    instagram_story/
    tiktok/
    pinterest/
    google_business/
src/
  menu/
    utils.py            # shared utilities for loading menus, finding images, writing JSON
    export_items.py     # CLI to generate per-item JSON files
  tools/
    validate_assets.py  # CLI for checking menu-image parity
  pipeline/
    run_once.py         # prototype pipeline with processed markers & manifest
  minimax/              # API client and prompt helpers [to be implemented]
docs/
  pipeline_plan.md      # detailed implementation roadmap
MISSING_IMAGES.md       # list of 83 items needing photography
.env.example            # template for all API keys and configuration
```

## Environment & Secrets
- `MINIMAX_API_KEY`: grants access to all MiniMax endpoints used in the pipeline.
- `GDRIVE_SERVICE_ACCOUNT`: service-account JSON for Drive uploads (store via Secret Manager or `.env`).
- Optional tunables: `PIPELINE_BATCH_SIZE`, `MINIMAX_STYLE_PRESET`, `VOICE_PROFILE` for flexible runs without code edits.

## Quick Start

### Prerequisites
1. Copy `.env.example` to `.env` and fill in credentials:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Common Commands
```bash
# Check menu-image parity and see missing items
python3 -m src.tools.validate_assets

# Export all menu items to JSON files
python3 -m src.menu.export_items

# Run pipeline to update processed markers and manifest
python3 -m src.pipeline.run_once

# Process specific items only
python3 -m src.pipeline.run_once --slugs grilled-chicken,caesar-salad

# Dry run (no file changes)
python3 -m src.pipeline.run_once --dry-run
```

## Next Steps for Engineers
1. **Image capture**: Source photography for 83 missing items (see `MISSING_IMAGES.md`)
2. **MiniMax client**: Scaffold `src/minimax/client.py` and add smoke tests targeting sandbox endpoints
3. **Enhancement pipeline**: Implement image upscaling, video generation, and copy creation
4. **Drive sync**: Build upload service using credentials from `.env`
5. **QA checklist**: Document manual approval workflow in `docs/qa.md`

## Quickstart

1) Install dependencies
- Python 3.11+ recommended
- `pip install -r requirements.txt`

2) Configure environment
- Copy `.env.example` to `.env` and fill in values (MiniMax API key, optional Drive/SMTP):
  - `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`
  - `RATE_LIMIT_RPM`, `MAX_RETRIES`
  - Optional: `GDRIVE_*`, `VOICE_PROFILE`, `MUSIC_VIBE`

3) Validate inputs
- Check menu ↔ image parity:
  - `python3 -m src.tools.validate_assets`
- Optionally verify generated assets for processed items:
  - `python3 -m src.tools.validate_assets --check-generated`

4) Run the orchestrator (single slug)
- End-to-end: image → content → audio → video → platform bundles
- `python -m src.pipeline.enhance --slug veal-piccata`
- Limit platforms:
  - `python -m src.pipeline.enhance --slug veal-piccata --platforms instagram_reel,tiktok`
- Upload to Drive after render (if configured):
  - `python -m src.pipeline.enhance --slug veal-piccata --sync-drive`

5) Batch processing
- Process N items with images (skips previously processed by default):
  - `python -m src.scheduler.batch_processor --limit 10`
- Upload to Drive during batch:
  - `python -m src.scheduler.batch_processor --limit 10 --sync-drive`

6) QA & Reporting
- Generate a daily QA report (+ optional notifications):
  - `python -m src.qa.reporter --email --webhook`
- Reports saved to `build/qa_reports/`

7) Drive Sync (standalone)
- Upload prepared bundles to Drive (per slug):
  - `python -m src.drive.sync --slug veal-piccata`
- Auto-discover bundles:
  - `python -m src.drive.sync`

8) Docker
- Build and run API for healthchecks:
  - `docker compose build && docker compose up -d api`
- One-shot batch via Compose:
  - `docker compose run --rm batch`

## Contributing
- Track progress with processed markers in `build/processed/`
- Update `MISSING_IMAGES.md` after adding new images
- Run validation before committing: `python3 -m src.tools.validate_assets`
- Keep prompts and brand tone consistent (open an issue before major changes)

Questions? Open an issue or check the implementation plan in `docs/pipeline_plan.md`.
