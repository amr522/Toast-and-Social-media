from __future__ import annotations

import time
from dataclasses import dataclass
import logging
from typing import Any, Dict, Optional

import requests

from .config import MiniMaxConfig, load_config


class MiniMaxError(RuntimeError):
    def __init__(self, message: str, status_code: Optional[int] = None, payload: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


@dataclass
class _RateLimiter:
    rpm: int
    _last_ts: float = 0.0

    def wait(self) -> None:
        if self.rpm <= 0:
            return
        min_interval = 60.0 / float(self.rpm)
        now = time.time()
        elapsed = now - self._last_ts
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_ts = time.time()


class MiniMaxClient:
    """MiniMax API client.

    Features:
    - Auth via Bearer token from env (see src.minimax.config.load_config)
    - Rate limiting (RPM)
    - Exponential backoff retries
    - Structured error handling parsing MiniMax base_resp envelope
    - Env-driven endpoints/models (no hardcoded constants required)
    - Lightweight logging integrated with Python logging
    """

    def __init__(self, config: Optional[MiniMaxConfig] = None, session: Optional[requests.Session] = None):
        self.config = config or load_config()
        self.session = session or requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        })
        self._limiter = _RateLimiter(self.config.rate_limit_rpm)
        self._log = logging.getLogger(__name__)

    def _url(self, path: str) -> str:
        return f"{self.config.base_url}{path}"

    def _request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform an HTTP request with retries and error parsing."""
        last_err: Optional[Exception] = None
        for attempt in range(1, self.config.max_retries + 1):
            self._limiter.wait()
            try:
                url = self._url(path)
                if self._log.isEnabledFor(logging.DEBUG):
                    self._log.debug("MiniMax %s %s attempt=%s payloadKeys=%s", method.upper(), url, attempt, list((json or {}).keys()))
                resp = self.session.request(method=method.upper(), url=url, json=json, timeout=self.config.timeout_sec)
                # Raise for transport-level issues (HTTP 4xx/5xx)
                if resp.status_code >= 400:
                    raise MiniMaxError(f"HTTP {resp.status_code} from MiniMax", status_code=resp.status_code, payload=self._safe_json(resp))
                data = self._safe_json(resp)
                # MiniMax success/error envelope
                base = data.get("base_resp") or {}
                code = base.get("status_code")
                if code not in (None, 0):
                    # Non-zero indicates API error per docs
                    msg = base.get("status_msg") or "MiniMax API error"
                    if self._log.isEnabledFor(logging.WARNING):
                        self._log.warning("MiniMax API error: code=%s msg=%s", code, msg)
                    raise MiniMaxError(msg, status_code=code, payload=data)
                if self._log.isEnabledFor(logging.DEBUG):
                    self._log.debug("MiniMax response ok: status=%s keys=%s", resp.status_code, list(data.keys()))
                return data
            except Exception as e:  # noqa: BLE001 broad for retry strategy
                last_err = e
                if attempt >= self.config.max_retries:
                    break
                # Exponential backoff with jitter
                backoff = min(2 ** (attempt - 1), 16)
                if self._log.isEnabledFor(logging.DEBUG):
                    self._log.debug("Retrying after error: %s backoff=%ss", e, backoff)
                time.sleep(backoff)
        if isinstance(last_err, MiniMaxError):
            raise last_err
        raise MiniMaxError(str(last_err or "MiniMax request failed"))

    @staticmethod
    def _safe_json(resp: requests.Response) -> Dict[str, Any]:
        try:
            return resp.json()
        except Exception:  # noqa: BLE001
            return {"raw": resp.text}

    # High-level helpers -------------------------------------------------
    def chat_completions(self, messages: list[dict], model: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Text generation via chat completions endpoint."""
        payload = {
            "model": model or self.config.chat_model,
            "messages": messages,
        }
        payload.update(kwargs)
        return self._request("POST", self.config.text_path, json=payload)

    def image_generation(self, prompt: dict, **kwargs: Any) -> Dict[str, Any]:
        """Text-to-image or image-enhance generation."""
        payload = {"model": self.config.image_model}
        payload.update(prompt)
        payload.update(kwargs)
        return self._request("POST", self.config.image_path, json=payload)

    def text_to_speech(self, prompt: dict, **kwargs: Any) -> Dict[str, Any]:
        """Text-to-speech (T2A) generation."""
        payload = {"model": self.config.tts_model}
        payload.update(prompt)
        payload.update(kwargs)
        return self._request("POST", self.config.tts_path, json=payload)

    def music_generation(self, prompt: dict, **kwargs: Any) -> Dict[str, Any]:
        """Music generation."""
        payload = {"model": self.config.music_model}
        payload.update(prompt)
        payload.update(kwargs)
        return self._request("POST", self.config.music_path, json=payload)

    def video_generation(self, prompt: dict, **kwargs: Any) -> Dict[str, Any]:
        """Video generation (text-to-video or image-to-video)."""
        payload = {"model": self.config.video_model}
        payload.update(prompt)
        payload.update(kwargs)
        return self._request("POST", self.config.video_path, json=payload)

    def video_query(self, job_id: str) -> Dict[str, Any]:
        """Query video generation job status using configured query path.

        Payload shape may vary across API versions; we use a generic {"id": job_id}.
        """
        payload = {"id": job_id}
        return self._request("POST", self.config.video_query_path, json=payload)
