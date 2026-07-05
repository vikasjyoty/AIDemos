# AIDemos

Hands-on AI demo projects focused on practical learning.

This repository currently includes a Python RAG (Retrieval-Augmented Generation) demo that:

1. Reads documents from a local folder
2. Chunks text using a tokenizer-aware strategy
3. Stores embeddings in local ChromaDB
4. Retrieves relevant chunks for a user question
5. Sends context to an LLM (Ollama by default)

## Project

- `RAG-Demo/`

## RAG Demo Overview

Main files:

1. `RAG-Demo/LoadDocs.py`
	- Loads files from `RAG-Demo/Docs`
	- Supports `.txt`, `.md`, `.csv`, `.pdf`
	- Chunks text and ingests vectors into ChromaDB

2. `RAG-Demo/ChromaDbOps.py`
	- Embedding creation
	- ChromaDB insert and retrieval

3. `RAG-Demo/LlmRag.py`
	- Builds RAG context
	- Calls LLM provider (default: Ollama)

4. `RAG-Demo/Main.py`
	- CLI interface for asking questions
	- Lets you choose provider and model at runtime

## Prerequisites

1. Python 3.10+
2. Ollama installed locally (for default free/local inference)
3. Windows PowerShell or CMD

## Setup

From repository root:

```powershell
cd c:\Users\vikas\source\repos\AIDemos
```

Create and activate virtual environment (if needed):

```powershell
python -m venv .venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .\.venv\Scripts\Activate.ps1)
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Ollama Setup (Default LLM Path)

Install Ollama:

```powershell
winget install Ollama.Ollama
```

Pull model used by the project:

```powershell
ollama pull qwen2.5:7b-instruct
```

Optional check:

```powershell
ollama list
```

## Run the RAG Demo

Move into the demo folder:

```powershell
cd .\RAG-Demo
```

1. Add your files to `RAG-Demo/Docs`
2. Ingest documents into local ChromaDB:

```powershell
python .\LoadDocs.py
```

3. Start the Q&A CLI:

```powershell
python .\Main.py
```

At startup, the CLI explains the options and asks you to choose:

1. Local Ollama provider
	- Free/local inference
	- No OpenAI API key required
	- Uses your selected local model (default shown in prompt)

2. OpenAI provider
	- Cloud model access
	- Requires `OPENAI_API_KEY`
	- Uses model you enter (default shown in prompt)

Type your question in terminal. Type `exit` to quit.

## Runtime Status Output

The scripts print step-by-step progress messages so you can see exactly what is happening:

1. File loading and parsing status
2. Sentence split and chunk counts
3. Embedding and Chroma upsert/retrieval status
4. Provider/model selection and LLM response status

## Optional: OpenAI Instead of Ollama

The code supports OpenAI as an alternate provider.

If you switch provider in code:

1. Set API key in terminal:

```powershell
$env:OPENAI_API_KEY="your_key_here"
```

2. Run `Main.py` normally.

## Troubleshooting

1. `Loaded and ingested 0 chunks`
	- Check that files exist in `RAG-Demo/Docs`
	- Ensure file types are supported
	- For PDFs, ensure text is extractable (not image-only scans)

2. `ollama` command not found
	- Restart terminal after install
	- Verify Ollama is installed and on PATH

3. Connection error to Ollama
	- Ensure Ollama is installed and running
	- Verify local API endpoint is reachable at `http://localhost:11434`

4. OpenAI call fails with missing API key
	- Set key first in PowerShell:
	- `$env:OPENAI_API_KEY="your_key_here"`

## Commit Hygiene

Generated runtime files are ignored to keep commits clean:

1. `RAG-Demo/chroma_db/`
2. `RAG-Demo/Results/`
3. `__pycache__/` and `*.pyc`
