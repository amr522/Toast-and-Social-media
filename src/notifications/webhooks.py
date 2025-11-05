from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import requests


def post_webhook(url: str, payload: Dict[str, Any], *, timeout: int = 10) -> bool:
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)
    return 200 <= resp.status_code < 300


def notify_team(summary: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """Send a brief summary to a configured webhook (Slack/Discord or Make.com).

    Uses env var MAKE_WEBHOOK_NOTIFY_TEAM if present.
    """
    url = os.getenv("MAKE_WEBHOOK_NOTIFY_TEAM") or os.getenv("QA_WEBHOOK_URL")
    if not url:
        return False
    payload = {
        "text": summary,
        "summary": summary,
        "details": details or {},
    }
    try:
        return post_webhook(url, payload)
    except Exception:
        return False

