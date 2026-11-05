from __future__ import annotations

from typing import Protocol

from app.models import ExtractionResult


class DocumentExtractor(Protocol):
    def extract(self, text: str) -> ExtractionResult: ...
