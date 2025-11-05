from __future__ import annotations

import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
MENU_ITEMS = ROOT / "menu" / "items"
BACKUPS = ROOT / "infra" / "backup" / "backups"


def create_tarball(out_dir: Path, name: Optional[str] = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = name or f"backup_{ts}.tar.gz"
    out_path = out_dir / name
    with tarfile.open(out_path, "w:gz") as tar:
        if BUILD.exists():
            tar.add(BUILD, arcname="build")
        if MENU_ITEMS.exists():
            tar.add(MENU_ITEMS, arcname="menu_items")
    return out_path


def maybe_upload_s3(path: Path) -> None:
    bucket = os.getenv("BACKUP_S3_BUCKET")
    if not bucket:
        return
    try:
        import boto3

        s3 = boto3.client("s3")
        key = f"minimax-pipeline/{path.name}"
        s3.upload_file(str(path), bucket, key)
        print(f"Uploaded {path.name} to s3://{bucket}/{key}")
    except Exception as e:  # noqa: BLE001
        print(f"S3 upload failed: {e}")


def main() -> None:
    tar = create_tarball(BACKUPS)
    print(f"Created backup: {tar}")
    maybe_upload_s3(tar)


if __name__ == "__main__":
    main()

