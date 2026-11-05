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
- branded live dashboard and architecture assets captured in CI

## Measured safety benchmark

The checked-in benchmark contains **30 generated synthetic purchase-order PDFs**:

- 12 clean documents
- 6 incorrect document totals
- 4 line-item arithmetic errors
- 4 missing signatures
- 4 low-confidence cases

It compares a naive **confidence-only** policy with the controlled workflow using confidence **plus deterministic validation**.

| Metric | Result |
| --- | ---: |
| Controlled routing accuracy | **100%** |
| Controlled unsafe auto-approvals | **0 / 30** |
| Confidence-only unsafe auto-approvals | **14 / 30** |
| Human-review recall | **100%** |
| Auto-approval precision | **100%** |

The important result is not a claim of universal document-AI accuracy. It demonstrates that model confidence alone is insufficient to decide whether extracted business data is safe to act on. High-confidence documents can still contain inconsistent totals, arithmetic errors or missing required approval information.

See `docs/evaluation-results.md` for methodology and limitations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]' reportlab
python scripts/generate_synthetic_corpus.py
PYTHONPATH=src uvicorn app.main:app --reload
```

Open:

- `http://localhost:8000/demo` — live document review dashboard
- `http://localhost:8000/architecture` — portfolio architecture/process visual

## Run tests and evaluation

```bash
pytest -q
python scripts/generate_synthetic_corpus.py
PYTHONPATH=src python scripts/run_evaluation.py
PYTHONPATH=src python scripts/plot_evaluation.py
```

GitHub Actions also runs the complete test/evaluation flow and captures the live UI with Playwright.

## Design principle

**LLMs interpret; application logic validates and controls side effects.**

LLMs are used for fuzzy interpretation. Conventional application logic owns deterministic checks and side effects. This makes it possible to audit why a document was automatically accepted, routed to review or rejected.
