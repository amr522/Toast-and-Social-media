from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from src.menu.utils import BUILD_DIR


try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except Exception as e:  # noqa: BLE001
    service_account = None  # type: ignore[assignment]
    build = None  # type: ignore[assignment]
    MediaFileUpload = None  # type: ignore[assignment]
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None


SCOPES = ["https://www.googleapis.com/auth/drive.file"]


@dataclass
class DriveConfig:
    root_folder_id: Optional[str]
    platform_folder_ids: Dict[str, str]
    rate_limit_rps: float


def _load_config() -> DriveConfig:
    platform_folder_ids = {}
    # Map both instagram_feed/reel to a single Instagram folder id if provided
    if os.getenv("GDRIVE_INSTAGRAM_FOLDER_ID"):
        platform_folder_ids["instagram_feed"] = os.getenv("GDRIVE_INSTAGRAM_FOLDER_ID", "")
        platform_folder_ids["instagram_reel"] = os.getenv("GDRIVE_INSTAGRAM_FOLDER_ID", "")
    if os.getenv("GDRIVE_TIKTOK_FOLDER_ID"):
        platform_folder_ids["tiktok"] = os.getenv("GDRIVE_TIKTOK_FOLDER_ID", "")
    if os.getenv("GDRIVE_PINTEREST_FOLDER_ID"):
        platform_folder_ids["pinterest"] = os.getenv("GDRIVE_PINTEREST_FOLDER_ID", "")

    root = os.getenv("GDRIVE_ROOT_FOLDER_ID") or None
    rps = float(os.getenv("GDRIVE_RATE_LIMIT_RPS", "2"))  # default 2 req/sec
    return DriveConfig(root_folder_id=root, platform_folder_ids=platform_folder_ids, rate_limit_rps=rps)


def _sleep_for_ratelimit(cfg: DriveConfig):
    if cfg.rate_limit_rps <= 0:
        return
    time.sleep(1.0 / cfg.rate_limit_rps)


def get_service():  # -> Resource
    """Authenticate a Drive v3 service using a service account.

    Supports either GDRIVE_SERVICE_ACCOUNT_FILE (path) or GDRIVE_SERVICE_ACCOUNT_JSON (json string).
    """
    if _IMPORT_ERROR is not None:
        raise RuntimeError(
            "google-api-python-client is required. Add google-api-python-client and google-auth to requirements.txt"
        ) from _IMPORT_ERROR

    creds_json = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")
    creds_file = os.getenv("GDRIVE_SERVICE_ACCOUNT_FILE")
    if creds_json:
        info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    elif creds_file:
        creds = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    else:
        raise RuntimeError("Missing GDRIVE_SERVICE_ACCOUNT_FILE or GDRIVE_SERVICE_ACCOUNT_JSON")
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _query_folder(service, name: str, parent_id: Optional[str]) -> Optional[str]:
    q = ["mimeType='application/vnd.google-apps.folder'", "trashed=false", f"name='{name.replace("'", "\\'")}'"]
    if parent_id:
        q.append(f"'{parent_id}' in parents")
    _sleep_for_ratelimit(_load_config())
    res = service.files().list(q=" and ".join(q), fields="files(id,name)", pageSize=1).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def _create_folder(service, name: str, parent_id: Optional[str]) -> str:
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        meta["parents"] = [parent_id]
    _sleep_for_ratelimit(_load_config())
    f = service.files().create(body=meta, fields="id").execute()
    return f["id"]


def ensure_path(service, parts: List[str], root_id: Optional[str]) -> str:
    """Ensure a path of folders exists under root and return the last folder id."""
    parent = root_id
    for name in parts:
        found = _query_folder(service, name, parent)
        if not found:
            found = _create_folder(service, name, parent)
        parent = found
    if not parent:
        raise RuntimeError("Failed to ensure Drive folder path")
    return parent


def _mime_for(path: Path) -> str:
    m, _ = mimetypes.guess_type(str(path))
    return m or "application/octet-stream"


