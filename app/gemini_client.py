from google import genai
from google.genai import types

from app import config
from app.logs import get_logger

logger = get_logger(__name__)

_client = None
BATCH_SIZE = 50  # texts sent to the embedding API per request


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.require_gemini_key())
    return _client


def embed_texts(texts: list[str], task_type: str) -> list[list[float]]:
    client = _get_client()
    vectors: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = client.models.embed_content(
            model=config.GEMINI_EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=config.EMBEDDING_DIM,
            ),
        )
        vectors.extend([list(e.values) for e in response.embeddings])

    return vectors  # vectors = [[----]]


def generate_answer(prompt: str) -> str:

    client = _get_client()
    response = client.models.generate_content(
        model=config.GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip()