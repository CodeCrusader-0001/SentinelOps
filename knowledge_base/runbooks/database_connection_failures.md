# RUNBOOK: Database Connection Failures

## Identification
- Symptoms: `Connection pool exhausted`, `timeout acquiring connection`, `Too many connections`, `FATAL: remaining connection slots are reserved for non-replication superuser connections`.
- Severity: CRITICAL / HIGH

## Root Causes
1. Application connection leak (unclosed database sessions or transactions).
2. Sudden surge in user traffic exhausting maximum pool size.
3. Slow running queries holding locks and blocking new queries.
4. Database node resource starvation or network partition.

## Investigation Steps
1. Inspect active connection count via `pg_stat_activity`.
2. Check for long-running uncommitted transactions (`idle in transaction`).
3. Analyze database CPU, memory, and IOPS consumption.
4. Review application connection pool settings (`pool_size`, `max_overflow`, `pool_timeout`).

## Recommended Remediation Actions
1. Safely restart hung client service instances to release abandoned connections.
2. Terminate idle blocking database connections.
3. Increase connection pool size or spin up PgBouncer pooler.
4. Scale application database cluster read replicas.

