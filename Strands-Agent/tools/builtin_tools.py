"""Built-in tools sourced from strands-agents-tools."""

from strands_tools.calculator import calculator
from strands_tools.current_time import current_time

# These are prebuilt tools shipped by strands-agents-tools.
# Exposing them as a list makes registration in Agent(...) simple and explicit.
BUILTIN_TOOLS = [calculator, current_time]
