# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### To Do
- Implement MiniMax API client (`src/minimax/client.py`)
- Build image enhancement pipeline
- Integrate video generation workflow
- Set up Google Drive synchronization
- Capture photography for 83 missing menu items

## [0.2.0] - 2024-11-04

### Added
- **Menu structuring system**
  - Created `menu/dinner.yaml` with 79 dinner items
  - Created `menu/lunch.yaml` with 40 lunch items
  - Structured schema: name, description, ingredients, category, availability, dietary tags
  - Added Pork Osso Buco to dinner menu

- **Asset tracking and validation**
  - Built `src/tools/validate_assets.py` for menu-image parity checking
  - Created `MISSING_IMAGES.md` listing 83 items needing photography
  - Renamed 36 existing images to slug-based format

- **JSON export system**
  - Implemented `src/menu/export_items.py` to generate per-item JSON files
  - Generated 119 JSON files under `menu/items/` with metadata and status
  - JSON schema includes: name, description, ingredients, images, processed timestamp

- **Pipeline infrastructure**
  - Built `src/pipeline/run_once.py` with processed markers and manifest generation
  - Created `build/processed/*.done` marker system with ISO timestamps
  - Generated `build/manifest.csv` for tracking asset status
  - Added support for slug filtering and dry-run mode

- **Shared utilities**
  - Created `src/menu/utils.py` with common functions:
    - `load_menu_items()` - Load and parse YAML menus
    - `find_images_for_slug()` - Locate matching image files
    - `marker_path()` - Manage processed markers
    - `write_json()` - Consistent JSON output formatting

- **Documentation**
  - Created `.env.example` with comprehensive API key templates
  - Updated `README.md` with current status, quick start guide, and repo structure
  - Enhanced `docs/pipeline_plan.md` with phase tracking and detailed roadmap
  - Added `CHANGELOG.md` to track version history

- **Dependencies**
  - Added `PyYAML>=6.0.1` to `requirements.txt` for menu parsing

### Changed
- Restructured documentation to reflect MiniMax-only workflow
- Updated README with progress tracking and next steps
- Enhanced pipeline plan with completed/in-progress phase markers
- Improved asset organization with clearer directory structure

### Fixed
- Corrected `ROOT_DIR` path calculation in utilities to handle package layout
- Fixed marker timestamp formatting to use ISO 8601 standard
- Removed accidental footer text from `utils.py`

## [0.1.0] - 2024-11-03

### Added
- Initial repository setup
- Git initialization and GitHub remote configuration
- Basic project structure with `src/`, `data/`, `build/` directories
- Initial `README.md` and `docs/pipeline_plan.md`
- Toast POS integration scaffolding (`src/toast/sync.py`)
- Database models (`src/db/models.py`)
- Email worker templates (`src/emailer/`)
- Make.com integration publisher (`src/make_integration/publisher.py`)
- Job scheduler handlers (`src/jobs/scheduler_handlers.py`)

### Documentation
- Created initial README with MiniMax strategy
- Documented Google Drive folder structure
- Outlined deferred features (auto-posting, external models)
- Established coding standards and contribution guidelines

---

## Version History Summary

- **0.2.0** (Nov 4, 2024): Menu structuring, asset validation, pipeline scaffolding
- **0.1.0** (Nov 3, 2024): Initial repository setup and architecture planning

---

## Navigation
- [Unreleased](#unreleased) - Planned features
- [0.2.0](#020---2024-11-04) - Current release
- [0.1.0](#010---2024-11-03) - Initial release
