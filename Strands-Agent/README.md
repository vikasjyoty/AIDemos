# Strands-Agent (Ollama + Strands SDK)

This folder contains a local, beginner-friendly agent app built with Strands SDK and Ollama.

The app now runs in continuous interactive mode and uses split config files:

- app config
- llm config
- tools config

## Current architecture

- main.py
	- Entry point
	- Configures logging
	- Starts the app

- agent_app/app.py
	- Loads config
	- Checks Ollama health
	- Starts interactive loop

- agent_app/agent_runner.py
	- Builds model + agent once
	- Logs LLM input/output previews
	- Logs selected tools

- tools/__init__.py
	- Tool group registry
	- Merges tools from enabled groups
	- Logs where tool selection happens

- config/app/config.json
	- Interactive banner and exit commands

- config/llm/config.json
	- Model, host, temperature, max tokens, system prompt

- config/tools/config.json
	- Enabled tool groups

## Tool groups

Valid group names:

- builtin
- custom
- db
- api
- notification
- calendar
- human_in_loop

## Install

From repository root:

```powershell
c:/Users/vikas/source/repos/AIDemos/.venv/Scripts/python.exe -m pip install -r Strands-Agent/requirements.txt
```

## Run

From Strands-Agent folder:

```powershell
c:/Users/vikas/source/repos/AIDemos/.venv/Scripts/python.exe main.py
```

You will get a prompt like:

- You> your question here
- Agent> response

Type exit or quit to end the session.

## Logging and visibility

Logs are structured with category tags so it is easy to see what happened.

Main tags:

- [FLOW] app lifecycle steps (config load, health check, runner init)
- [USER] user-entered input
- [LLM] prompt send, response receive, input/output previews
- [TOOLS] tool group resolution and active tool list
- [ERROR] failures and exceptions

Color coding (when terminal supports ANSI colors):

- [FLOW] cyan
- [USER] green
- [LLM] magenta
- [TOOLS] yellow
- [ERROR] red

If you want plain logs without colors, set NO_COLOR=1 in your terminal before running.

## Where tool selection happens

- tools/__init__.py
	- get_tools_by_groups(...) resolves enabled groups and logs each added group.

- agent_app/agent_runner.py
	- reads enabled_tool_groups from config
	- calls get_tools_by_groups(...)
	- logs final active tool names

## Config examples

app config (config/app/config.json)

```json
{
	"interactive_banner": "Interactive mode started. Type 'exit' or 'quit' to stop.",
	"exit_commands": ["exit", "quit"]
}
```

llm config (config/llm/config.json)

```json
{
	"model_name": "llama3.2:3b",
	"host": "http://localhost:11434",
	"temperature": 0.2,
	"max_tokens": 512,
	"system_prompt": "You are a professional local agent powered by Ollama..."
}
```

tools config (config/tools/config.json)

```json
{
	"enabled_tool_groups": [
		"builtin",
		"custom",
		"db",
		"api",
		"notification",
		"calendar",
		"human_in_loop"
	]
}
```

## Notes

- Old CLI flags like --tools-only and --prompt are no longer used.
- Runtime behavior is config-driven.
- If Ollama is not running, startup will fail fast with a clear error.
