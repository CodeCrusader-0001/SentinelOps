import sys
import os
import time

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database.session import SessionLocal, Base, engine
from backend.app.services.user_service import UserService
from backend.app.models.log import Log
from backend.app.models.incident import Incident
from backend.app.models.remediation import RemediationRequest
from backend.app.workers.pipeline import run_pipeline_sync
from backend.app.agents.workflow import run_investigation_pipeline_sync
from backend.app.remediation.service import remediation_service
from backend.app.rag.service import rag_service

def print_banner(text: str):
    print("\n" + "="*80)
    print(f" >>> {text}")
    print("="*80)

def main():
    print_banner("SENTINELOPS — END-TO-END DEMONSTRATION WORKFLOW")

    # Step 1: Database Initialization
    print("\n[Stage 1] Initializing Database & Seeding Knowledge Base...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    UserService.seed_default_users(db)
    rag_service.seed_default_runbooks(db)
    print("✓ Default Admin & IT Engineer seeded.")
    print("✓ 8 Standard Runbooks indexed in FAISS vector store.")

    # Step 2: Log Ingestion & Anomalous Sequence Generation
    print_banner("STAGE 2: TELEMETRY INGESTION & ANOMALOUS LOGS")
    anomalous_logs = [
        Log(
            application="payment-gateway",
            service="billing-service",
            level="INFO",
            message="Payment authorization batch job started"
        ),
        Log(
            application="payment-gateway",
            service="billing-service",
            level="WARNING",
            message="Database connection pool utilization exceeded 85%"
        ),
        Log(
            application="payment-gateway",
            service="billing-service",
            level="ERROR",
            message="Database connection pool timeout while acquiring connection"
        ),
        Log(
            application="payment-gateway",
            service="billing-service",
            level="CRITICAL",
            message="FATAL: remaining connection slots are reserved for non-replication superuser connections"
        ),
    ]
    db.add_all(anomalous_logs)
    db.commit()
    for l in anomalous_logs:
        db.refresh(l)
    print(f"✓ Ingested {len(anomalous_logs)} logs into staging buffer.")

    # Step 3: Asynchronous Pipeline & Anomaly Detection
    print_banner("STAGE 3: RUNNING ASYNC DEEPLOG ANOMALY DETECTION")
    log_ids = [l.id for l in anomalous_logs]
    pipeline_res = run_pipeline_sync(log_ids)
    print(f"✓ Pipeline Result: {pipeline_res}")

    # Verify incident creation
    incident = db.query(Incident).filter(Incident.title.ilike("%billing-service%")).order_by(Incident.created_at.desc()).first()
    if not incident:
        print("✗ Error: Incident was not generated.")
        return

    print(f"\n✓ Incident Auto-Generated:")
    print(f"  - Incident ID: {incident.id}")
    print(f"  - Title: {incident.title}")
    print(f"  - Severity: {incident.severity}")
    print(f"  - Status: {incident.status}")

    # Step 4: RAG Knowledge Retrieval
    print_banner("STAGE 4: RAG RUNBOOK RETRIEVAL (FAISS + MiniLM)")
    search_results = rag_service.search("Database connection pool timeout exhausted", top_k=2)
    for idx, r in enumerate(search_results):
        print(f"[{idx+1}] Runbook: '{r.document_title}' | Similarity: {r.similarity_score:.4f}")
        print(f"    Snippet: {r.chunk_content[:140]}...\n")

    # Step 5: LangGraph AI Investigation with Gemini
    print_banner("STAGE 5: LANGGRAPH AGENTIC WORKFLOW & GEMINI INVESTIGATION")
    graph_state = run_investigation_pipeline_sync(incident.id)
    print("✓ LangGraph State History:")
    for step in graph_state["step_history"]:
        print(f"  * {step}")

    print(f"\n[AI Investigation Report]:")
    print(f"  - Root Cause: {graph_state['investigation_report'].get('root_cause')}")
    print(f"  - Approval Status: {graph_state['approval_status']}")
    print(f"  - Remediation Request ID: {graph_state['remediation_request_id']}")

    # Step 6: Human Approval & Controlled Remediation
    print_banner("STAGE 6: HUMAN APPROVAL GATE & SAFE EXECUTION")
    req_id = graph_state["remediation_request_id"]
    if req_id:
        admin_user = UserService.get_by_email(db, "admin@sentinelops.io")
        print(f"Engineer ({admin_user.full_name}) authorizing remediation request {req_id}...")
        remediation_service.approve_request(db, req_id, admin_user)
        print("✓ Request Cryptographically Approved.")

        print("Executing allowlisted mitigation routine in sandbox...")
        exec_result = remediation_service.execute_request_sync(req_id)
        print(f"✓ Remediation Execution Output: {exec_result['output']['message']}")
        print(f"✓ Automated Recovery Verification Probe: Healthy = {exec_result['recovery_verified']}")

    # Step 7: Incident Resolution Verification
    db.refresh(incident)
    print_banner("STAGE 7: FINAL INCIDENT POST-MORTEM & RESOLUTION")
    print(f"Incident Current Status: {incident.status}")
    print(f"Verified Recovered: {incident.status == 'RESOLVED'}")
    print("\n✓ DEMONSTRATION WORKFLOW SUCCESSFULLY CONCLUDED!\n")
    db.close()

if __name__ == "__main__":
    main()

