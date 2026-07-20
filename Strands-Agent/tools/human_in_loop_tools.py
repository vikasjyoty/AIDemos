from __future__ import annotations

"""Human-in-the-loop demo tools for approval-gated actions."""

import logging
from datetime import datetime, timezone
from uuid import uuid4

from strands import tool


# In-memory request store for demo usage.
_APPROVAL_REQUESTS: dict[str, dict] = {}
logger = logging.getLogger("tools.approval")


@tool
def request_human_approval(action: str, reason: str) -> dict:
    """Create an approval request id before sensitive operations."""
    logger.info("Tool selected: request_human_approval(action=%s)", action)
    clean_action = action.strip()
    clean_reason = reason.strip()

    if not clean_action:
        return {"ok": False, "error": "action is required"}
    if not clean_reason:
        return {"ok": False, "error": "reason is required"}

    approval_id = f"apr_{uuid4().hex[:10]}"
    _APPROVAL_REQUESTS[approval_id] = {
        "action": clean_action,
        "reason": clean_reason,
        "approved": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }

    result = {
        "ok": True,
        "approval_id": approval_id,
        "status": "pending_human_approval",
        "action": clean_action,
        "reason": clean_reason,
    }
    logger.info("Tool completed: request_human_approval(approval_id=%s)", approval_id)
    return result


@tool
def approve_request(approval_id: str, approved_by: str) -> dict:
    """Mark a pending approval request as approved."""
    logger.info("Tool selected: approve_request(approval_id=%s)", approval_id)
    clean_id = approval_id.strip()
    clean_approver = approved_by.strip()

    if clean_id not in _APPROVAL_REQUESTS:
        return {"ok": False, "error": f"unknown approval_id '{clean_id}'"}
    if not clean_approver:
        return {"ok": False, "error": "approved_by is required"}

    request = _APPROVAL_REQUESTS[clean_id]
    request["approved"] = True
    request["approved_by"] = clean_approver
    request["approved_utc"] = datetime.now(timezone.utc).isoformat()

    result = {
        "ok": True,
        "approval_id": clean_id,
        "status": "approved",
        "approved_by": clean_approver,
    }
    logger.info("Tool completed: approve_request(status=approved)")
    return result


@tool
def execute_sensitive_action(approval_id: str, action_payload: str) -> dict:
    """Execute a sensitive action only when an approval request is approved."""
    logger.info("Tool selected: execute_sensitive_action(approval_id=%s)", approval_id)
    clean_id = approval_id.strip()
    payload = action_payload.strip()

    if clean_id not in _APPROVAL_REQUESTS:
        return {"ok": False, "error": f"unknown approval_id '{clean_id}'"}
    if not payload:
        return {"ok": False, "error": "action_payload is required"}

    request = _APPROVAL_REQUESTS[clean_id]
    if not request.get("approved", False):
        logger.info("Tool blocked: execute_sensitive_action(approval_required)")
        return {
            "ok": False,
            "error": "approval_required",
            "status": "blocked",
            "approval_id": clean_id,
            "action": request["action"],
        }

    result = {
        "ok": True,
        "status": "executed",
        "approval_id": clean_id,
        "action": request["action"],
        "payload": payload,
        "executed_utc": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Tool completed: execute_sensitive_action(status=executed)")
    return result


HUMAN_IN_LOOP_TOOLS = [request_human_approval, approve_request, execute_sensitive_action]