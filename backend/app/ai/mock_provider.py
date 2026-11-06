from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from backend.app.ai.base import BaseLLMProvider
from backend.app.ai.schemas import InvestigationResultSchema, RecommendedRemediationAction

T = TypeVar("T", bound=BaseModel)

class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic mock provider for automated unit testing without consuming API quota.
    """
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        return "Deterministic Mock LLM Investigation Summary."

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        mock_data = {
            "executive_summary": "Simulated outage: Automated connection pool exhaustion detected in billing-service.",
            "root_cause": "Database connection pool saturated by spike in unclosed client sessions.",
            "supporting_evidence": [
                "Database connection pool timeout while acquiring connection",
                "Observed latency spike in transaction commit phase"
            ],
            "relevant_runbooks": ["Database Connection Failures"],
            "recommended_actions": [
                {
                    "action_type": "restart_service",
                    "target_service": "billing-service",
                    "parameters": {"service_name": "billing-service"},
                    "rationale": "Restart client application instance to cleanly release orphaned DB connections.",
                    "risk_level": "LOW",
                    "requires_approval": True
                }
            ],
            "severity_assessment": "HIGH",
            "risk_assessment": "MEDIUM",
            "confidence_score": 0.92,
            "uncertainty_notes": "None observed.",
            "missing_information": "PgBouncer active client metrics.",
            "post_mortem": "Enforce strict session context manager timeouts and increase pool headroom."
        }
        return response_model.model_validate(mock_data)

