from __future__ import annotations

from app.models import ExtractionResult, FieldConfidence, PurchaseOrder


class PydanticAIExtractor:
    """Optional model-backed structured extractor.

    Import is delayed so the repository still runs without paid-model dependencies.
    """

    def __init__(self, model: str):
        from pydantic_ai import Agent

        self.model = model
        self.agent = Agent(
            model,
            output_type=PurchaseOrder,
            instructions=(
                "Extract only facts explicitly present in the purchase-order text. "
                "Never repair arithmetic or invent missing values. Preserve the stated values "
                "so deterministic validators can detect inconsistencies."
            ),
        )

    def extract(self, text: str) -> ExtractionResult:
        result = self.agent.run_sync(text).output
        return ExtractionResult(
            document=result,
            field_confidences=[
                FieldConfidence(field=name, confidence=0.90)
                for name in result.model_fields
            ],
            model_name=self.model,
        )
