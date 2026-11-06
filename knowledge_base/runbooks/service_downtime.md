# RUNBOOK: Service Downtime and Unscheduled Outages

## Identification
- Symptoms: HTTP 502 Bad Gateway, HTTP 503 Service Unavailable, health check failures, zero healthy upstream endpoints in load balancer.
- Severity: CRITICAL

## Root Causes
1. Unhandled fatal runtime exceptions triggering process crashes (SIGSEGV, SIGKILL).
2. Failed deployment or bad environment configuration / missing secrets.
3. Node eviction or kernel host hardware failures.
4. Cascading failures caused by dependent service outage.

## Investigation Steps
1. Review container exit codes and crash logs (`dmesg`, `journalctl`, `kubectl describe pod`).
2. Verify ingress controller routing tables and DNS resolution.
3. Check recent CI/CD deployments and configuration changes.
4. Execute synthetic health probes against service internal endpoints.

## Recommended Remediation Actions
1. Roll back to last verified good deployment image.
2. Restart application container instances or service daemon.
3. Re-inject missing configuration or rotate expired certificates.
4. Isolate failing node and reschedule pods on healthy hardware.

