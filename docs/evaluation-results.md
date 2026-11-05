# Measured safety-routing benchmark

The first benchmark intentionally measures **workflow safety**, not LLM extraction accuracy.

## Dataset

30 generated synthetic purchase-order PDFs:

| Failure mode | Cases |
| --- | ---: |
| Clean | 12 |
| Incorrect document total | 6 |
| Incorrect line-item arithmetic | 4 |
| Missing signature | 4 |
| Low extraction confidence | 4 |

## Policies compared

**Confidence-only baseline** automatically approves any extraction whose minimum field confidence is at least the configured threshold. It performs no independent business-rule validation.

**Controlled workflow** requires sufficient confidence and deterministic validation of totals, line-item arithmetic, required fields and signatures. Otherwise the document is routed to human review.

## Measured result

| Metric | Result |
| --- | ---: |
| Controlled routing accuracy | **100%** |
| Controlled unsafe auto-approvals | **0 / 30** |
| Confidence-only unsafe auto-approvals | **14 / 30** |
| Review recall | **100%** |
| Auto-approval precision | **100%** |

The confidence-only policy failed because the extractor can be highly confident while faithfully extracting a document that itself contains inconsistent totals or is missing required approval information.

The result demonstrates the architecture choice rather than claiming universal document-AI accuracy: model confidence is not a substitute for deterministic business validation.

## Limitations

- The documents and failure modes are synthetic.
- The dependency-free demo extractor is not used as evidence of LLM extraction quality.
- Model-backed extraction accuracy should be evaluated separately on a labeled document set before production use.
- OCR and handwriting quality depend on the chosen multimodal/OCR provider and are intentionally not hidden behind fabricated metrics.
