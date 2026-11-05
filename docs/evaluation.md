# Evaluation

The first benchmark evaluates **routing safety**, not LLM extraction accuracy.

A generated corpus of 30 synthetic purchase-order PDFs contains:

- 12 clean orders
- 6 total mismatches
- 4 line-item arithmetic errors
- 4 missing signatures
- 4 low-confidence extraction markers

Two policies are compared:

1. **Confidence-only baseline** — automatically approve when extraction confidence is high.
2. **Controlled workflow** — require high confidence *and* deterministic business-rule validation.

This separation matters because an extraction model can be highly confident while faithfully extracting a document that contains inconsistent totals or missing approval information.
