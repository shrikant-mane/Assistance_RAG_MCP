import json

from app import retrieval
from app.logs import get_logger

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("My_Company_Assistance")

logger = get_logger(__name__)

# ---------------------------- TOOLS ----------------------------
@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> str:
    """Semantic search: return the top_k chunks most similar to the query (JSON text)."""
    return json.dumps(retrieval.semantic_search(query, top_k))


@mcp.tool()
def list_documents() -> str:
    """List all uploaded documents with their chunk counts (JSON text)."""
    data = json.dumps(retrieval.list_documents())
    
    return json.dumps(retrieval.list_documents())


# --------------------------- RESOURCES --------------------------
@mcp.resource("docs://documents")
def documents_catalog() -> str:
    """Catalog of all uploaded documents."""
    return json.dumps(retrieval.list_documents())


@mcp.resource("docs://documents/{source}")
def read_document(source: str) -> str:
    """All chunks of one uploaded document, in reading order."""
    return json.dumps(retrieval.get_document_chunks(source))


# ---------------------------- PROMPTS ---------------------------
@mcp.prompt()
def answer_from_context(question: str, context: str) -> str:
    """Prompt template that turns retrieved chunks into a readable answer."""
    return (
        "You are My Company Assistant. Answer the employee's question using ONLY "
        "the context below, which comes from company documents.\n"
        "- Write a clear, friendly, human-readable answer.\n"
        "- If the context does not contain the answer, say you could not find it "
        "in the uploaded documents. Do not make anything up.\n"
        "- Mention the document name(s) you used at the end.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "ANSWER:"
    )


if __name__ == "__main__":
    mcp.run()  # stdio transport
