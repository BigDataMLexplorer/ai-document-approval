from __future__ import annotations

import re
from datetime import date

from app.models import ExtractionResult, FieldConfidence, LineItem, PurchaseOrder


def _money(value: str) -> float:
    return float(value.replace(",", "").strip())


class DeterministicDemoExtractor:
    """Dependency-free extractor for the public demo and safety-pipeline tests.

    The production-facing interface is provider-agnostic. A PydanticAI extractor can
    replace this class without changing validation, approval, or audit logic.
    """

    def extract(self, text: str) -> ExtractionResult:
        def grab(pattern: str, default: str = "") -> str:
            match = re.search(pattern, text, flags=re.I | re.M)
            return match.group(1).strip() if match else default

        po_number = grab(r"^PO(?: Number)?:\s*(.+)$")
        customer = grab(r"^Customer:\s*(.+)$")
        order_date = date.fromisoformat(grab(r"^Order Date:\s*(\d{4}-\d{2}-\d{2})$"))
        currency = grab(r"^Currency:\s*([A-Z]{3})$", "USD")
        subtotal = _money(grab(r"^Subtotal:\s*([0-9.,]+)$", "0"))
        tax = _money(grab(r"^Tax:\s*([0-9.,]+)$", "0"))
        total = _money(grab(r"^Total:\s*([0-9.,]+)$", "0"))
        delivery_raw = grab(r"^Requested Delivery:\s*(\d{4}-\d{2}-\d{2})$")
        signature = grab(r"^Signature:\s*(present|missing)$", "missing").lower() == "present"

        items: list[LineItem] = []
        for m in re.finditer(
            r"^ITEM\|([^|]+)\|([^|]+)\|([0-9.]+)\|([0-9.]+)\|([0-9.]+)$",
            text,
            flags=re.M,
        ):
            items.append(
                LineItem(
                    sku=m.group(1).strip(),
                    description=m.group(2).strip(),
                    quantity=float(m.group(3)),
                    unit_price=float(m.group(4)),
                    line_total=float(m.group(5)),
                )
            )

        low_fields = set(re.findall(r"^LOW_CONFIDENCE:\s*(.+)$", text, flags=re.I | re.M))
        key_fields = [
            "po_number", "customer_name", "order_date", "currency", "line_items",
            "subtotal", "tax", "total", "requested_delivery_date", "signature_present",
        ]
        confidences = [
            FieldConfidence(field=f, confidence=0.62 if f in low_fields else 0.98)
            for f in key_fields
        ]
        return ExtractionResult(
            document=PurchaseOrder(
                po_number=po_number,
                customer_name=customer,
                order_date=order_date,
                currency=currency,
                line_items=items,
                subtotal=subtotal,
                tax=tax,
                total=total,
                requested_delivery_date=date.fromisoformat(delivery_raw) if delivery_raw else None,
                signature_present=signature,
            ),
            field_confidences=confidences,
            model_name="deterministic-demo",
        )
