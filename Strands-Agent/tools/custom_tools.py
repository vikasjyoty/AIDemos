from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from strands import tool


@tool
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers and return a structured result."""
    # Returning structured output helps the agent (and users) read tool results clearly.
    return {"a": a, "b": b, "result": a + b}


@tool
def reverse_text(text: str) -> str:
    """Reverse any text string."""
    return text[::-1]


@tool
def local_time(city: str = "UTC") -> str:
    """Get local time for a small set of city names."""
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
        return f"Unknown city '{city}'. Try one of: {allowed}."

    zone_name = city_map[key]
    # ZoneInfo gives timezone-aware datetime output.
    now = datetime.now(ZoneInfo(zone_name))
    return f"{city.title()} time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


CUSTOM_TOOLS = [add_numbers, reverse_text, local_time]
