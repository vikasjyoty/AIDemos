from __future__ import annotations

import logging
import sys

from agent_app import AgentApplication
from agent_app.logging_setup import configure_logging


logger = logging.getLogger("main")


def main() -> int:
    """Run the app and return an exit code."""
    configure_logging()

    try:
        logger.info("Starting Strands-Agent application")
        return AgentApplication().run()
    except Exception as exc:
        logger.exception("Application failed: %s", exc)
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
