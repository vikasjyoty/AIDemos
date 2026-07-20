from __future__ import annotations

import logging

from .agent_runner import AgentRunner
from .config import AgentConfig
from .config import load_config
from .ollama_health import OllamaHealthChecker


logger = logging.getLogger("agent_app.app")


class AgentApplication:
    """Simple app flow: load config file, verify Ollama, then chat interactively."""

    def _run_interactive_loop(self, runner: AgentRunner, config: AgentConfig) -> None:
        """Keep reading prompts until the user exits."""
        logger.info("[FLOW] Interactive mode started")
        print(config.interactive_banner)
        while True:
            user_prompt = input("You> ").strip()

            if not user_prompt:
                logger.info("[USER] Empty input skipped")
                continue

            if user_prompt.lower() in config.exit_commands:
                logger.info("[FLOW] User ended interactive session")
                print("Session ended.")
                return

            logger.info("[USER] Input: %s", user_prompt)
            response = runner.run_once(user_prompt)
            logger.info("[LLM] Output rendered to terminal (characters=%s)", len(response))
            print(f"Agent> {response}")

    def run(self) -> int:
        """Execute the application flow and return a process exit code."""
        # Read runtime config from config/app, config/llm, and config/tools.
        config = load_config()
        logger.info("[FLOW] Config loaded: model=%s host=%s", config.model_name, config.host)

        # Validate Ollama server availability before creating the agent.
        logger.info("[FLOW] Checking Ollama health")
        checker = OllamaHealthChecker(config.host)
        checker.ensure_running()
        logger.info("[FLOW] Ollama health check passed")

        # Reuse one runner instance for both one-shot and interactive mode.
        runner = AgentRunner(config)
        logger.info("[FLOW] Agent runner initialized")

        # Otherwise start a continuous command loop.
        self._run_interactive_loop(runner, config)
        return 0
