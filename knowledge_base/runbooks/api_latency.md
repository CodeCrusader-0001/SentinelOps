# RUNBOOK: API Latency Spikes (p95/p99 Degradation)

## Identification
- Symptoms: `p95 latency > 2000ms`, `upstream request timeout (HTTP 504)`, Gateway Timeouts, client request cancellation.
- Severity: HIGH / MEDIUM

## Root Causes
1. Slow downstream database queries or missing database indexes.
2. Synchronous blocking calls to third-party APIs without timeouts.
3. Thread pool / event loop starvation due to blocking I/O on async threads.
4. Network congestion or packet loss between microservices.

## Investigation Steps
1. Examine distributed traces (Jaeger / OpenTelemetry) for slowest spans.
2. Inspect slow query logs (`pg_stat_statements`).
3. Check upstream and downstream service response times.
4. Verify HTTP connection pool metrics and TCP socket retransmissions.

## Recommended Remediation Actions
1. Enable downstream caching and circuit breaking.
2. Scale backend worker instances to reduce queue wait time.
3. Restart sluggish dependency service or reroute traffic to healthy replicas.
4. Apply transient query index or cache warm-up.

