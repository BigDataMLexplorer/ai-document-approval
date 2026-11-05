from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.extraction.demo import DeterministicDemoExtractor
from app.models import DocumentCase, HumanReviewRequest
from app.parsers import parse_upload
from app.workflow.engine import DocumentWorkflow

router = APIRouter()
workflow = DocumentWorkflow(DeterministicDemoExtractor())


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/documents/process", response_model=DocumentCase)
def process_document(source_text: str) -> DocumentCase:
    try:
        return workflow.process(source_text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/documents/upload", response_model=DocumentCase)
async def upload_document(file: UploadFile = File(...)) -> DocumentCase:
    try:
        source_text = await parse_upload(file)
        return workflow.process(source_text)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/documents/{case_id}", response_model=DocumentCase)
def get_case(case_id: UUID) -> DocumentCase:
    try:
        return workflow.cases[case_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


@router.post("/documents/{case_id}/review", response_model=DocumentCase)
def review_case(case_id: UUID, review: HumanReviewRequest) -> DocumentCase:
    try:
        return workflow.review(case_id, review)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
