from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Dict, Any

class RecommendedRemediationAction(BaseModel):
    action_type: str = Field(
        default="run_health_check",
        description="One of: restart_service, clear_cache, scale_workers, run_health_check"
    )
    target_service: str = Field(default="system-service", description="Target service identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(default="Automated mitigation action", description="Technical justification for this action")
    risk_level: str = Field(default="LOW", description="LOW, MEDIUM, or HIGH")
    requires_approval: bool = Field(default=True, description="Always true for safe operations")

class InvestigationResultSchema(BaseModel):
    executive_summary: str = Field(default="", description="Concise 2-3 sentence overview for on-call engineers")
    root_cause: str = Field(default="Root cause under investigation.", description="Detailed technical root cause analysis based on log evidence and runbooks")
    supporting_evidence: List[str] = Field(default_factory=list, description="Concrete log snippets and metrics proving the root cause")
    relevant_runbooks: List[str] = Field(default_factory=list, description="Titles of runbooks referenced")
    recommended_actions: List[RecommendedRemediationAction] = Field(
        default_factory=list,
        description="Allowed safe simulated remediation actions"
    )
    severity_assessment: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, or CRITICAL")
    risk_assessment: str = Field(default="LOW", description="Risk of system impact (LOW, MEDIUM, HIGH)")
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence in root cause (0-1)")
    uncertainty_notes: Optional[str] = Field(default=None, description="Ambiguities or alternative hypotheses")
    missing_information: Optional[str] = Field(default=None, description="Telemetry data not available in logs")
    post_mortem: Optional[str] = Field(default=None, description="Lessons learned and preventive engineering measures")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        # Handle field aliases from LLMs
        if "executive_summary" not in data or not data["executive_summary"]:
            data["executive_summary"] = data.get("summary") or data.get("overview") or data.get("description") or "Automated investigation report generated."
        if "root_cause" not in data or not data["root_cause"]:
            data["root_cause"] = data.get("root_cause_analysis") or data.get("cause") or "Root cause under active investigation."
        if "supporting_evidence" not in data:
            data["supporting_evidence"] = data.get("evidence") or data.get("findings") or []
        if isinstance(data.get("supporting_evidence"), str):
            data["supporting_evidence"] = [data["supporting_evidence"]]
        if isinstance(data.get("risk_assessment"), dict):
            data["risk_assessment"] = str(data["risk_assessment"].get("impact") or data["risk_assessment"].get("level") or "MEDIUM")
        return data

    model_config = ConfigDict(extra="ignore")

