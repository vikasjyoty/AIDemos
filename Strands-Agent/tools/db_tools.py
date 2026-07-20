from __future__ import annotations

"""SQLite-backed example tools for simple database reads and writes."""

import logging
import sqlite3
from pathlib import Path

from strands import tool


_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "agent_tools_demo.db"
logger = logging.getLogger("tools.db")


def _get_connection() -> sqlite3.Connection:
    """Open the demo database and ensure required tables exist."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(_DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT,
            phone TEXT
        )
        """
    )
    connection.commit()
    return connection


@tool
def db_upsert_contact(name: str, email: str = "", phone: str = "") -> dict:
    """Insert or update a contact in the local demo SQLite database."""
    logger.info("Tool selected: db_upsert_contact(name=%s)", name)
    clean_name = name.strip()
    if not clean_name:
        return {"ok": False, "error": "name is required"}

    with _get_connection() as connection:
        connection.execute(
            """
            INSERT INTO contacts(name, email, phone)
            VALUES (?, ?, ?)
            ON CONFLICT(name)
            DO UPDATE SET email=excluded.email, phone=excluded.phone
            """,
            (clean_name, email.strip(), phone.strip()),
        )
        connection.commit()

    result = {
        "ok": True,
        "action": "upsert_contact",
        "name": clean_name,
        "email": email.strip(),
        "phone": phone.strip(),
        "db_path": str(_DB_PATH),
    }
    logger.info("Tool completed: db_upsert_contact(name=%s)", clean_name)
    return result


@tool
def db_get_contact(name: str) -> dict:
    """Fetch a single contact by name from the local demo database."""
    logger.info("Tool selected: db_get_contact(name=%s)", name)
    clean_name = name.strip()
    if not clean_name:
        return {"ok": False, "error": "name is required"}

    with _get_connection() as connection:
        row = connection.execute(
            "SELECT name, email, phone FROM contacts WHERE name = ?",
            (clean_name,),
        ).fetchone()

    if row is None:
        logger.info("Tool completed: db_get_contact(found=False)")
        return {"ok": False, "found": False, "name": clean_name}

    result = {
        "ok": True,
        "found": True,
        "contact": {
            "name": row[0],
            "email": row[1],
            "phone": row[2],
        },
    }
    logger.info("Tool completed: db_get_contact(found=True)")
    return result


@tool
def db_list_contacts(limit: int = 10) -> dict:
    """List recent contacts from the local demo database."""
    logger.info("Tool selected: db_list_contacts(limit=%s)", limit)
    safe_limit = max(1, min(limit, 100))

    with _get_connection() as connection:
        rows = connection.execute(
            "SELECT name, email, phone FROM contacts ORDER BY id DESC LIMIT ?",
            (safe_limit,),
        ).fetchall()

    result = {
        "ok": True,
        "count": len(rows),
        "contacts": [
            {"name": row[0], "email": row[1], "phone": row[2]} for row in rows
        ],
    }
    logger.info("Tool completed: db_list_contacts(count=%s)", result["count"])
    return result


DB_TOOLS = [db_upsert_contact, db_get_contact, db_list_contacts]