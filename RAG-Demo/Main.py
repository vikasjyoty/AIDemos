from __future__ import annotations

import os
from pathlib import Path

from LlmRag import DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL, query_llm_with_chroma_rag


def get_user_question() -> str:
	"""Read one user question from terminal input."""
	question = input("\nAsk a question (or type 'exit'): ").strip()
	return question


def explain_model_options() -> None:
	"""Show simple explanation of local vs OpenAI options."""
	print("\n[INFO] Chat model options:")
	print("1) Local (Ollama): free to run, runs on your machine, no API key required.")
	print("2) OpenAI API: cloud model, requires OPENAI_API_KEY and paid API usage.")


def choose_provider_and_model() -> tuple[str, str]:
	"""Ask user to select provider and model for current CLI session."""
	explain_model_options()
	choice = input("Select provider [1=Local Ollama, 2=OpenAI] (default 1): ").strip() or "1"

	if choice == "2":
		model = input(f"OpenAI model (default {DEFAULT_OPENAI_MODEL}): ").strip() or DEFAULT_OPENAI_MODEL
		if not os.getenv("OPENAI_API_KEY"):
			print("[WARN] OPENAI_API_KEY not set. OpenAI calls will fail until you set it.")
		print(f"[OK] Using OpenAI provider with model: {model}")
		return "openai", model

	model = input(f"Ollama model (default {DEFAULT_OLLAMA_MODEL}): ").strip() or DEFAULT_OLLAMA_MODEL
	print(f"[OK] Using local Ollama provider with model: {model}")
	return "ollama", model


def run_rag_cli() -> None:
	"""
	Simple interactive loop for RAG Q&A.

	Why CLI loop:
	- Easy way to test retrieval + LLM flow while learning.

	Other options:
	- FastAPI/Flask endpoint
	- Streamlit/Gradio UI
	"""
	base_dir = Path(__file__).resolve().parent
	persist_directory = base_dir / "chroma_db"
	print(f"[INFO] Using Chroma path: {persist_directory}")

	print("RAG CLI is ready.")
	provider, model = choose_provider_and_model()

	while True:
		question = get_user_question()
		if question.lower() in {"exit", "quit"}:
			print("Exiting RAG CLI.")
			break

		if not question:
			print("Please enter a question.")
			continue

		try:
			print("[INFO] Sending question to RAG pipeline...")
			answer, chunks = query_llm_with_chroma_rag(
				user_question=question,
				persist_directory=persist_directory,
				collection_name="rag_docs",
				top_k=4,
				llm_provider=provider,
				llm_model_name=model,
			)
		except Exception as exc:
			print(f"Error: {exc}")
			continue

		print("\nAnswer:\n")
		print(answer)
		print("[OK] Answer generated.")

		if chunks:
			print("\nRetrieved sources:")
			for item in chunks:
				metadata = item.get("metadata", {})
				source = metadata.get("filename", "unknown")
				distance = item.get("distance", "n/a")
				print(f"- {source} (distance={distance})")


if __name__ == "__main__":
	run_rag_cli()
