
from pathlib import Path

def read_file(path: Path) -> str:
    ext = path.suffix.lower()

    if ext in (".txt", ".md"):
        text = path.read_text(encoding="utf-8", errors="ignore")

    elif ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)

    elif ext == ".docx":
        from docx import Document

        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return text.replace("\x00", "")  
