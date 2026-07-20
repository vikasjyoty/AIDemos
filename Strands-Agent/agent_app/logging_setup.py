from __future__ import annotations

"""Simple logging setup for beginner-friendly runtime visibility."""

import logging
import os
import sys


class CategoryColorFormatter(logging.Formatter):
    """Colorize log messages by category tag like [USER], [LLM], [TOOLS], [FLOW]."""

    RESET = "\x1b[0m"
    TAG_COLORS = {
        "[FLOW]": "\x1b[36m",   # cyan
        "[USER]": "\x1b[32m",   # green
        "[LLM]": "\x1b[35m",    # magenta
        "[TOOLS]": "\x1b[33m",  # yellow
        "[ERROR]": "\x1b[31m",  # red
    }

    def __init__(self, fmt: str, datefmt: str | None, use_color: bool) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if not self.use_color:
            return message

        for tag, color in self.TAG_COLORS.items():
            if tag in message:
                return message.replace(tag, f"{color}{tag}{self.RESET}", 1)
        return message


def _should_use_color() -> bool:
    """Enable color unless disabled, and only on interactive terminals."""
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def configure_logging() -> None:
    """Configure process-wide logging only once."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        CategoryColorFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
            use_color=_should_use_color(),
        )
    )

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
