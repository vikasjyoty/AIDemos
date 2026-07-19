from __future__ import annotations

import argparse
import os
from typing import Optional

from strands import Agent

from tools import ALL_TOOLS
from tools.builtin_tools import BUILTIN_TOOLS
from tools.custom_tools import CUSTOM_TOOLS, add_numbers, local_time, reverse_text


def run_tools_only_demo() -> None:
    """Run tools directly so you can validate setup without an LLM."""
    # This mode is a quick smoke test for all tools without any model/provider setup.
    print("Running direct tool checks...\n")

    print("Custom tool -> add_numbers(7, 5):")
    print(add_numbers(a=7, b=5))
    print()

    print("Custom tool -> reverse_text('strands sdk demo'):")
    print(reverse_text(text="strands sdk demo"))
    print()

    print("Custom tool -> local_time('india'):")
    print(local_time(city="india"))
    print()

    # Built-in tools are loaded from the shared tool registry.
    calculator = BUILTIN_TOOLS[0]
    current_time = BUILTIN_TOOLS[1]

    print("Built-in tool -> calculator('12 * (8 + 3)'):")
    print(calculator(expression="12 * (8 + 3)"))
    print()

    print("Built-in tool -> current_time('UTC'):")
    print(current_time(timezone="UTC"))
    print()


def run_agent_demo(prompt: str, model: Optional[str]) -> None:
    """Run an agent that can decide which tools to call."""
    # The system prompt nudges behavior: concise answers and tool usage when useful.
    system_prompt = (
        "You are a basic Strands demo agent. "
        "Use tools when helpful, explain briefly, and keep answers concise."
    )

    # Agent receives the complete tool list, so it can call both built-in and custom tools.
    agent = Agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=system_prompt,
    )

    response = agent(prompt)
    print("\nAgent response:\n")
    print(response)


def parse_args() -> argparse.Namespace:
    # CLI flags make it easy to switch between local tool testing and full agent calls.
    parser = argparse.ArgumentParser(description="Basic Strands SDK demo agent")
    parser.add_argument(
        "--prompt",
        default="What is 225/15, and what time is it in UTC and India?",
        help="Prompt for the agent run",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("STRANDS_MODEL"),
        help=(
            "Optional model identifier (for example provider/model). "
            "If omitted, Strands default model resolution is used."
        ),
    )
    parser.add_argument(
        "--tools-only",
        action="store_true",
        help="Run direct tool smoke test only (no LLM call)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Loaded {len(CUSTOM_TOOLS)} custom tools and {len(BUILTIN_TOOLS)} built-in tools.")

    # tools-only avoids LLM/network dependencies and is ideal for first-time setup checks.
    if args.tools_only:
        run_tools_only_demo()
        return

    try:
        run_agent_demo(prompt=args.prompt, model=args.model)
    except Exception as exc:
        # Most failures here are model credential/provider setup issues.
        print("\nAgent run failed.")
        print("Reason:", exc)
        print(
            "\nTip: configure your model credentials/provider first, "
            "or run with --tools-only to test local tools."
        )


if __name__ == "__main__":
    main()
