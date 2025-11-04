# MiniMax Media Pipeline Plan

## Goals
- Centralize all generative tasks on MiniMax (text, image, voice, music, video).
- Produce enhanced imagery, short-form videos, and SEO copy from raw photo/menu pairs.
- Store final assets in Google Drive for manual publishing while automation remains paused.

## Inputs & Conventions
- `data/<dish>.jpg|png` — raw photo supplied by the culinary team. Once processed, the file moves to `archive/raw_processed/` so it never re-enters the queue.
- `menu/<dish>.txt` — menu description where the first line is the display name and the remaining lines list ingredients or tasting notes.
- File basenames must match exactly (case-insensitive); orphaned files are flagged for review.

## Deliverables per Dish
- `build/enhanced_images/<dish>_<variant>.jpg`
- `build/videos/<dish>.mp4`
- `build/content/<dish>.json` (captions, hashtags, alt text, allergen notes)
- Platform variants under `build/platform_assets/<platform>/<dish>/` (images, videos, copy tailored to specs).
- Google Drive structure `/<platform>/<date>/<dish>/` (or Sheet tab per platform) containing the generated image, video, and associated text side-by-side to streamline future scheduling.

## Phase 1 — Foundations
1. Validate data/menu parity and emit a report of missing counterparts; move processed originals into `archive/raw_processed/` and drop marker files in `build/processed/`.
2. Implement `src/minimax/client.py` with retries, rate limiting, and structured error handling.
3. Draft prompt templates for:
   - Image enhancement style presets (hero shot, overhead, ambiance).
   - Copy generation (SEO caption, alt text, review snippet).
   - Voiceover tone and background music vibe.

## Phase 2 — Asset Generation MVP
1. Build a synchronous CLI (`python -m src.pipeline.run_once --dish <name>`):
   - Load menu text + image.
   - Call MiniMax image enhancement.
   - Generate narration script + voiceover audio.
   - Ask MiniMax to compose background music and stitch video output.
   - Produce SEO copy JSON bundle.
2. Store artifacts under `build/` plus platform-specific subfolders and log summary metrics.
3. Add pytest smoke tests using recorded MiniMax responses (VCR or fixtures).

## Phase 3 — Automation & Storage
1. Introduce a scheduling layer (Celery beat or cron) to process new dish assets nightly.
2. Package results and upload to Google Drive using service-account credentials.
3. Write a manifest (`build/manifest.json`) capturing per-platform share links and metadata for each run.
4. Generate daily QA report outlining generated assets, detected allergens, and manual review checklist.

## Deferred Items
- Re-enable social posting (Make.com webhooks) once the marketing team approves automated asset quality.
- Integrate external models only if MiniMax coverage gaps are identified.
- Add analytics feedback loop after manual posting resumes.

## Open Questions
- Standard voice persona for narration?
- Preferred Drive folder naming beyond `Assets/<date>/<dish>/`?
- Target turnaround time per batch (impacts rate-limit strategy)?
