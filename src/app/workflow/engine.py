from __future__ import annotations

import os
from uuid import UUID

from app.extraction.base import DocumentExtractor
from app.models import AuditEvent, DocumentCase, HumanReviewRequest, ReviewStatus, WorkflowDecision
from app.validation.rules import validate_extraction


class DocumentWorkflow:
    def __init__(self, extractor: DocumentExtractor, auto_approve_confidence: float | None = None):
        self.extractor = extractor
        self.threshold = auto_approve_confidence or float(os.getenv("AUTO_APPROVE_CONFIDENCE", "0.92"))
        self.cases: dict[UUID, DocumentCase] = {}

    def process(self, source_text: str) -> DocumentCase:
        case = DocumentCase(source_text=source_text)
        case.audit.append(AuditEvent(document_id=case.id, event_type="received", payload={}))
        extraction = self.extractor.extract(source_text)
        case.extraction = extraction
        case.audit.append(
            AuditEvent(
                document_id=case.id,
                event_type="extracted",
                payload={"model": extraction.model_name, "min_confidence": extraction.min_confidence},
            )
        )
        issues = validate_extraction(extraction)
        blocking = [x for x in issues if x.severity == "error"]
        if blocking or extraction.min_confidence < self.threshold:
            reason = "validation_issues" if blocking else "low_confidence"
            status = ReviewStatus.NEEDS_REVIEW
        else:
            reason = "all_checks_passed"
            status = ReviewStatus.AUTO_APPROVED
        case.decision = WorkflowDecision(
            status=status,
            issues=issues,
            min_confidence=extraction.min_confidence,
            reason=reason,
        )
        case.status = status
        case.audit.append(
            AuditEvent(
                document_id=case.id,
                event_type="routed",
                payload={"status": status.value, "reason": reason, "issue_codes": [x.code for x in issues]},
            )
        )
        self.cases[case.id] = case
        return case

    def review(self, case_id: UUID, review: HumanReviewRequest) -> DocumentCase:
        case = self.cases[case_id]
        if case.status != ReviewStatus.NEEDS_REVIEW:
            raise ValueError("Only cases in needs_review state can be reviewed")
        if review.approved:
            if review.edited_document is not None and case.extraction is not None:
                case.extraction.document = review.edited_document
                edit_flag = True
            else:
                edit_flag = False
            case.status = ReviewStatus.HUMAN_APPROVED
            event = "human_approved"
        else:
            case.status = ReviewStatus.REJECTED
            edit_flag = False
            event = "human_rejected"
        case.audit.append(
            AuditEvent(
                document_id=case.id,
                event_type=event,
                payload={"edited": edit_flag, "note": review.note},
            )
        )
        return case
