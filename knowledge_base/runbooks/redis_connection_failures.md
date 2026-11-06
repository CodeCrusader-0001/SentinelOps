# RUNBOOK: Redis Connection Failures and Cluster Degradation

## Identification
- Symptoms: `ConnectionRefusedError: [Errno 111] Connection refused`, `redis.exceptions.TimeoutError`, `OOM command not allowed when used memory > 'maxmemory'`, Sentinel quorum loss.
- Severity: HIGH / CRITICAL

## Root Causes
1. Redis memory reached `maxmemory` without volatile or allkeys-lru eviction policy.
2. Redis single-threaded event loop blocked by expensive operations (`KEYS *`, `SMEMBERS`, lua scripts).
3. Client connection limit exceeded (`maxclients`).
4. Redis daemon process terminated or host rebooted.

## Investigation Steps
1. Run `redis-cli INFO` to check memory usage, connected clients, and blocked clients.
2. Check `SLOWLOG GET 10` for long-running blocking commands.
3. Review Redis log file for eviction warnings or persistence (AOF/RDB) failures.
4. Test network latency and packet loss to Redis host on port 6379.

## Recommended Remediation Actions
1. Purge stale cache keys or flush volatile cache partitions (`UNLINK`).
2. Restart Redis service or failover to standby replica.
3. Increase Redis `maxmemory` ceiling.
4. Scale out cluster sharding or enable Redis Sentinel automatic failover.

