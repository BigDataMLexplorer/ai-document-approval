from __future__ import annotations

import json
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "generated"


def doc_text(i: int, kind: str) -> str:
    qty = 2 + (i % 5)
    price = 10.0 + (i % 7)
    correct_line = qty * price
    line_total = correct_line
    subtotal = correct_line
    tax = round(subtotal * 0.1, 2)
    total = subtotal + tax
    signature = "present"
    low_conf = ""

    if kind == "total_mismatch":
        total += 7.0
    elif kind == "line_math_error":
        line_total += 5.0
        subtotal = line_total
        tax = round(subtotal * 0.1, 2)
        total = subtotal + tax
    elif kind == "missing_signature":
        signature = "missing"
    elif kind == "low_confidence":
        low_conf = "\nLOW_CONFIDENCE: total"

    return (
        f"PO: SYN-{1000+i}\n"
        f"Customer: Synthetic Customer {i%4+1}\n"
        f"Order Date: 2026-11-05\nCurrency: USD\n"
        f"ITEM|SKU-{i:03d}|Synthetic item {i}|{qty}|{price:.2f}|{line_total:.2f}\n"
        f"Subtotal: {subtotal:.2f}\nTax: {tax:.2f}\nTotal: {total:.2f}\n"
        f"Requested Delivery: 2026-11-12\nSignature: {signature}{low_conf}"
    )


def write_pdf(path: Path, text: str) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    y = 750
    for line in text.splitlines():
        c.drawString(72, y, line)
        y -= 18
    c.save()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    specs = (["clean"] * 12 + ["total_mismatch"] * 6 + ["line_math_error"] * 4 + ["missing_signature"] * 4 + ["low_confidence"] * 4)
    manifest = []
    for i, kind in enumerate(specs):
        text = doc_text(i, kind)
        path = OUT / f"case_{i:02d}_{kind}.pdf"
        write_pdf(path, text)
        manifest.append({
            "name": path.name,
            "kind": kind,
            "expected_status": "auto_approved" if kind == "clean" else "needs_review",
        })
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(manifest)} synthetic PDFs in {OUT}")


if __name__ == "__main__":
    main()
