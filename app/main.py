import os
import re
from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app import config
from app import mcp_client
from app.gemini_client import generate_answer
from app.ingestion import ingest_file


app = FastAPI(
    title="My_Company_Assistance",
    description="RAG backend: upload company documents, search them, and ask questions.",
    version="1.0.0",
)

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["How many casual leaves do I get?"])
    top_k: int = Field(config.DEFAULT_TOP_K, ge=1, le=20)


def safe_filename(name: str)-> str:
    name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(name or "").name)
    return name.strip("._") and name


@app.get("/")
def home():
    return {"message": "My_Company_Assistance is running", "open_in_browser": "/docs"}




# ============================ STAGE 1 ============================
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    filename = safe_filename(file.filename)
    if not filename or Path(filename).suffix.lower() not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Allowed file types: {sorted(config.ALLOWED_EXTENSIONS)}")


    config.DOCS_DIR.mkdir(exist_ok=True)
    final_path = config.DOCS_DIR / filename
    temp_path = config.DOCS_DIR / f".{filename}.uploading"
    with open(temp_path, "wb") as out:
        shutil.copyfileobj(file.file, out)
    os.replace(temp_path, final_path)



    try:
        print("try")
        result = ingest_file(final_path)
        print(result)
    except Exception as e:
        raise HTTPException(500, f"File saved in /docs but processing failed: {e}")

    return {
        "message": "Success! File uploaded and stored in the database.",
        "file": result["source"],
        "saved_to": f"docs/{result['source']}",
        "chunks_stored": result["chunks_stored"],
    }


# ============================ STAGE 2 ============================

@app.get("/documents")
async def documents():
    """See all uploaded documents."""
    try:
        return {"documents": await mcp_client.list_documents()}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/documents/{source}")
async def read_document(source: str):
    """Read the data (chunks) stored for one document."""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", source):
        raise HTTPException(400, "Invalid document name.")
    try:
        chunks = await mcp_client.read_document(source)
    except Exception as e:
        raise HTTPException(500, str(e))
    if not chunks:
        raise HTTPException(404, f"No document named '{source}' found.")
    return {"source": source, "total_chunks": len(chunks), "chunks": chunks}


@app.post("/search")
async def search(req: QueryRequest):
    """Top-K matching chunks (raw, machine format) with source, index and score."""
    try:
        results = await mcp_client.search_chunks(req.query, req.top_k)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"query": req.query, "top_k": req.top_k, "results": results}


@app.post("/ask")
async def ask(req: QueryRequest):
    """Semantic search + Gemini -> human readable answer."""
    try:
        chunks, prompt = await mcp_client.build_rag_prompt(req.query, req.top_k)
    except Exception as e:
        raise HTTPException(500, str(e))

    if not chunks:
        return {"question": req.query, "answer": "No documents found yet. Please upload a document first.", "sources": []}

    try:
        answer = generate_answer(prompt)
    except Exception as e:
        raise HTTPException(502, f"Gemini API error: {e}")

    return {"question": req.query, "answer": answer, "sources": chunks}
