from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "artifacts/evaluation.json").read_text(encoding="utf-8"))
    summary = payload["summary"]
    labels = ["Confidence only", "Controlled workflow"]
    unsafe = [summary["confidence_only_unsafe_auto_approvals"], summary["controlled_unsafe_auto_approvals"]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, unsafe)
    ax.set_ylabel("Unsafe auto-approvals")
    ax.set_title("Deterministic validation prevents unsafe document approvals")
    ax.set_ylim(0, max(unsafe) + 3)
    for bar, value in zip(bars, unsafe, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.25, str(value), ha="center", va="bottom")
    fig.tight_layout()
    out = ROOT / "artifacts" / "approval_safety.png"
    fig.savefig(out, dpi=180)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
