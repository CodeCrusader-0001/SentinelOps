# RUNBOOK: Memory Leaks and Heap Exhaustion

## Identification
- Symptoms: `java.lang.OutOfMemoryError: Java heap space`, `OOMKilled exit status 137`, persistent upward drift in resident memory without plateau.
- Severity: CRITICAL / HIGH

## Root Causes
1. Unbounded in-memory collections, cache accumulation without TTL or eviction policy.
2. Circular object references or static variable retention.
3. High concurrency buffering large payloads into RAM instead of streaming.
4. Native memory leaks in compiled C/C++ extensions or libraries.

## Investigation Steps
1. Review heap memory graphs (Prometheus memory metrics).
2. Generate and analyze heap dump (jhat / memray / tracemalloc).
3. Identify top retained memory allocations by class and module.
4. Verify cache eviction logs and max memory thresholds.

## Recommended Remediation Actions
1. Execute rolling restart of affected application instances.
2. Flush and purge application or Redis cache keys.
3. Temporarily increase memory limit / container heap allocation.
4. Deploy fix ensuring explicit cache expiry and object disposal.

