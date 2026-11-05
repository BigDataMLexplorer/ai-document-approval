from __future__ import annotations

import json
from pathlib import Path

from app.extraction.demo import DeterministicDemoExtractor
from app.parsers import parse_bytes
from app.workflow.engine import DocumentWorkflow

ROOT = Path(__file__).resolve().parents[1]


def div(a: int, b: int) -> float:
    return a / b if b else 0.0


def main() -> None:
    generated = ROOT / "data" / "generated"
    manifest = json.loads((generated / "manifest.json").read_text(encoding="utf-8"))
    workflow = DocumentWorkflow(DeterministicDemoExtractor())
    rows = []
    controlled_correct = 0
    unsafe_auto = 0
    baseline_unsafe_auto = 0
    review_tp = 0
    review_fn = 0
    auto_tp = 0
    auto_fp = 0

    for item in manifest:
        path = generated / item["name"]
        text = parse_bytes(path.name, path.read_bytes())
        case = workflow.process(text)
        predicted = case.status.value
        expected = item["expected_status"]
        controlled_correct += predicted == expected
        unsafe = predicted == "auto_approved" and expected != "auto_approved"
        unsafe_auto += unsafe

        # Naive baseline: trust extraction confidence only, ignore business-rule validation.
        baseline_pred = "auto_approved" if case.extraction.min_confidence >= workflow.threshold else "needs_review"
        baseline_unsafe_auto += baseline_pred == "auto_approved" and expected != "auto_approved"

        if expected == "needs_review":
            if predicted == "needs_review":
                review_tp += 1
            else:
                review_fn += 1
        else:
            if predicted == "auto_approved":
                auto_tp += 1
            else:
                auto_fp += 1

        rows.append({
            "name": item["name"],
            "kind": item["kind"],
            "expected": expected,
            "controlled": predicted,
            "confidence_only_baseline": baseline_pred,
            "issues": [x.code for x in case.decision.issues],
            "min_confidence": case.decision.min_confidence,
        })

    summary = {
        "cases": len(manifest),
        "controlled_routing_accuracy": div(controlled_correct, len(manifest)),
        "controlled_unsafe_auto_approvals": unsafe_auto,
        "confidence_only_unsafe_auto_approvals": baseline_unsafe_auto,
        "review_recall": div(review_tp, review_tp + review_fn),
        "auto_approval_precision": div(auto_tp, auto_tp + auto_fp),
    }
    payload = {"summary": summary, "cases": rows}
    out = ROOT / "artifacts" / "evaluation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
