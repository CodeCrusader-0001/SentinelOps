from typing import TypedDict, List, Dict, Any, Optional

class InvestigationState(TypedDict):
    incident_id: str
    title: str
    severity: str
    status: str
    logs_data: List[Dict[str, Any]]
    anomalies_data: List[Dict[str, Any]]
    runbook_context: str
    investigation_report: Dict[str, Any]
    remediation_request_id: Optional[str]
    approval_status: str # "PENDING", "APPROVED", "REJECTED"
    remediation_executed: bool
    remediation_result: Dict[str, Any]
    recovery_verified: bool
    final_report: str
    step_history: List[str]
    error: Optional[str]

