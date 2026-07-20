from __future__ import annotations

import logging

from strands import Agent
from strands.models.ollama import OllamaModel

from tools import get_tools_by_groups

from .config import AgentConfig


logger = logging.getLogger("agent_app.runner")


def _preview(text: str, limit: int = 180) -> str:
    """Return a compact single-line preview for log readability."""
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3]}..."


class AgentRunner:
    """Simple wrapper that runs prompts with an Ollama-backed Strands Agent."""

    def __init__(self, config: AgentConfig) -> None:
        """Create the model + agent one time so run_once stays easy to read."""
        logger.info("[TOOLS] Requested tool groups=%s", config.enabled_tool_groups)
        selected_tools = get_tools_by_groups(config.enabled_tool_groups)
        tool_names = [getattr(tool, "__name__", str(tool)) for tool in selected_tools]
        logger.info("[TOOLS] Active tools (%s): %s", len(tool_names), ", ".join(tool_names))
        logger.info(
            "[FLOW] Creating Ollama model: host=%s model=%s temperature=%s max_tokens=%s",
            config.host,
            config.model_name,
            config.temperature,
            config.max_tokens,
        )
        model = OllamaModel(
            config.host,
            model_id=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        self.agent = Agent(model=model, tools=selected_tools, system_prompt=config.system_prompt)
        logger.info("[FLOW] Agent created with %s tools", len(selected_tools))

    def run_once(self, prompt: str) -> str:
        """Execute one prompt and return the model response as text."""
        logger.info("[LLM] Input preview: %s", _preview(prompt))
        logger.info("[LLM] Sending prompt to model")
        response = str(self.agent(prompt))
        logger.info("[LLM] Response received (characters=%s)", len(response))
        logger.info("[LLM] Output preview: %s", _preview(response))
        return response
