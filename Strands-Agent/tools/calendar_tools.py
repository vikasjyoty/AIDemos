from __future__ import annotations

"""Calendar tool examples using an in-memory event store."""

import logging
from datetime import datetime, timezone
from uuid import uuid4

from strands import tool


_EVENTS: dict[str, dict] = {}
logger = logging.getLogger("tools.calendar")


@tool
def calendar_create_event(title: str, start_iso_utc: str, duration_minutes: int = 30) -> dict:
    """Create a mock calendar event and return its identifier."""
    logger.info("Tool selected: calendar_create_event(title=%s)", title)
    clean_title = title.strip()
    clean_start = start_iso_utc.strip()
    safe_duration = max(15, min(duration_minutes, 8 * 60))

    if not clean_title:
        return {"ok": False, "error": "title is required"}
    if not clean_start:
        return {"ok": False, "error": "start_iso_utc is required"}

    try:
        datetime.fromisoformat(clean_start.replace("Z", "+00:00"))
    except ValueError:
        return {"ok": False, "error": "start_iso_utc must be ISO format (example: 2026-07-21T10:00:00Z)."}

    event_id = f"evt_{uuid4().hex[:10]}"
    _EVENTS[event_id] = {
        "event_id": event_id,
        "title": clean_title,
        "start_iso_utc": clean_start,
        "duration_minutes": safe_duration,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }

    result = {"ok": True, "event": _EVENTS[event_id]}
    logger.info("Tool completed: calendar_create_event(event_id=%s)", event_id)
    return result


@tool
def calendar_list_events(limit: int = 10) -> dict:
    """List recent mock calendar events."""
    logger.info("Tool selected: calendar_list_events(limit=%s)", limit)
    safe_limit = max(1, min(limit, 100))
    events = list(_EVENTS.values())[-safe_limit:]

    result = {
        "ok": True,
        "count": len(events),
        "events": events,
    }
    logger.info("Tool completed: calendar_list_events(count=%s)", result["count"])
    return result


CALENDAR_TOOLS = [calendar_create_event, calendar_list_events]