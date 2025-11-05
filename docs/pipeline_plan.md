# MiniMax Media Pipeline Plan

**Last Updated:** November 4, 2025  
**Status:** Foundation phase complete, MiniMax integration next

## Goals
- Centralize all generative tasks on MiniMax (text, image, voice, music, video).
- Produce enhanced imagery, short-form videos, and SEO copy from raw photo/menu pairs.
- Store final assets in Google Drive for manual publishing while automation remains paused.

## Current Progress

### ✅ Phase 0 - Menu Structuring (Completed Nov 4, 2025)
- Converted menu text to YAML format (`menu/dinner.yaml`, `menu/lunch.yaml`)
- 119 total items: 79 dinner, 40 lunch
- Structured schema: name, description, ingredients, category, availability
- All items have unique slugs for automated tracking

### ✅ Phase 1 - Foundations (Completed Nov 4, 2025)
1. ✅ Data/menu parity validation implemented (`src/tools/validate_assets.py`)
2. ✅ Processed marker system in place (`build/processed/*.done` with ISO timestamps)
3. ✅ Manifest tracking via `build/manifest.csv` (slug, image count, processed status)
4. ✅ Per-item JSON export system (`menu/items/*.json` with metadata)
5. ✅ 36 images renamed to slug format, 83 items still need photography (tracked in `MISSING_IMAGES.md`)
6. ⏳ `src/minimax/client.py` - NOT YET IMPLEMENTED
7. ⏳ Prompt templates - TO BE DESIGNED

**Current State:**
- All tooling ready for image capture phase
- `python3 -m src.tools.validate_assets` reports 83 missing items
- `python3 -m src.pipeline.run_once` successfully processes available items

## Inputs & Conventions
- `data/<dish>.jpg|png` — raw photo supplied by the culinary team. Once processed, the file moves to `archive/raw_processed/` so it never re-enters the queue.
- `menu/dinner.yaml` & `menu/lunch.yaml` — structured menu data where each item includes name, description, ingredients, category, and availability.
- File basenames must match slugs exactly (case-insensitive); orphaned files are flagged for review.

## Deliverables per Dish
- `build/enhanced_images/<dish>_<variant>.jpg`
- `build/videos/<dish>.mp4`
- `build/content/<dish>.json` (captions, hashtags, alt text, allergen notes)
- Platform variants under `build/platform_assets/<platform>/<dish>/` (images, videos, copy tailored to specs).
- Google Drive structure `/<platform>/<date>/<dish>/` (or Sheet tab per platform) containing the generated image, video, and associated text side-by-side to streamline future scheduling.

## Phase 2 — Asset Generation MVP (Next Sprint)

**Prerequisites:** MiniMax API key configured in `.env`, at least 20 items with images

### Tasks
1. Build MiniMax client (`src/minimax/client.py`):
   - Authentication and API key management
   - Rate limiting (60 RPM default, configurable via `RATE_LIMIT_RPM`)
   - Retry logic with exponential backoff
   - Structured error handling and logging
   
2. Implement enhancement functions:
   - `enhance_image(slug, style_preset)` → upscaled/styled variants
   - `generate_narration_script(menu_item)` → voiceover text
   - `synthesize_voice(script, voice_profile)` → audio file
   - `compose_music(vibe, duration)` → background track
   - `render_video(image, audio, music)` → final MP4
   - `write_seo_copy(menu_item, platform)` → captions, hashtags, alt text

3. Build synchronous CLI (`python -m src.pipeline.enhance --slug <name>`):
   - Load menu data and image from validated sources
   - Call MiniMax enhancement pipeline
   - Store artifacts under `build/` plus platform-specific subfolders
   - Log summary metrics and update processed markers
   
4. Add pytest smoke tests:
   - Mock MiniMax responses using fixtures or VCR
   - Validate output file structure and metadata
   - Test error handling and retry logic

**Deliverables:**
- ✅ Working MiniMax client with all helper functions
- ✅ End-to-end processing for at least 5 sample dishes
- ✅ Test coverage ≥80% for new code
- ✅ Documentation in `docs/minimax_api.md`

## Phase 3 — Automation & Storage (Future Sprint)

**Prerequisites:** Phase 2 complete, Google Drive service account configured

### Tasks
1. Scheduling layer:
   - Set up Celery beat or cron job to process new items nightly
   - Queue system for batch processing (default: 10 items per run)
   - Configurable via `PIPELINE_BATCH_SIZE` environment variable
   
2. Google Drive integration (`src/drive/sync.py`):
   - Authenticate using service account credentials from `.env`
   - Upload platform-specific bundles to organized folder structure
   - Generate shareable links for each asset
   - Update `build/drive_manifest.json` with links and metadata
   
3. QA reporting:
   - Generate daily report: items processed, allergens detected, review checklist
   - Email notifications using SMTP settings from `.env`
   - Slack/Discord webhooks for team alerts (optional)
   
4. Archive management:
   - Move processed raw images to `archive/raw_processed/`
   - Cleanup old build artifacts (configurable retention policy)
   - Version control for re-processed items

**Deliverables:**
- ✅ Automated nightly processing
- ✅ All assets synced to Google Drive with shareable links
- ✅ Daily QA reports delivered to team
- ✅ Archive workflow prevents duplicate processing

## Deferred Items
- **Social posting automation**: Re-enable Make.com webhooks and platform APIs once marketing team approves automated asset quality
- **External models**: Integrate Kling, Seedream, Qwen, etc., only if MiniMax coverage gaps are identified
- **Analytics feedback**: Add performance tracking after manual posting resumes
- **A/B testing**: Variant testing for captions, thumbnails, posting times
- **Toast POS sync**: Auto-pull menu updates from Toast API

## Open Questions & Decisions Needed
- ✅ **RESOLVED:** Menu structure → YAML with structured schema
- ✅ **RESOLVED:** Asset tracking → Processed markers + manifest.csv
- ⏳ **Standard voice persona for narration?** → To be decided during MiniMax integration
- ⏳ **Preferred Drive folder naming?** → Current plan: `/<platform>/<YYYY-MM-DD>/<dish>/`
- ⏳ **Target turnaround time per batch?** → Will determine rate-limit strategy

## Dependencies & Prerequisites

### Phase 2 (Next)
- [ ] MiniMax API key obtained
- [ ] `.env` file configured with `MINIMAX_API_KEY`
- [ ] At least 20-30 menu items with images for testing
- [ ] Python dependencies: `requests`, `pytest`, `python-dotenv`

### Phase 3 (Future)
- [ ] Google Drive service account created
- [ ] Drive folder structure set up
- [ ] SMTP credentials for email notifications
- [ ] Celery worker infrastructure (Redis or RabbitMQ)

## Monitoring & Success Metrics

### Phase 2 Targets
- Successfully enhance 100% of items with images
- Average processing time < 2 minutes per item
- Zero failed API calls (after retries)
- All outputs pass validation checks

### Phase 3 Targets  
- 100% of generated assets synced to Drive within 1 hour
- Daily QA report delivery 99%+ uptime
- Zero duplicate processing of raw images
- Manual review completion < 24 hours

## Risk Mitigation
- **API rate limits:** Configurable throttling, queue backoff
- **API quota exhaustion:** Monitor usage, alert at 80% threshold
- **Image quality issues:** Manual QA before Drive sync
- **Missing dependencies:** Pre-flight checks in pipeline scripts
- **Data loss:** Automated backups of `build/` directory
