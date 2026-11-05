from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "artifacts/evaluation.json").read_text(encoding="utf-8"))
    summary = payload["summary"]
    labels = ["Confidence only", "Controlled workflow"]
    unsafe = [
        summary["confidence_only_unsafe_auto_approvals"],
        summary["controlled_unsafe_auto_approvals"],
    ]

    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.patch.set_facecolor("#07101d")
    ax.set_facecolor("#091524")

    bars = ax.bar(
        labels,
        unsafe,
        width=0.58,
        color=["#d96a73", "#6f82ff"],
        edgecolor=["#ef8991", "#92a0ff"],
        linewidth=1.2,
    )

    ax.set_ylabel("Unsafe auto-approvals", color="#a9bbd2", fontsize=12)
    ax.set_title(
        "Deterministic validation prevents unsafe document approvals",
        color="#edf4ff",
        fontsize=18,
        fontweight="bold",
        pad=18,
    )
    ax.set_ylim(0, max(unsafe) + 3)
    ax.tick_params(axis="x", colors="#dce8f8", labelsize=12)
    ax.tick_params(axis="y", colors="#8fa4bf")
    ax.yaxis.grid(True, color="#203753", linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color("#284262")

    for bar, value in zip(bars, unsafe, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.3,
            str(value),
            ha="center",
            va="bottom",
            color="#edf4ff",
            fontsize=18,
            fontweight="bold",
        )

    ax.text(
        0.5,
        -0.18,
        "30 synthetic PDFs · confidence threshold + deterministic business validation + human review",
        transform=ax.transAxes,
        ha="center",
        color="#7f96b4",
        fontsize=10,
    )

    fig.tight_layout()
    out = ROOT / "artifacts" / "approval_safety.png"
    fig.savefig(out, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
