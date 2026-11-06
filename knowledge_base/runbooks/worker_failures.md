# RUNBOOK: Celery / Background Worker Failures

## Identification
- Symptoms: `WorkerLostError: Worker process exited prematurely`, task queue lag growing monotonically, tasks marked pending without progress, Celery heartbeat missing.
- Severity: HIGH / CRITICAL

## Root Causes
1. Celery child worker killed by Linux OOM killer due to memory leakage during task processing.
2. Hard task time limit exceeded (`TimeLimitExceeded`).
3. Loss of broker heartbeat or Redis broker disconnection.
4. Segfault in native C extension (e.g. image processing, machine learning library).

## Investigation Steps
1. Inspect Celery worker logs for stack traces and SIGKILL notifications.
2. Check broker queue depth via `celery inspect active` / `celery inspect reserved`.
3. Check host dmesg for kernel OOM killer events (`invoked oom-killer`).
4. Identify tasks with highest execution duration and payload sizes.

## Recommended Remediation Actions
1. Restart Celery worker processes with clean state.
2. Scale worker concurrency or spawn additional worker nodes.
3. Configure `worker_max_tasks_per_child` to cycle workers and mitigate memory leaks.
4. Re-queue stranded tasks from dead letter queue with backoff.

