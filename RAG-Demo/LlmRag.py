from __future__ import annotations

import importlib
import os
import requests
from pathlib import Path
from typing import Dict, List, Tuple

from ChromaDbOps import retrieve_relevant_chunks

DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_OLLAMA_MODEL = "qwen2.5:7b-instruct"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def _build_context(chunks: List[Dict[str, object]], max_chars: int = 3500) -> str:
    """Join retrieved chunks into one context block for the LLM prompt."""
    print(f"[INFO] Building context from {len(chunks)} retrieved chunk(s)...")
    context_parts: List[str] = []
    used_chars = 0

    for item in chunks:
        text = str(item.get("text", "")).strip()
        if not text:
            continue

        source = str(item.get("metadata", {}).get("filename", "unknown"))
        part = f"[Source: {source}]\n{text}\n"
        if used_chars + len(part) > max_chars:
            break

        context_parts.append(part)
        used_chars += len(part)

    context = "\n".join(context_parts)
    print(f"[OK] Context built with {len(context)} characters.")
    return context


def _call_ollama(messages: List[Dict[str, str]], model_name: str) -> str:
    """Call local Ollama API and return model text with endpoint fallbacks."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    print(f"[INFO] Using Ollama host: {host}")
    print(f"[INFO] Calling Ollama model: {model_name}")

    # Try native Ollama chat endpoint first.
    response = requests.post(
        f"{host}/api/chat",
        json={"model": model_name, "messages": messages, "stream": False},
        timeout=120,
    )
    if response.ok:
        payload = response.json()
        content = payload.get("message", {}).get("content", "")
        if content:
            print("[OK] Received response from Ollama (/api/chat).")
            return content

    # Fallback for OpenAI-compatible endpoints exposed by some local runtimes.
    response_v1 = requests.post(
        f"{host}/v1/chat/completions",
        json={"model": model_name, "messages": messages, "temperature": 0.2},
        timeout=120,
    )
    if response_v1.ok:
        payload_v1 = response_v1.json()
        content_v1 = payload_v1.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content_v1:
            print("[OK] Received response from local OpenAI-compatible endpoint (/v1/chat/completions).")
            return content_v1

    # Final fallback to Ollama generate endpoint.
    prompt = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    response_generate = requests.post(
        f"{host}/api/generate",
        json={"model": model_name, "prompt": prompt, "stream": False},
        timeout=120,
    )
    if response_generate.ok:
        payload_generate = response_generate.json()
        content_generate = payload_generate.get("response", "")
        if content_generate:
            print("[OK] Received response from Ollama (/api/generate).")
            return content_generate

    raise ValueError(
        "Could not get a response from local LLM endpoint. Checked /api/chat, /v1/chat/completions, and /api/generate. "
        "Verify OLLAMA_HOST, ensure Ollama is running, and confirm the model is available with: ollama list"
    )


def _call_openai(messages: List[Dict[str, str]], model_name: str) -> str:
    """Call OpenAI chat completion API and return model text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables.")

    openai_module = importlib.import_module("openai")
    client = openai_module.OpenAI(api_key=api_key)

    print("[INFO] Using OpenAI provider (cloud API).")
    print(f"[INFO] Calling OpenAI model: {model_name}")
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.2,
    )

    content = response.choices[0].message.content or ""
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    print("[OK] Received response from OpenAI.")
    return content


def query_llm_with_chroma_rag(
    user_question: str,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = "rag_docs",
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    llm_model_name: str = DEFAULT_OLLAMA_MODEL,
    top_k: int = 4,
    llm_provider: str = DEFAULT_LLM_PROVIDER,
) -> Tuple[str, List[Dict[str, object]]]:
    """Retrieve from Chroma and ask an LLM (Ollama or OpenAI) with that context."""
    print("[INFO] Starting RAG query...")
    if not user_question.strip():
        print("[INFO] Empty question received.")
        return "Please ask a non-empty question.", []

    chunks = retrieve_relevant_chunks(
        query_text=user_question,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=embedding_model_name,
        top_k=top_k,
    )
    print(f"[OK] Retrieved chunks for prompt: {len(chunks)}")

    context = _build_context(chunks)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful RAG assistant. Use provided context first. "
                "If not enough context, clearly say what is missing."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question:\n{user_question}\n\n"
                f"Retrieved Context:\n{context if context else 'No context found.'}\n\n"
                "Answer briefly and mention source file names where possible."
            ),
        },
    ]

    selected_provider = llm_provider.lower().strip()
    print(f"[INFO] Selected LLM provider: {selected_provider}")
    if selected_provider == "ollama":
        answer = _call_ollama(messages=messages, model_name=llm_model_name)
    elif selected_provider == "openai":
        answer = _call_openai(messages=messages, model_name=llm_model_name)
    else:
        raise ValueError("Unsupported llm_provider. Use 'ollama' or 'openai'.")

    return answer, chunks
