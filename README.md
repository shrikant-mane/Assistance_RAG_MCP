
# Assistance MCP RAG

An AI-powered company knowledge assistant built with **Python, FastAPI, RAG, PostgreSQL + pgvector, Google Gemini, and Model Context Protocol (MCP)**.

Upload company documents and ask questions about their contents. The application retrieves relevant document chunks using semantic search and uses Gemini to generate clear, context-based answers.

## Features

- **Document Upload:** Upload `.txt`, `.md`, `.pdf`, and `.docx` files.
- **Document Processing:** Extract text, split it into overlapping chunks, and generate embeddings.
- **Vector Search:** Store document embeddings in PostgreSQL using pgvector and retrieve relevant content.
- **AI-Powered Answers:** Use Google Gemini to generate answers based on retrieved context.
- **MCP Integration:** Expose document search and listing as MCP tools, document contents as resources, and answer generation instructions as prompts.
- **REST API:** Access the application through FastAPI and interactive Swagger documentation.

## Tech Stack

- Python
- FastAPI and Uvicorn
- SQLAlchemy
- PostgreSQL and pgvector
- Google Gemini API
- Model Context Protocol (MCP)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shrikant-mane/Assistance_MCP_RAG.git
cd Assistance_MCP_RAG
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv env
source env/bin/activate
```

**Windows**

```bash
python -m venv env
env\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/company_assistant

GEMINI_CHAT_MODEL=gemini-3.8-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=768
```

Replace the API key and database credentials with your actual values. Ensure PostgreSQL is running and the database exists.

The database must support the pgvector extension. Enable it if necessary:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Keep your `.env` file private and never commit API keys or database credentials to Git.

### 5. Run the application

From the project root, with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload
```

Open the following URLs:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Application root:** http://127.0.0.1:8000/

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check application status |
| POST | `/upload` | Upload and process a document |
| GET | `/documents` | List uploaded documents |
| GET | `/documents/{source}` | Read a document's stored chunks |
| POST | `/search` | Retrieve relevant document chunks |
| POST | `/ask` | Ask a question and receive a Gemini-generated answer |

For `/search` and `/ask`, use a JSON request body:

```json
{
  "query": "What is the company leave policy?",
  "top_k": 5
}
```

Use Swagger UI to upload files and test the endpoints interactively.

## Test the MCP Integration

Run the MCP client tests from the project root:

```bash
python -m test_mcp
```

The tests exercise document listing, document resource access, semantic search, and RAG prompt construction through the MCP client.

The server uses **stdio transport** when launched directly. The FastAPI application launches and communicates with the MCP server through its MCP client.

## How It Works

1. Upload a company document through the REST API.
2. Extract the text and split it into overlapping chunks.
3. Generate embeddings using Google's Gemini embedding model.
4. Store chunks and embeddings in PostgreSQL with pgvector.
5. Convert a user question into an embedding and retrieve relevant chunks.
6. Pass the retrieved context to the MCP prompt template.
7. Generate a readable, context-based answer using Gemini.

## Project Structure

```text
Assistance_MCP_RAG/
├── app/
│   ├── main.py          # FastAPI application and REST endpoints
│   ├── config.py        # Environment and application configuration
│   ├── ingestion.py     # Document ingestion pipeline
│   ├── retrieval.py     # Semantic search and document retrieval
│   ├── database.py      # Database models and connection
│   ├── gemini_client.py # Gemini embeddings and answer generation
│   ├── mcp_server.py    # MCP tools, resources, and prompts
│   └── mcp_client.py    # FastAPI-to-MCP communication
├── docs/                # Uploaded documents
├── sample_documents/    # Sample documents
├── requirements.txt
├── test_mcp.py
└── README.md
```

## Future Enhancements

- Hybrid search combining semantic and keyword retrieval.
- Authentication and role-based document access.
- Automated evaluation of retrieval quality and answer accuracy.
- Containerization and cloud deployment.

---

**Author:** [Shrikant Mane](https://github.com/shrikant-mane)
