from __future__ import annotations

from email import policy
from email.parser import BytesParser
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".eml"}


def parse_bytes(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8")
    if suffix == ".pdf":
        with NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(content)
            tmp.flush()
            reader = PdfReader(tmp.name)
            pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages).strip()
        if not text:
            raise ValueError("PDF contains no extractable text; OCR/multimodal extraction is required")
        return text
    if suffix == ".eml":
        msg = BytesParser(policy=policy.default).parsebytes(content)
        body = msg.get_body(preferencelist=("plain",))
        text = body.get_content() if body else ""
        attachments: list[str] = []
        for part in msg.iter_attachments():
            if part.get_content_type() == "text/plain":
                attachments.append(part.get_content())
        combined = "\n\n".join([text, *attachments]).strip()
        if not combined:
            raise ValueError("Email contains no extractable plain-text content")
        return combined
    raise AssertionError("unreachable")


async def parse_upload(file: UploadFile) -> str:
    return parse_bytes(file.filename or "upload.txt", await file.read())
