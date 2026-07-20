"""Central tool registry imported by the agent runtime."""

import logging

from .api_tools import API_TOOLS
from .builtin_tools import BUILTIN_TOOLS
from .calendar_tools import CALENDAR_TOOLS
from .custom_tools import CUSTOM_TOOLS
from .db_tools import DB_TOOLS
from .human_in_loop_tools import HUMAN_IN_LOOP_TOOLS
from .notification_tools import NOTIFICATION_TOOLS


logger = logging.getLogger("tools.registry")

TOOL_GROUPS = {
	"builtin": BUILTIN_TOOLS,
	"custom": CUSTOM_TOOLS,
	"db": DB_TOOLS,
	"api": API_TOOLS,
	"notification": NOTIFICATION_TOOLS,
	"calendar": CALENDAR_TOOLS,
	"human_in_loop": HUMAN_IN_LOOP_TOOLS,
}


def get_tools_by_groups(group_names: tuple[str, ...] | list[str]) -> list:
	"""Return merged tool list for the requested group names."""
	logger.info("[TOOLS] Resolving tool groups=%s", group_names)
	selected_tools = []
	for group_name in group_names:
		key = group_name.strip().lower()
		if key not in TOOL_GROUPS:
			known = ", ".join(sorted(TOOL_GROUPS.keys()))
			raise ValueError(f"Unknown tool group '{group_name}'. Known groups: {known}")
		logger.info("[TOOLS] Adding group '%s' (%s tools)", key, len(TOOL_GROUPS[key]))
		selected_tools.extend(TOOL_GROUPS[key])
	logger.info("[TOOLS] Resolved total selected tools=%s", len(selected_tools))
	return selected_tools


# Default full tool set for compatibility.
ALL_TOOLS = get_tools_by_groups(tuple(TOOL_GROUPS.keys()))
