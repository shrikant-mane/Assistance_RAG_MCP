"""
MCP CLIENT - used by the FastAPI app (Stage 2) to talk to the MCP server.
"""
import json
import os
import sys
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app import config
from app.logs import get_logger

logger = get_logger(__name__)


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,                 # the same Python that runs FastAPI
        args=["-m", "app.mcp_server"],
        cwd=str(config.PROJECT_ROOT),
        env=dict(os.environ),
    )



@asynccontextmanager
async def _open_session():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


def _text_of(result) -> str:
    text = result.content[0].text if result.content else ""    # type='text', text = []
    if result.is_error:
        raise RuntimeError(f"MCP tool failed: {text}")

    return text



async def list_documents() -> list[dict]:
    async with _open_session() as session:
        result = await session.call_tool("list_documents", {})
        
        return json.loads(_text_of(result))


async def read_document(source: str) -> list[dict]:
    """Read one document through an MCP RESOURCE."""
    async with _open_session() as session:
        result = await session.read_resource(f"docs://documents/{source}")
        return json.loads(result.contents[0].text)


async def search_chunks(query: str, top_k: int) -> list[dict]:
    """Semantic search through an MCP TOOL."""
    async with _open_session() as session:
        result = await session.call_tool("search_documents", {"query": query, "top_k": top_k})
        return json.loads(_text_of(result))


async def build_rag_prompt(question: str, top_k: int) -> tuple[list[dict], str]:
    """Search with the TOOL, then build the final prompt with the MCP PROMPT template.
    Returns (chunks, prompt). If nothing is stored yet, prompt is an empty string."""
    async with _open_session() as session:
        result = await session.call_tool("search_documents", {"query": question, "top_k": top_k})
        chunks = json.loads(_text_of(result))
        if not chunks:
            return [], ""

        context = "\n\n".join(
            f"[Source: {c['source']} | chunk {c['chunk_index']}]\n{c['content']}" for c in chunks
        )
        prompt = await session.get_prompt(
            "answer_from_context", {"question": question, "context": context}
        )
        return chunks, prompt.messages[0].content.text