def upload_file(service, folder_id: str, path: Path) -> Dict[str, str]:
    meta = {"name": path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(path), mimetype=_mime_for(path), resumable=True)
    _sleep_for_ratelimit(_load_config())
    file = service.files().create(body=meta, media_body=media, fields="id,name,webViewLink,webContentLink").execute()

    # Try to make file shareable (anyone with link)
    try:
        _sleep_for_ratelimit(_load_config())
        service.permissions().create(
            fileId=file["id"],
            body={"role": "reader", "type": "anyone"},
        ).execute()
        # Re-fetch to get webViewLink
        _sleep_for_ratelimit(_load_config())
        file = service.files().get(fileId=file["id"], fields="id,name,webViewLink,webContentLink").execute()
    except Exception:
        pass

    return {
        "id": file.get("id"),
        "name": file.get("name"),
        "webViewLink": file.get("webViewLink"),
        "webContentLink": file.get("webContentLink"),
    }


def _resolve_platform_root(cfg: DriveConfig, platform: str) -> Optional[str]:
    return cfg.platform_folder_ids.get(platform) or cfg.root_folder_id


def _manifest_path() -> Path:
    return BUILD_DIR / "drive_manifest.json"


def _read_manifest() -> Dict[str, Dict[str, Dict[str, str]]]:
    p = _manifest_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _write_manifest(data: Dict[str, Dict[str, Dict[str, str]]]) -> None:
    p = _manifest_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_platform_assets(
    slug: str,
    platform: str,
    *,
    service=None,
    date_str: Optional[str] = None,
    cleanup_local: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Upload platform bundle files under build/platform_assets/<platform>/<slug>/.

    Returns a mapping of filename -> { id, webViewLink, webContentLink }.
    """
    cfg = _load_config()
    if service is None:
        service = get_service()
    platform_root = _resolve_platform_root(cfg, platform)
    if not platform_root:
        raise RuntimeError("GDRIVE_ROOT_FOLDER_ID or platform-specific folder id not configured")

    today = date_str or datetime.now().strftime("%Y-%m-%d")
    dish_dir = BUILD_DIR / "platform_assets" / platform / slug
    if not dish_dir.exists():
        raise FileNotFoundError(f"Missing platform bundle: {dish_dir}")

    folder_id = ensure_path(service, [platform, today, slug], root_id=cfg.root_folder_id)

    results: Dict[str, Dict[str, str]] = {}
    for f in sorted(dish_dir.glob("*")):
        if not f.is_file():
            continue
        info = upload_file(service, folder_id, f)
        results[f.name] = info
        if cleanup_local:
            try:
                f.unlink()
            except Exception:
                pass

    # Update manifest
    manifest = _read_manifest()
    manifest.setdefault(slug, {})[platform] = results
    _write_manifest(manifest)
    return results


def sync_batch(
    slugs: Iterable[str],
    platforms: Iterable[str],
    *,
    cleanup_local: bool = False,
) -> Dict[str, Dict[str, Dict[str, str]]]:
    service = get_service()
    out: Dict[str, Dict[str, Dict[str, str]]] = {}
    for slug in slugs:
        out[slug] = {}
        for platform in platforms:
            try:
                out[slug][platform] = sync_platform_assets(slug, platform, service=service, cleanup_local=cleanup_local)
            except Exception as e:  # noqa: BLE001
                out[slug][platform] = {"error": str(e)}  # type: ignore[assignment]
    return out


def _discover_ready_slugs() -> List[str]:
    """Find slugs that have platform bundles prepared."""
    bundles_root = BUILD_DIR / "platform_assets"
    slugs: set[str] = set()
    if not bundles_root.exists():
        return []
    for platform_dir in bundles_root.iterdir():
        if not platform_dir.is_dir():
            continue
        for slug_dir in platform_dir.iterdir():
            if slug_dir.is_dir() and any(slug_dir.glob("*")):
                slugs.add(slug_dir.name)
    return sorted(slugs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync platform assets to Google Drive")
    parser.add_argument("--slug", action="append", help="Slug(s) to upload; can be repeated")
    parser.add_argument("--platforms", help="Comma-separated platforms to upload (default: detect bundles present)")
    parser.add_argument("--cleanup", action="store_true", help="Delete local files after successful upload")
    args = parser.parse_args()

    slugs = args.slug or _discover_ready_slugs()
    if not slugs:
        print("No slugs provided and none discovered.")
        raise SystemExit(1)

    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    else:
        # Auto-detect platforms by reading subfolders
        platforms: List[str] = []
        for slug in slugs:
            for p in (BUILD_DIR / "platform_assets").iterdir():
                if (p / slug).exists():
                    platforms.append(p.name)
        platforms = sorted(set(platforms))

    try:
        results = sync_batch(slugs, platforms, cleanup_local=args.cleanup)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except Exception as e:  # noqa: BLE001
        print(f"Drive sync failed: {e}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()

