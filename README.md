# AI Document Processing + Human Approval

An independently built portfolio project demonstrating a production-minded document automation workflow:

**PDF / email → structured extraction → deterministic validation → confidence routing → human approval → audit trail**

The repository uses only synthetic purchase-order data. No employer or client material is included.

## Why this project exists

Many document-AI systems become unsafe when the model is allowed to both interpret a document and decide whether its output should be acted on. This project separates those responsibilities:

- an extractor produces a typed `PurchaseOrder`
- deterministic validators recompute totals and enforce business rules
- low-confidence or invalid cases go to a human review queue
- humans approve, edit or reject
- every stage emits an audit event

## Current implementation

- FastAPI backend and portfolio demo UI
- PDF, TXT/Markdown and EML parsing
- typed Pydantic extraction schema
- provider-agnostic extractor interface
- dependency-free deterministic demo extractor
- optional PydanticAI structured extractor for real LLM providers
- arithmetic validation for line totals, subtotal and tax/total
- mandatory-field and signature validation
- confidence threshold routing
- human approve/edit/reject workflow
- audit events for extraction, routing and review
- generated synthetic PDF benchmark
- GitHub Actions CI and reproducible evaluation

## Safety benchmark

The synthetic benchmark deliberately separates **model confidence** from **business validity**. It compares:

1. a naive confidence-only policy
2. the controlled workflow using confidence + deterministic validation

This measures whether high-confidence but invalid documents are incorrectly auto-approved. See `docs/evaluation.md`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]' reportlab
python scripts/generate_synthetic_corpus.py
PYTHONPATH=src uvicorn app.main:app --reload
```

Open `http://localhost:8000/demo`.

## Run tests and evaluation

```bash
pytest -q
python scripts/generate_synthetic_corpus.py
PYTHONPATH=src python scripts/run_evaluation.py
```

## Design principle

LLMs are used for fuzzy interpretation. Conventional application logic owns deterministic checks and side effects. This makes it possible to audit why a document was automatically accepted, routed to review or rejected.
