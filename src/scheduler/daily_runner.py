from __future__ import annotations

import argparse
import os
from datetime import datetime

from src.scheduler.batch_processor import discover_candidates, process_batch
from src.qa.reporter import generate_daily_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily scheduled runner for MiniMax pipeline")
    parser.add_argument("--limit", type=int, default=int(os.getenv("PIPELINE_BATCH_SIZE", "10")))
    parser.add_argument("--sync-drive", action="store_true", help="Upload platform bundles after processing")
    args = parser.parse_args()

    candidates = discover_candidates(args.limit)
    if not candidates:
        print("[daily] No candidates with images to process today.")
        return

    print(f"[daily] {datetime.utcnow().isoformat()}Z processing {len(candidates)} items")
    result = process_batch(candidates, sync_drive=args.sync_drive)
    print(f"[daily] Done: {len(result.succeeded)} ok / {len(result.failed)} failed")
    # Generate QA report and notify if configured
    try:
        generate_daily_report(email=True, webhook=True)
    except Exception:
        pass


if __name__ == "__main__":
    main()
