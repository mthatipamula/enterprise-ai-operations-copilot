from pathlib import Path
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """
    Represents a chunk of a source document that will eventually
    be embedded and stored in the vector database.
    """

    chunk_id: str
    source: str
    content: str


def load_documents(documents_dir: str = "documents") -> list[tuple[str, str]]:
    """
    Load Markdown documents from the documents directory.

    Returns:
        A list of tuples containing:
        (source_file_name, document_content)
    """

    documents_path = Path(documents_dir)

    if not documents_path.exists():
        raise FileNotFoundError(
            f"Documents directory does not exist: {documents_dir}"
        )

    documents = []

    for file_path in sorted(documents_path.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")

        if content.strip():
            documents.append((file_path.name, content))

    return documents


def chunk_document(
    source: str,
    content: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[DocumentChunk]:
    """
    Split a document into overlapping word-based chunks.

    chunk_size:
        Maximum number of words in each chunk.

    chunk_overlap:
        Number of words shared between consecutive chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    words = content.split()

    chunks = []
    start = 0
    chunk_number = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk_text = " ".join(words[start:end])

        chunks.append(
            DocumentChunk(
                chunk_id=f"{source}:{chunk_number}",
                source=source,
                content=chunk_text,
            )
        )

        chunk_number += 1

        if end == len(words):
            break

        start = end - chunk_overlap

    return chunks


def load_and_chunk_documents(
    documents_dir: str = "documents",
) -> list[DocumentChunk]:
    """
    Load all Markdown documents and split them into chunks.
    """

    documents = load_documents(documents_dir)

    all_chunks = []

    for source, content in documents:
        chunks = chunk_document(
            source=source,
            content=content,
        )

        all_chunks.extend(chunks)

    return all_chunks