from __future__ import annotations

"""Notification tool examples (mock SMS, email, and Slack message sends)."""

import logging
import re
from datetime import datetime, timezone
from uuid import uuid4

from strands import tool


_PHONE_REGEX = re.compile(r"^\+?[1-9]\d{7,14}$")
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
logger = logging.getLogger("tools.notify")


def _message_id(prefix: str) -> str:
    """Create a stable-looking id for mock delivery records."""
    return f"{prefix}_{uuid4().hex[:12]}"


@tool
def notify_sms(to_number: str, message: str) -> dict:
    """Mock an SMS send and return a delivery receipt payload."""
    logger.info("Tool selected: notify_sms(to_number=%s)", to_number)
    phone = to_number.strip()
    text = message.strip()

    if not _PHONE_REGEX.match(phone):
        return {"ok": False, "error": "Invalid phone format. Use E.164 like +14155552671."}
    if not text:
        return {"ok": False, "error": "Message cannot be empty."}

    result = {
        "ok": True,
        "channel": "sms",
        "provider": "mock_twilio",
        "message_id": _message_id("sms"),
        "to": phone,
        "message": text,
        "status": "queued",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Tool completed: notify_sms(status=%s)", result["status"])
    return result


@tool
def notify_email(to_email: str, subject: str, body: str) -> dict:
    """Mock an email send and return a delivery receipt payload."""
    logger.info("Tool selected: notify_email(to_email=%s)", to_email)
    email = to_email.strip().lower()
    clean_subject = subject.strip()
    clean_body = body.strip()

    if not _EMAIL_REGEX.match(email):
        return {"ok": False, "error": "Invalid email format."}
    if not clean_subject:
        return {"ok": False, "error": "Subject cannot be empty."}
    if not clean_body:
        return {"ok": False, "error": "Body cannot be empty."}

    result = {
        "ok": True,
        "channel": "email",
        "provider": "mock_ses",
        "message_id": _message_id("email"),
        "to": email,
        "subject": clean_subject,
        "body_preview": clean_body[:200],
        "status": "queued",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Tool completed: notify_email(status=%s)", result["status"])
    return result


@tool
def notify_slack(channel: str, text: str) -> dict:
    """Mock a Slack message send and return an API-like response."""
    logger.info("Tool selected: notify_slack(channel=%s)", channel)
    clean_channel = channel.strip()
    clean_text = text.strip()

    if not clean_channel.startswith("#"):
        return {"ok": False, "error": "Slack channel must start with '#' (example: #alerts)."}
    if not clean_text:
        return {"ok": False, "error": "Text cannot be empty."}

    result = {
        "ok": True,
        "channel": "slack",
        "provider": "mock_slack",
        "message_id": _message_id("slack"),
        "destination": clean_channel,
        "text": clean_text,
        "status": "posted",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Tool completed: notify_slack(status=%s)", result["status"])
    return result


NOTIFICATION_TOOLS = [notify_sms, notify_email, notify_slack]