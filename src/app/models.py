from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class ReviewStatus(str, Enum):
    AUTO_APPROVED = "auto_approved"
    NEEDS_REVIEW = "needs_review"
    HUMAN_APPROVED = "human_approved"
    REJECTED = "rejected"


class LineItem(BaseModel):
    sku: str
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    line_total: float = Field(ge=0)


class PurchaseOrder(BaseModel):
    po_number: str
    customer_name: str
    order_date: date
    currency: str = Field(min_length=3, max_length=3)
    line_items: list[LineItem]
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0)
    total: float = Field(ge=0)
    requested_delivery_date: date | None = None
    signature_present: bool = False


class FieldConfidence(BaseModel):
    field: str
    confidence: float = Field(ge=0, le=1)


class ExtractionResult(BaseModel):
    document: PurchaseOrder
    field_confidences: list[FieldConfidence] = Field(default_factory=list)
    model_name: str = "deterministic-demo"

    @property
    def min_confidence(self) -> float:
        return min((x.confidence for x in self.field_confidences), default=1.0)


class ValidationIssue(BaseModel):
    code: str
    message: str
    field: str | None = None
    severity: str = "error"


class WorkflowDecision(BaseModel):
    status: ReviewStatus
    issues: list[ValidationIssue] = Field(default_factory=list)
    min_confidence: float
    reason: str


class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    event_type: str
    payload: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentCase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_text: str
    extraction: ExtractionResult | None = None
    decision: WorkflowDecision | None = None
    status: ReviewStatus | None = None
    audit: list[AuditEvent] = Field(default_factory=list)


class HumanReviewRequest(BaseModel):
    approved: bool
    edited_document: PurchaseOrder | None = None
    note: str | None = None

    @model_validator(mode="after")
    def edited_doc_only_when_approved(self):
        if not self.approved and self.edited_document is not None:
            raise ValueError("edited_document is only valid when approved=true")
        return self
