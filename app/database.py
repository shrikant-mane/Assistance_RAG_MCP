from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.orm import declarative_base

from app import config

Base = declarative_base()


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(255), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(config.EMBEDDING_DIM), nullable=False)


_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(config.get_database_url(), pool_pre_ping=True)
    return _engine

def table_exists() -> bool:
    return inspect(get_engine()).has_table(DocumentChunk.__tablename__)


def create_table_if_needed() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)