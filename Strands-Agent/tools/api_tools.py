from __future__ import annotations

"""Example API tools for mock and real (allowlisted) HTTP calls."""

import json
import logging
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from strands import tool


_ALLOWED_HOSTS = {"api.github.com", "httpbin.org", "jsonplaceholder.typicode.com"}
logger = logging.getLogger("tools.api")


@tool
def api_get_json(url: str, timeout_seconds: int = 8) -> dict:
    """Fetch JSON from an allowlisted URL to demonstrate external API calling."""
    logger.info("Tool selected: api_get_json(url=%s)", url)
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return {"ok": False, "error": "Only http/https URLs are allowed."}

    host = (parsed.hostname or "").lower()
    if host not in _ALLOWED_HOSTS:
        logger.info("Tool blocked by policy: api_get_json(host=%s)", host)
        return {
            "ok": False,
            "error": f"Host '{host}' is not allowlisted.",
            "allowed_hosts": sorted(_ALLOWED_HOSTS),
        }

    safe_timeout = max(1, min(timeout_seconds, 20))
    request = Request(url.strip(), headers={"User-Agent": "Strands-Agent-Demo/1.0"})

    try:
        with urlopen(request, timeout=safe_timeout) as response:
            status = getattr(response, "status", 200)
            raw_body = response.read().decode("utf-8", errors="replace")
    except URLError as exc:
        logger.info("Tool failed: api_get_json(error=%s)", exc)
        return {"ok": False, "error": f"Request failed: {exc}"}

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        logger.info("Tool completed: api_get_json(non_json_response)")
        return {
            "ok": False,
            "error": "Response is not valid JSON.",
            "status": status,
            "body_preview": raw_body[:300],
        }

    result = {
        "ok": True,
        "status": status,
        "host": host,
        "data": body,
    }
    logger.info("Tool completed: api_get_json(status=%s host=%s)", status, host)
    return result


@tool
def api_mock_customer_lookup(customer_id: str) -> dict:
    """Return deterministic mock customer data for API-calling practice."""
    logger.info("Tool selected: api_mock_customer_lookup(customer_id=%s)", customer_id)
    clean_id = customer_id.strip()
    if not clean_id:
        return {"ok": False, "error": "customer_id is required"}

    result = {
        "ok": True,
        "source": "mock_api",
        "customer": {
            "customer_id": clean_id,
            "tier": "gold" if clean_id[-1].isdigit() and int(clean_id[-1]) % 2 == 0 else "standard",
            "active": True,
            "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        },
    }
    logger.info("Tool completed: api_mock_customer_lookup")
    return result


API_TOOLS = [api_get_json, api_mock_customer_lookup]