# Strands Agent Basic Demo

This folder contains a minimal Strands SDK demo with both built-in and custom tools.

## What is included

- `main.py`: runs either a tools-only smoke test or a full agent call.
- `tools/builtin_tools.py`: inbuilt tools from `strands-agents-tools`.
- `tools/custom_tools.py`: custom tools created with `@tool`.
- `tools/__init__.py`: combines all tools into one list.

## Tools in this demo

Built-in tools:
- `calculator`
- `current_time`

Custom tools:
- `add_numbers`
- `reverse_text`
- `local_time`

## Setup

From workspace root:

```powershell
c:/Users/vikas/source/repos/AIDemos/.venv/Scripts/python.exe -m pip install -r Strands-Agent/requirements.txt
```

## Run

Tools-only check (no model required):

```powershell
c:/Users/vikas/source/repos/AIDemos/.venv/Scripts/python.exe Strands-Agent/main.py --tools-only
```

Agent run (requires model/provider credentials):

```powershell
c:/Users/vikas/source/repos/AIDemos/.venv/Scripts/python.exe Strands-Agent/main.py --prompt "Use tools to calculate 45*6 and give UTC time"
```

Optional model override:

```powershell
c:/Users/vikas/source/repos/AIDemos/.venv/Scripts/python.exe Strands-Agent/main.py --model "provider/model-name"
```
