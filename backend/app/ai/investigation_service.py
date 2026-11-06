from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.ai.base import BaseLLMProvider
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.ai.mock_provider import MockLLMProvider
from backend.app.ai.schemas import InvestigationResultSchema
from backend.app.ai.prompts import SYSTEM_INVESTIGATION_PROMPT, build_investigation_prompt
from backend.app.models.incident import Incident
from backend.app.models.investigation import InvestigationReport
from backend.app.rag.service import rag_service
from backend.app.core.config import settings
from backend.app.core.logging import logger

class AIInvestigationService:
    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        if provider:
            self.provider = provider
        elif settings.GEMINI_API_KEY:
            self.provider = GeminiProvider()
        else:
            self.provider = MockLLMProvider()

    def investigate_incident(self, db: Session, incident_id: str) -> Optional[InvestigationReport]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            logger.error(f"Incident {incident_id} not found for investigation.")
            return None

        # 1. Collate Log Evidence
        logs = incident.logs[:25] # Cap to recent 25 logs to prevent excessive prompt tokens
        logs_evidence = "\n".join(
            [f"[{l.timestamp}] [{l.level}] {l.service} ({l.hostname or 'unknown'}): {l.message}" for l in logs]
        ) or "No correlated logs attached to incident."

        # 2. Collate Anomaly Evidence
        anomalies = incident.anomalies
        anomalies_summary = "\n".join(
            [f"- Anomaly in {a.service}: Event {a.actual_event} (Score: {a.anomaly_score}). Evidence: {a.supporting_evidence}" for a in anomalies]
        ) or "No ML anomalies explicitly flagged."

        # 3. Retrieve Matching Runbooks via RAG
        search_query = f"{incident.title} {incident.description} {logs_evidence[:200]}"
        runbook_context = rag_service.get_runbook_context(search_query, top_k=2)

        # 4. Build Structured Prompt
        prompt = build_investigation_prompt(
            incident_title=incident.title,
            incident_description=incident.description,
            severity=incident.severity,
            source=incident.source,
            logs_evidence=logs_evidence,
            anomalies_summary=anomalies_summary,
            runbook_context=runbook_context
        )

        # 5. Call LLM Provider
        logger.info(f"Invoking LLM investigation for incident {incident_id}...")
        try:
            report_schema: InvestigationResultSchema = self.provider.generate_structured(
                prompt=prompt,
                response_model=InvestigationResultSchema,
                system_instruction=SYSTEM_INVESTIGATION_PROMPT
            )
        except Exception as e:
            logger.error(f"Gemini API failure during investigation: {e}. Falling back to mock generator.", exc_info=True)
            report_schema = MockLLMProvider().generate_structured(
                prompt=prompt,
                response_model=InvestigationResultSchema,
                system_instruction=SYSTEM_INVESTIGATION_PROMPT
            )

        # 6. Save or Update InvestigationReport in DB
        existing_report = db.query(InvestigationReport).filter(
            InvestigationReport.incident_id == incident.id
        ).first()

        recommended_actions_dict = [a.model_dump() for a in report_schema.recommended_actions]

        if existing_report:
            existing_report.executive_summary = report_schema.executive_summary
            existing_report.root_cause = report_schema.root_cause
            existing_report.supporting_evidence = report_schema.supporting_evidence
            existing_report.relevant_runbooks = report_schema.relevant_runbooks
            existing_report.recommended_actions = recommended_actions_dict
            existing_report.severity_assessment = report_schema.severity_assessment
            existing_report.risk_assessment = report_schema.risk_assessment
            existing_report.confidence_score = report_schema.confidence_score
            existing_report.uncertainty_notes = report_schema.uncertainty_notes
            existing_report.post_mortem = report_schema.post_mortem
            report_record = existing_report
        else:
            report_record = InvestigationReport(
                incident_id=incident.id,
                executive_summary=report_schema.executive_summary,
                root_cause=report_schema.root_cause,
                supporting_evidence=report_schema.supporting_evidence,
                relevant_runbooks=report_schema.relevant_runbooks,
                recommended_actions=recommended_actions_dict,
                severity_assessment=report_schema.severity_assessment,
                risk_assessment=report_schema.risk_assessment,
                confidence_score=report_schema.confidence_score,
                uncertainty_notes=report_schema.uncertainty_notes,
                post_mortem=report_schema.post_mortem
            )
            db.add(report_record)

        # Update incident status to INVESTIGATING
        if incident.status == "OPEN":
            incident.status = "INVESTIGATING"

        db.commit()
        db.refresh(report_record)
        logger.info(f"Persisted investigation report {report_record.id} for incident {incident_id}")
        return report_record

ai_investigation_service = AIInvestigationService()

