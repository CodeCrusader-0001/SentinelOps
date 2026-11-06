from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from backend.app.agents.state import InvestigationState
from backend.app.database.session import SessionLocal
from backend.app.models.incident import Incident
from backend.app.ai.investigation_service import ai_investigation_service
from backend.app.rag.service import rag_service
from backend.app.remediation.service import remediation_service
from backend.app.core.logging import logger

def intake_node(state: InvestigationState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        if not incident:
            return {"error": "Incident not found", "step_history": state["step_history"] + ["Intake failed: Incident not found"]}
        
        logs_data = [
            {"id": l.id, "level": l.level, "service": l.service, "message": l.message, "timestamp": str(l.timestamp)}
            for l in incident.logs[:25]
        ]
        anomalies_data = [
            {"id": a.id, "service": a.service, "event": a.actual_event, "score": a.anomaly_score, "evidence": a.supporting_evidence}
            for a in incident.anomalies
        ]
        
        return {
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "logs_data": logs_data,
            "anomalies_data": anomalies_data,
            "step_history": state["step_history"] + ["1. Incident Intake completed"]
        }
    finally:
        db.close()

def context_retrieval_node(state: InvestigationState) -> Dict[str, Any]:
    query = f"{state.get('title', '')} {state.get('severity', '')}"
    if state.get("logs_data"):
        query += f" {state['logs_data'][0].get('message', '')}"
        
    context = rag_service.get_runbook_context(query, top_k=2)
    return {
        "runbook_context": context,
        "step_history": state["step_history"] + ["2. RAG Context Retrieval completed"]
    }

def log_analysis_node(state: InvestigationState) -> Dict[str, Any]:
    # Synthesize log anomaly observations
    log_count = len(state.get("logs_data", []))
    anom_count = len(state.get("anomalies_data", []))
    summary_step = f"3. Log Analysis completed ({log_count} logs, {anom_count} anomalies correlated)"
    return {
        "step_history": state["step_history"] + [summary_step]
    }

def root_cause_node(state: InvestigationState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        report = ai_investigation_service.investigate_incident(db, state["incident_id"])
        report_dict = {
            "executive_summary": report.executive_summary if report else "Investigation pending",
            "root_cause": report.root_cause if report else "Unknown",
            "recommended_actions": report.recommended_actions if report else []
        }
        return {
            "investigation_report": report_dict,
            "step_history": state["step_history"] + ["4. Root Cause Analysis generated with Gemini 3.8 Flash"]
        }
    finally:
        db.close()

def recommendation_node(state: InvestigationState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        actions = state.get("investigation_report", {}).get("recommended_actions", [])
        remediation_req_id = None
        
        if actions:
            first_action = actions[0]
            action_type = first_action.get("action_type", "run_health_check")
            params = first_action.get("parameters", {})
            target = first_action.get("target_service") or "system-service"
            params["target_service"] = target
            rationale = first_action.get("rationale", "Automated recommendation from AI Investigation.")

            req = remediation_service.create_request(
                db=db,
                incident_id=state["incident_id"],
                action_type=action_type,
                parameters=params,
                rationale=rationale,
                requested_by="LangGraph Agent"
            )
            remediation_req_id = req.id

        return {
            "remediation_request_id": remediation_req_id,
            "approval_status": "PENDING",
            "step_history": state["step_history"] + [f"5. Generated Remediation Proposal ({remediation_req_id})"]
        }
    finally:
        db.close()

def approval_gate_node(state: InvestigationState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        req_id = state.get("remediation_request_id")
        approval_status = "PENDING"
        if req_id:
            from backend.app.models.remediation import RemediationRequest
            req = db.query(RemediationRequest).filter(RemediationRequest.id == req_id).first()
            if req:
                approval_status = req.status

        # If still pending, pause the workflow and update incident to PENDING_APPROVAL
        if approval_status == "PENDING":
            incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
            if incident:
                incident.status = "PENDING_APPROVAL"
                db.commit()

        return {
            "approval_status": approval_status,
            "step_history": state["step_history"] + [f"6. Human Approval Gate evaluated: Status is {approval_status}"]
        }
    finally:
        db.close()

def controlled_remediation_node(state: InvestigationState) -> Dict[str, Any]:
    req_id = state.get("remediation_request_id")
    if not req_id:
        return {"remediation_executed": False, "step_history": state["step_history"] + ["7. Remediation skipped: No request"]}

    result = remediation_service.execute_request_sync(req_id)
    return {
        "remediation_executed": True,
        "remediation_result": result,
        "step_history": state["step_history"] + ["7. Controlled Remediation executed safely"]
    }

def recovery_verification_node(state: InvestigationState) -> Dict[str, Any]:
    verified = state.get("remediation_result", {}).get("recovery_verified", False)
    return {
        "recovery_verified": verified,
        "step_history": state["step_history"] + [f"8. Recovery Verification complete: Healthy={verified}"]
    }

def final_report_node(state: InvestigationState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        final_summary = (
            f"Investigation concluded for incident {state['incident_id']}.\n"
            f"Root Cause: {state.get('investigation_report', {}).get('root_cause', 'N/A')}\n"
            f"Remediation Executed: {state.get('remediation_executed', False)}\n"
            f"Recovery Verified: {state.get('recovery_verified', False)}"
        )
        if incident and state.get("recovery_verified", False):
            incident.status = "RESOLVED"
            db.commit()

        return {
            "final_report": final_summary,
            "step_history": state["step_history"] + ["9. Final Incident Post-Mortem Report generated"]
        }
    finally:
        db.close()

def check_approval_condition(state: InvestigationState) -> str:
    if state.get("approval_status") == "APPROVED":
        return "controlled_remediation"
    # If PENDING or REJECTED, pause or conclude early
    return "final_report"

# Construct LangGraph StateGraph
def create_investigation_graph():
    builder = StateGraph(InvestigationState)
    builder.add_node("intake", intake_node)
    builder.add_node("context_retrieval", context_retrieval_node)
    builder.add_node("log_analysis", log_analysis_node)
    builder.add_node("root_cause", root_cause_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("approval_gate", approval_gate_node)
    builder.add_node("controlled_remediation", controlled_remediation_node)
    builder.add_node("recovery_verification", recovery_verification_node)
    builder.add_node("final_report", final_report_node)

    # Edge wiring
    builder.set_entry_point("intake")
    builder.add_edge("intake", "context_retrieval")
    builder.add_edge("context_retrieval", "log_analysis")
    builder.add_edge("log_analysis", "root_cause")
    builder.add_edge("root_cause", "recommendation")
    builder.add_edge("recommendation", "approval_gate")
    
    # Conditional edge based on human approval
    builder.add_conditional_edges(
        "approval_gate",
        check_approval_condition,
        {
            "controlled_remediation": "controlled_remediation",
            "final_report": "final_report"
        }
    )
    
    builder.add_edge("controlled_remediation", "recovery_verification")
    builder.add_edge("recovery_verification", "final_report")
    builder.add_edge("final_report", END)

    return builder.compile()

investigation_workflow = create_investigation_graph()

def run_investigation_pipeline_sync(incident_id: str) -> Dict[str, Any]:
    initial_state: InvestigationState = {
        "incident_id": incident_id,
        "title": "",
        "severity": "",
        "status": "OPEN",
        "logs_data": [],
        "anomalies_data": [],
        "runbook_context": "",
        "investigation_report": {},
        "remediation_request_id": None,
        "approval_status": "PENDING",
        "remediation_executed": False,
        "remediation_result": {},
        "recovery_verified": False,
        "final_report": "",
        "step_history": [],
        "error": None
    }
    return investigation_workflow.invoke(initial_state)

