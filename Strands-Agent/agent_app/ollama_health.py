from __future__ import annotations

from urllib import error, request


class OllamaHealthChecker:
    """Performs lightweight readiness checks against a local Ollama server."""

    def __init__(self, host: str, timeout_seconds: int = 3) -> None:
        """Store host and timeout values for subsequent health checks."""
        self.host = host
        self.timeout_seconds = timeout_seconds

    def ensure_running(self) -> None:
        """Raise an error when Ollama cannot be reached or returns non-200."""
        # /api/tags is a small endpoint that confirms server health.
        url = self.host.rstrip("/") + "/api/tags"
        try:
            with request.urlopen(url, timeout=self.timeout_seconds) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Ollama server returned status {resp.status} at {url}")
        except error.URLError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {self.host}. Start Ollama and try again."
            ) from exc
