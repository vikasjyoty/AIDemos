from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentConfig:
    """Runtime settings collected from app, llm, and tools config files."""

    model_name: str
    host: str
    temperature: float
    max_tokens: int
    system_prompt: str
    interactive_banner: str
    exit_commands: tuple[str, ...]
    enabled_tool_groups: tuple[str, ...]


CONFIG_ROOT = Path(__file__).resolve().parent.parent / "config"
APP_CONFIG_PATH = CONFIG_ROOT / "app" / "config.json"
LLM_CONFIG_PATH = CONFIG_ROOT / "llm" / "config.json"
TOOLS_CONFIG_PATH = CONFIG_ROOT / "tools" / "config.json"


DEFAULT_SYSTEM_PROMPT = (
    "You are a professional local agent powered by Ollama. "
    "Use tools proactively when they improve accuracy, explain actions briefly, "
    "and provide concise, correct answers."
)


def _read_json(path: Path) -> dict:
    """Read one JSON config file and return a dictionary."""
    if not path.exists():
        raise ValueError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def load_config() -> AgentConfig:
    """Load runtime settings from config/app, config/llm, and config/tools."""
    app_data = _read_json(APP_CONFIG_PATH)
    llm_data = _read_json(LLM_CONFIG_PATH)
    tools_data = _read_json(TOOLS_CONFIG_PATH)

    model_name = str(llm_data.get("model_name", "")).strip()
    host = str(llm_data.get("host", "http://localhost:11434")).strip()
    temperature = float(llm_data.get("temperature", 0.2))
    max_tokens = int(llm_data.get("max_tokens", 512))
    system_prompt = str(llm_data.get("system_prompt", DEFAULT_SYSTEM_PROMPT)).strip()

    interactive_banner = str(
        app_data.get("interactive_banner", "Interactive mode started. Type 'exit' or 'quit' to stop.")
    ).strip()
    exit_commands_data = app_data.get("exit_commands", ["exit", "quit"])
    exit_commands = tuple(str(command).strip().lower() for command in exit_commands_data if str(command).strip())

    enabled_tool_groups_data = tools_data.get(
        "enabled_tool_groups",
        ["builtin", "custom", "db", "api", "notification", "calendar", "human_in_loop"],
    )
    enabled_tool_groups = tuple(
        str(group).strip().lower() for group in enabled_tool_groups_data if str(group).strip()
    )

    if not model_name:
        raise ValueError("config/llm/config.json must include model_name")
    if not exit_commands:
        raise ValueError("config/app/config.json must include at least one exit command")
    if not enabled_tool_groups:
        raise ValueError("config/tools/config.json must include at least one enabled tool group")

    return AgentConfig(
        model_name=model_name,
        host=host,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        interactive_banner=interactive_banner,
        exit_commands=exit_commands,
        enabled_tool_groups=enabled_tool_groups,
    )
