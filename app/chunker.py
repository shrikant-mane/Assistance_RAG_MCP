import re

from app import config


def chunk_text(text: str, size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks: list[str] = []
    start = 0
    total = len(text)

    while start < total:
        end = min(start + size, total)

        # try to end the chunk at a space instead of in the middle of a word
        if end < total:
            cut = text.rfind(" ", start + size // 2, end)
            if cut != -1:
                end = cut

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= total:
            break
        start = max(end - overlap, start + 1)  # step back a little = overlap

    return chunks
