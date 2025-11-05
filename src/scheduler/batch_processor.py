from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from src.menu.utils import BUILD_DIR, PROCESSED_DIR, find_images_for_slug, load_menu_items
from src.pipeline.enhance import orchestrate_enhancement
from src.notifications.email import send_email


@dataclass
class BatchResult:
    started_at: str
    finished_at: str
    batch_size: int
    attempted: List[str]
    succeeded: List[str]
    failed: Dict[str, str]
    durations_sec: Dict[str, float]


def discover_candidates(limit: int, *, include_processed: bool = False) -> List[str]:
    items = load_menu_items()
    processed = {p.stem for p in PROCESSED_DIR.glob("*.done")}
    candidates: List[str] = []
    for it in items:
        if not find_images_for_slug(it.slug):
            continue
        if not include_processed and it.slug in processed:
            continue
        candidates.append(it.slug)
        if len(candidates) >= limit:
            break
    return candidates


def _report_path(now: Optional[datetime] = None) -> Path:
    now = now or datetime.utcnow()
    d = BUILD_DIR / "batch_reports"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"batch_{now.strftime('%Y%m%d_%H%M%S')}.json"


def process_batch(
    slugs: Iterable[str],
    *,
    platforms: Optional[List[str]] = None,
    sync_drive: bool = False,
) -> BatchResult:
    started = datetime.utcnow()
    attempted: List[str] = []
    succeeded: List[str] = []
    failed: Dict[str, str] = {}
    durations: Dict[str, float] = {}

    for slug in slugs:
        attempted.append(slug)
        t0 = time.time()
        try:
            statuses = orchestrate_enhancement(slug, platforms=platforms, sync_drive=sync_drive)
            if any(str(v).startswith("error") for v in statuses.values()):
                failed[slug] = json.dumps(statuses)
            else:
                succeeded.append(slug)
        except Exception as e:  # noqa: BLE001
            failed[slug] = str(e)
        finally:
            durations[slug] = round(time.time() - t0, 2)

    finished = datetime.utcnow()
    result = BatchResult(
        started_at=started.isoformat() + "Z",
        finished_at=finished.isoformat() + "Z",
        batch_size=len(list(slugs)),
        attempted=attempted,
        succeeded=succeeded,
        failed=failed,
        durations_sec=durations,
    )

    # Write report
    report_path = _report_path(finished)
    report_path.write_text(json.dumps(result.__dict__, indent=2) + "\n", encoding="utf-8")

    # Optional email
    subject = f"MiniMax Batch: {len(succeeded)} ok, {len(failed)} failed"
    body = (
        f"Started: {result.started_at}\nFinished: {result.finished_at}\n"
        f"Attempted: {len(attempted)}\nSucceeded: {len(succeeded)}\nFailed: {len(failed)}\n"
    )
    try:
        send_email(subject, body)
    except Exception:
        pass

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Process a batch of items through the MiniMax pipeline")
    parser.add_argument("--limit", type=int, default=int(os.getenv("PIPELINE_BATCH_SIZE", "10")), help="Max items to process")
    parser.add_argument("--slugs", nargs="*", help="Explicit slugs to process (overrides discovery)")
    parser.add_argument("--platforms", help="Comma-separated platforms to target")
    parser.add_argument("--reprocess", action="store_true", help="Include already processed items")
    parser.add_argument("--sync-drive", action="store_true", help="Upload platform bundles to Drive")
    args = parser.parse_args()

    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    else:
        platforms = None

    if args.slugs:
        target = args.slugs[: args.limit]
    else:
        target = discover_candidates(args.limit, include_processed=args.reprocess)
    if not target:
        print("No candidates found.")
        raise SystemExit(0)

    result = process_batch(target, platforms=platforms, sync_drive=args.sync_drive)
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()

