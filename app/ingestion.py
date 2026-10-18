from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app import config
from app.file_reader import read_file
from app.chunker import chunk_text
from app.gemini_client import embed_texts
from app.database import create_table_if_needed, DocumentChunk, get_engine

def ingest_file(path: Path) -> dict:
    # 1. read the file
    text = read_file(path)

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No readable text found in this file.")


    vectors = embed_texts(chunks, task_type="RETRIEVAL_DOCUMENT")
    if len(vectors[0]) != config.EMBEDDING_DIM:
        raise ValueError(
            f"Embedding size is {len(vectors[0])} but EMBEDDING_DIM is {config.EMBEDDING_DIM}."
        )

    create_table_if_needed()
    rows = [
        DocumentChunk(source=path.name, chunk_index=i, content=chunk, embedding=vector)
        for i, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]


    with Session(get_engine()) as session:
        # re-uploading the same file name replaces its old chunks
        session.execute(delete(DocumentChunk).where(DocumentChunk.source == path.name))
        session.add_all(rows)
        session.commit()

    return {"source": path.name, "chunks_stored": len(rows)}
