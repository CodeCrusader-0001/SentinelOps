import pytest
from backend.app.ai.mock_provider import MockLLMProvider
from backend.app.ai.schemas import InvestigationResultSchema
from backend.app.ai.investigation_service import AIInvestigationService
from backend.app.database.session import SessionLocal
from backend.app.models.incident import Incident
from backend.app.models.log import Log

def test_mock_llm_structured_generation():
    provider = MockLLMProvider()
    result: InvestigationResultSchema = provider.generate_structured(
        prompt="Sample test incident prompt",
        response_model=InvestigationResultSchema
    )
    assert result.executive_summary is not None
    assert "Database" in result.root_cause or "billing-service" in result.executive_summary
    assert len(result.recommended_actions) >= 1
    assert result.recommended_actions[0].action_type in [
        "restart_service", "clear_cache", "scale_workers", "run_health_check"
    ]

def test_ai_investigation_service_persists_report():
    db = SessionLocal()
    try:
        # Create test incident with logs
        incident = Incident(
            title="Redis Cluster Degradation Outage",
            description="Session validation timeouts due to high Redis memory usage.",
            severity="HIGH",
            status="OPEN",
            source="Redis Monitor"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        log = Log(
            application="session-service",
            service="redis-cluster",
            level="ERROR",
            message="OOM command not allowed when used memory > 'maxmemory'",
            incident_id=incident.id
        )
        db.add(log)
        db.commit()

        # Run investigation with Mock Provider
        service = AIInvestigationService(provider=MockLLMProvider())
        report = service.investigate_incident(db, incident.id)

        assert report is not None
        assert report.incident_id == incident.id
        assert report.executive_summary is not None
        assert report.confidence_score > 0.5
        assert len(report.recommended_actions) >= 1
    finally:
        db.close()

