import random
import time
import requests
from typing import List, Dict, Any

BASE_URL = "http://127.0.0.1:8000/api/v1"

SCENARIOS = {
    "normal": [
        ("auth-service", "jwt-validator", "INFO", "User authentication token validated successfully"),
        ("checkout", "cart-service", "INFO", "Item added to active shopping cart"),
        ("payment-gateway", "stripe-client", "INFO", "Payment authorization token received from provider"),
        ("api-gateway", "reverse-proxy", "INFO", "HTTP 200 GET /api/v1/products latency=12ms"),
    ],
    "database_failure": [
        ("billing-service", "postgres-pool", "WARNING", "Database connection pool usage reached 85% capacity"),
        ("billing-service", "postgres-pool", "ERROR", "Timeout acquiring connection from pool: timeout=5000ms"),
        ("billing-service", "invoice-job", "CRITICAL", "Database connection pool exhausted: remaining connection slots are reserved for superuser"),
    ],
    "high_cpu": [
        ("recommendation-engine", "ml-serving", "WARNING", "Worker thread CPU utilization sustained > 92% across 8 cores"),
        ("recommendation-engine", "ml-serving", "ERROR", "Processing thread pool queue depth exceeded 1500 tasks, throttling incoming inference"),
    ],
    "memory_leak": [
        ("analytics-service", "session-aggregator", "WARNING", "JVM Old Gen Heap memory utilization > 88%"),
        ("analytics-service", "session-aggregator", "CRITICAL", "java.lang.OutOfMemoryError: Java heap space exhausted during settlement"),
    ],
    "api_latency": [
        ("api-gateway", "ingress-router", "WARNING", "p95 upstream response latency spike: 2450ms on /api/v1/orders"),
        ("api-gateway", "ingress-router", "ERROR", "HTTP 504 Gateway Timeout while awaiting downstream order-service"),
    ],
    "redis_failure": [
        ("session-service", "redis-cluster", "WARNING", "Redis cluster memory usage approaching maxmemory limit"),
        ("session-service", "redis-cluster", "CRITICAL", "ConnectionRefusedError: [Errno 111] Connection refused on 10.0.4.12:6379"),
    ],
    "worker_crash": [
        ("order-processor", "celery-worker-02", "WARNING", "Task order.process_payment exceeded soft time limit (240s)"),
        ("order-processor", "celery-worker-02", "CRITICAL", "WorkerLostError: Worker process exited prematurely with exitcode 137 (SIGKILL)"),
    ],
    "service_downtime": [
        ("notification-service", "email-sender", "WARNING", "Circuit breaker state changed to OPEN for sendgrid downstream"),
        ("notification-service", "email-sender", "CRITICAL", "HTTP 503 Service Unavailable: No healthy upstream hosts available"),
    ]
}

def generate_batch(scenario_name: str = "normal", count: int = 5) -> List[Dict[str, Any]]:
    logs = []
    templates = SCENARIOS.get(scenario_name, SCENARIOS["normal"])
    for _ in range(count):
        app, svc, lvl, msg = random.choice(templates)
        logs.append({
            "application": app,
            "service": svc,
            "level": lvl,
            "message": msg,
            "hostname": f"prod-{svc}-node{random.randint(1, 9):02d}",
            "metadata_json": {"scenario": scenario_name, "cluster": "us-west-2"}
        })
    return logs

def send_logs(logs: List[Dict[str, Any]]):
    try:
        resp = requests.post(f"{BASE_URL}/logs/batch", json={"logs": logs}, timeout=5)
        print(f"Sent {len(logs)} logs -> Status: {resp.status_code}")
    except Exception as e:
        print(f"Could not connect to SentinelOps API at {BASE_URL}: {e}")

if __name__ == "__main__":
    print("Generating simulated normal and anomalous logs...")
    for scenario in ["normal", "database_failure", "memory_leak", "redis_failure"]:
        batch = generate_batch(scenario, count=3)
        send_logs(batch)
        time.sleep(1)

