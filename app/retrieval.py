from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import config
from app.database import DocumentChunk, get_engine, table_exists
from app.gemini_client import embed_texts
from app.logs import get_logger
logger = get_logger(__name__)


def list_documents() -> list[dict]:
    
    if not table_exists():
        return []
    stmt = (
        select(DocumentChunk.source, func.count(DocumentChunk.id))
        .group_by(DocumentChunk.source)
        .order_by(func.min(DocumentChunk.id))
    )
    with Session(get_engine()) as session:
        
        return [{"source": s, "chunks": n} for s, n in session.execute(stmt).all()]


def get_document_chunks(source: str) -> list[dict]:
    """All chunks of one document, in reading order."""
    if not table_exists():
        return []
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.source == source)
        .order_by(DocumentChunk.chunk_index)
    )
    with Session(get_engine()) as session:
        return [
            {"id": c.id, "source": c.source, "chunk_index": c.chunk_index, "content": c.content}
            for c in session.scalars(stmt).all()
        ]


def semantic_search(query: str, top_k: int = config.DEFAULT_TOP_K) -> list[dict]:
    """Embed the question and return the top_k most similar chunks."""
    if not table_exists():
        return []
    query_vector = embed_texts([query], task_type="RETRIEVAL_QUERY")[0]     #query_vector = [[]][0] => []

    distance = DocumentChunk.embedding.cosine_distance(query_vector)   

    # cosine_diatance comes from from pgvector.sqlalchemy import Vector
    stmt = select(DocumentChunk, distance.label("distance")).order_by(distance).limit(top_k)

    with Session(get_engine()) as session:
        rows = session.execute(stmt).all()          # rows = (chunk_obj, distance)
        return [
            {
                "id": chunk.id,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "score": round(1 - float(dist), 4),  # 1.0 = identical meaning
                "content": chunk.content,
            }
            for chunk, dist in rows
        ]


"""
ORM
# Using execute()
result = session.execute(select(DocumentChunk.source)).all()
# Output: [('leave_policy.txt',), ('expense_policy.txt',)]

# Using scalars()
result = session.scalars(select(DocumentChunk.source)).all()
# Output: ['leave_policy.txt', 'expense_policy.txt']

"""