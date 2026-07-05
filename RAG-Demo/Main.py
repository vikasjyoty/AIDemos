from __future__ import annotations

from pathlib import Path

from LlmRag import query_llm_with_chroma_rag


def get_user_question() -> str:
	"""Read one user question from terminal input."""
	question = input("\nAsk a question (or type 'exit'): ").strip()
	return question


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
	print("Default LLM provider is local Ollama (model: qwen2.5:7b-instruct).")
	print("If you want OpenAI instead, set LLM provider in code and configure OPENAI_API_KEY.")

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
