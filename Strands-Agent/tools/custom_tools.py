from __future__ import annotations

"""Custom tool implementations exposed to the local Strands agent."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from strands import tool


logger = logging.getLogger("tools.custom")


@tool
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers and return a structured result."""
    logger.info("Tool selected: add_numbers(a=%s, b=%s)", a, b)
    # Returning structured output helps the agent (and users) read tool results clearly.
    result = {"a": a, "b": b, "result": a + b}
    logger.info("Tool completed: add_numbers(result=%s)", result["result"])
    return result


@tool
def reverse_text(text: str) -> str:
    """Reverse any text string."""
    logger.info("Tool selected: reverse_text(text_length=%s)", len(text))
    # Simple text utility to demonstrate lightweight custom tools.
    result = text[::-1]
    logger.info("Tool completed: reverse_text")
    return result


@tool
def local_time(city: str = "UTC") -> str:
    """Get local time for a small set of city names."""
    logger.info("Tool selected: local_time(city=%s)", city)
    # Keep accepted city inputs predictable for a beginner-friendly demo.
    city_map = {
        "utc": "UTC",
        "india": "Asia/Kolkata",
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
    }

    # Normalize input so case/spacing differences do not break lookups.
    key = city.strip().lower()
    if key not in city_map:
        allowed = ", ".join(sorted(city_map.keys()))
        logger.info("Tool completed: local_time(city_not_supported)")
        return f"Unknown city '{city}'. Try one of: {allowed}."

    zone_name = city_map[key]
    # ZoneInfo gives timezone-aware datetime output.
    now = datetime.now(ZoneInfo(zone_name))
    result = f"{city.title()} time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    logger.info("Tool completed: local_time(zone=%s)", zone_name)
    return result


CUSTOM_TOOLS = [add_numbers, reverse_text, local_time]
