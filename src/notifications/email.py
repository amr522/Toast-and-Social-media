from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable, Optional


def _smtp_config() -> dict:
    return {
        "host": os.getenv("SMTP_HOST", ""),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from_addr": os.getenv("SMTP_USER", ""),
        "to_addrs": [addr.strip() for addr in os.getenv("NOTIFICATION_EMAIL", "").split(",") if addr.strip()],
    }


def send_email(subject: str, body: str, *, attachments: Optional[Iterable[tuple[str, bytes, str]]] = None) -> bool:
    """Send a plain-text email with optional attachments.

    attachments: iterable of (filename, content_bytes, mime_type)
    Returns True if at least one recipient was configured and the email was attempted.
    """
    cfg = _smtp_config()
    if not cfg["host"] or not cfg["user"] or not cfg["password"] or not cfg["to_addrs"]:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["from_addr"]
    msg["To"] = ", ".join(cfg["to_addrs"])
    msg.set_content(body)

    for att in attachments or []:
        filename, content, mime = att
        maintype, subtype = (mime.split("/", 1) + ["octet-stream"])[:2]
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

    with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
        server.starttls()
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
    return True

