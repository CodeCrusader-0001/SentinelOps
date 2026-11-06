# RUNBOOK: High CPU Utilization

## Identification
- Symptoms: CPU utilization sustained $> 90\%$ on application host or container, elevated request queue depth, throttled CPU shares.
- Severity: HIGH / MEDIUM

## Root Causes
1. Unoptimized nested loops or regular expressions (ReDoS).
2. Tight polling loops in background workers.
3. Garbage collection thrashing due to memory pressure.
4. Cryptographic operations or heavy unmemoized calculations.

## Investigation Steps
1. Capture thread dump or profile with py-spy / async-profiler.
2. Identify hot worker threads and associated request endpoints.
3. Check system load average vs CPU core count.
4. Verify if CPU throttling is occurring due to container resource limits.

## Recommended Remediation Actions
1. Horizontally scale worker count or pod replicas.
2. Enable rate limiting or shedding of non-critical traffic.
3. Restart degraded worker nodes showing CPU lockup.
4. Hotfix algorithmic bottlenecks or optimize query batching.

