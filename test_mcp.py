
import asyncio
import logging

from app.mcp_client import (
    list_documents,
    read_document,
    search_chunks,
    build_rag_prompt,
)

logging.basicConfig(level=logging.INFO)


async def main():
    tests = [
        ("list_documents", lambda: list_documents()),
        ("read_document", lambda: read_document("leave_policy.txt")),
        ("search_chunks", lambda: search_chunks("leave policy", 3)),
        (
            "build_rag_prompt",
            lambda: build_rag_prompt("What is the leave policy?", 3),
        ),
    ]

    for name, call in tests:
        try:
            result = await call()
            print(f"\n{name}: SUCCESS")
            print(result)
        except Exception:
            logging.exception("%s FAILED", name)


if __name__ == "__main__":
    asyncio.run(main())
