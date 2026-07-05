from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import importlib
import re

from sentence_transformers import SentenceTransformer

from ChromaDbOps import ingest_chunks_to_chroma

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FILE_TYPES = {".txt", ".md", ".csv", ".pdf"}
CHUNK_SIZE = 256


def _split_sentences(text: str) -> List[str]:
	"""Simple sentence split for demo use."""
	print("[INFO] Splitting text into sentences...")
	cleaned = re.sub(r"\s+", " ", text).strip()
	if not cleaned:
		print("[INFO] No text found after cleanup.")
		return []
	sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", cleaned) if segment.strip()]
	print(f"[OK] Sentence count: {len(sentences)}")
	return sentences


def _read_text_file(file_path: Path) -> str:
	"""Read a text file in UTF-8 and skip invalid bytes for simple demos."""
	print(f"[INFO] Reading text file: {file_path.name}")
	text = file_path.read_text(encoding="utf-8", errors="ignore")
	print(f"[OK] Read {len(text)} characters from {file_path.name}")
	return text


def _read_pdf_file(file_path: Path) -> str:
	"""Extract text from a PDF file using pypdf."""
	print(f"[INFO] Reading PDF file: {file_path.name}")
	try:
		pypdf_module = importlib.import_module("pypdf")
	except ImportError as exc:
		raise ImportError("pypdf is required for PDF files. Install with: pip install pypdf") from exc

	reader = pypdf_module.PdfReader(str(file_path))
	print(f"[INFO] PDF page count: {len(reader.pages)}")
	pages: List[str] = []
	for page in reader.pages:
		pages.append(page.extract_text() or "")
	text = "\n".join(pages)
	print(f"[OK] Extracted {len(text)} characters from {file_path.name}")
	return text


def _chunk_text(text: str, tokenizer: object, chunk_size: int = CHUNK_SIZE) -> List[str]:
	"""
	Group full sentences until token limit is reached.

	Why tokenizer-based chunking:
	- Embedding models see tokens, not characters.
	- This gives more stable chunk sizes than plain character splitting.

	Other options:
	- Character windows (simpler but less token-accurate)
	- LangChain text splitters (more features, extra dependency)
	"""
	if chunk_size <= 0:
		raise ValueError("chunk_size must be > 0")
	print(f"[INFO] Chunking text with chunk size: {chunk_size}")

	sentences = _split_sentences(text)
	chunks: List[str] = []
	current_sentences: List[str] = []
	current_tokens = 0

	for sentence in sentences:
		sentence_tokens = len(tokenizer.tokenize(sentence))
		if current_sentences and (current_tokens + sentence_tokens > chunk_size):
			chunks.append(" ".join(current_sentences).strip())
			current_sentences = []
			current_tokens = 0

		current_sentences.append(sentence)
		current_tokens += sentence_tokens

	if current_sentences:
		chunks.append(" ".join(current_sentences).strip())

	result_chunks = [chunk for chunk in chunks if chunk]
	print(f"[OK] Chunk count generated: {len(result_chunks)}")
	return result_chunks


def load_docs_to_local_chroma(
	docs_directory: str | Path = "Docs",
	persist_directory: str | Path = "chroma_db",
	collection_name: str = "rag_docs",
	model_name: str = EMBEDDING_MODEL,
	chunk_size: int = CHUNK_SIZE,
) -> List[Dict[str, object]]:
	"""
	Read files from Docs, chunk text, then store vectors in local Chroma.

	This file handles file/chunk operations only.
	DB actions are delegated to ChromaDbOps.
	"""
	print("[INFO] Starting document load and ingestion...")
	base_dir = Path(__file__).resolve().parent
	docs_path = (base_dir / docs_directory).resolve() if not Path(docs_directory).is_absolute() else Path(docs_directory)
	persist_path = (base_dir / persist_directory).resolve() if not Path(persist_directory).is_absolute() else Path(persist_directory)

	if not docs_path.exists() or not docs_path.is_dir():
		raise ValueError(f"Invalid docs directory: {docs_path}")

	print(f"[OK] Docs folder found: {docs_path}")
	print(f"[INFO] Supported file types: {sorted(FILE_TYPES)}")

	model = SentenceTransformer(model_name)
	print(f"[OK] Loaded embedding model: {model_name}")
	tokenizer = model.tokenizer

	chunk_documents: List[Dict[str, object]] = []
	processed_files = 0

	for file_path in docs_path.rglob("*"):
		if (not file_path.is_file()) or (file_path.suffix.lower() not in FILE_TYPES):
			continue
		processed_files += 1
		print(f"[INFO] Processing file: {file_path.name}")

		if file_path.suffix.lower() == ".pdf":
			text = _read_pdf_file(file_path)
		else:
			text = _read_text_file(file_path)

		if not text.strip():
			print(f"[INFO] Skipped empty content: {file_path.name}")
			continue

		chunks = _chunk_text(text=text, tokenizer=tokenizer, chunk_size=chunk_size)
		for chunk_index, chunk_text in enumerate(chunks):
			chunk_documents.append(
				{
					"id": f"{file_path.stem}-{chunk_index}",
					"text": chunk_text,
					"metadata": {
						"source": str(file_path),
						"filename": file_path.name,
						"chunk_index": chunk_index,
					},
				}
			)

		print(f"[OK] Created {len(chunks)} chunk(s) from {file_path.name}")

	print(f"[OK] Processed files: {processed_files}")
	print(f"[OK] Total chunks created: {len(chunk_documents)}")

	ingest_chunks_to_chroma(
		chunk_documents=chunk_documents,
		persist_directory=persist_path,
		collection_name=collection_name,
		model_name=model_name,
	)
	print(f"[OK] Ingestion complete. Collection: {collection_name}")
	return chunk_documents


if __name__ == "__main__":
	# Running this file directly executes the complete sample flow.
	chunks = load_docs_to_local_chroma()
	print(f"Loaded and ingested {len(chunks)} chunks into local ChromaDB.")
