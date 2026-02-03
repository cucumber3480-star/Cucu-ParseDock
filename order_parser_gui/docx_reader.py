from docx import Document

def read_docx_paragraphs(path: str) -> list[str]:
    doc = Document(path)
    return [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
