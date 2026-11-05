from __future__ import annotations

from datetime import date, timedelta

from app.models import ExtractionResult, ValidationIssue

EPSILON = 0.01


def validate_extraction(result: ExtractionResult, *, today: date | None = None) -> list[ValidationIssue]:
    doc = result.document
    today = today or date.today()
    issues: list[ValidationIssue] = []

    if not doc.po_number.strip():
        issues.append(ValidationIssue(code="missing_po_number", field="po_number", message="PO number is missing."))
    if not doc.customer_name.strip():
        issues.append(ValidationIssue(code="missing_customer", field="customer_name", message="Customer name is missing."))
    if not doc.line_items:
        issues.append(ValidationIssue(code="missing_line_items", field="line_items", message="No line items were extracted."))

    calculated_subtotal = sum(item.line_total for item in doc.line_items)
    if abs(calculated_subtotal - doc.subtotal) > EPSILON:
        issues.append(
            ValidationIssue(
                code="subtotal_mismatch",
                field="subtotal",
                message=f"Line items sum to {calculated_subtotal:.2f}, document subtotal is {doc.subtotal:.2f}.",
            )
        )

    expected_total = doc.subtotal + doc.tax
    if abs(expected_total - doc.total) > EPSILON:
        issues.append(
            ValidationIssue(
                code="total_mismatch",
                field="total",
                message=f"Subtotal + tax is {expected_total:.2f}, document total is {doc.total:.2f}.",
            )
        )

    for idx, item in enumerate(doc.line_items):
        expected = item.quantity * item.unit_price
        if abs(expected - item.line_total) > EPSILON:
            issues.append(
                ValidationIssue(
                    code="line_total_mismatch",
                    field=f"line_items[{idx}].line_total",
                    message=f"{item.quantity} × {item.unit_price:.2f} != {item.line_total:.2f}.",
                )
            )

    if not doc.signature_present:
        issues.append(ValidationIssue(code="missing_signature", field="signature_present", message="Required signature is missing."))

    if doc.requested_delivery_date and doc.requested_delivery_date < today:
        issues.append(ValidationIssue(code="delivery_in_past", field="requested_delivery_date", message="Requested delivery date is already in the past."))
    elif doc.requested_delivery_date and doc.requested_delivery_date <= today + timedelta(days=2):
        issues.append(ValidationIssue(code="urgent_delivery", field="requested_delivery_date", message="Requested delivery is within two days.", severity="warning"))

    return issues
