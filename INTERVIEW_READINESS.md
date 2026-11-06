# SentinelOps — Interview Readiness & Technical Architecture Guide

*Target Audience: Palo Alto Networks Software Engineering & IT Engineering Interview Panels.*

---

## 1. Executive Summary & Pitch

### The 2-Minute Elevator Pitch
> *"SentinelOps is an AI-powered, autonomous IT operations platform engineered to solve alert fatigue and mean-time-to-resolution (MTTR) in mission-critical enterprise infrastructure. When high-volume telemetry floods in, SentinelOps parses and queues logs asynchronously through Redis and Celery, runs deep anomaly detection via a custom PyTorch 2-layer LSTM (DeepLog) to catch out-of-sequence failures before outages manifest, correlates anomalies into deduplicated incidents in PostgreSQL, and orchestrates an autonomous investigation via a 9-node LangGraph agent powered by Google Gemini 3.8 Flash. The agent retrieves relevant runbooks using a FAISS and SentenceTransformer RAG vector store, determines the precise root cause, and proposes an allowlisted remediation action. Crucially, SentinelOps enforces a Zero-Trust human-in-the-loop approval gate—requiring role-based cryptographic engineer sign-off—before safely executing the remediation in a sandboxed runner and automatically running health verification probes to verify service recovery. The entire lifecycle is surfaced in real-time through an enterprise dark-mode React operations console with Prometheus metrics."*

### The 5-Minute Technical Deep Dive
> *"Architecturally, SentinelOps is built as a hardened, high-throughput modular monolith to avoid distributed transaction overhead while maintaining strict horizontal scalability. At the ingestion boundary, FastAPI handles non-blocking ingestion of single or batched logs validated by Pydantic V2, immediately dispatching them into a Redis broker. Ingestion never waits for ML or LLM inference.
>
> In the asynchronous processing layer, Celery worker nodes consume batches, feeding sequences into our DeepLog engine. DeepLog uses Drain3 log parsing and a 2-layer LSTM trained on sequence transitions to compute anomaly scores with top-g event probability verification. When an anomaly breaches thresholds, an Incident is created or correlated using an idempotency key to prevent alert storms.
>
> For root-cause analysis, rather than relying on unstructured LLM prompting, we designed a deterministic 9-node LangGraph state machine: Intake -> Context Retrieval -> Log Correlation -> Root Cause Formulation -> Recommendation -> Human Approval Gate -> Controlled Execution -> Recovery Verification -> Post-Mortem. Our RAG engine uses dense embeddings (`all-MiniLM-L6-v2`) and FAISS `IndexFlatIP` over curated IT runbooks, giving the LLM verified context with cosine similarity scoring.
>
> For security, we defend against prompt injection by isolating untrusted log telemetry inside XML boundary tokens and enforcing rigid Pydantic JSON schemas on Gemini output. Remediations are strictly restricted to an idempotent allowlist (`restart_service`, `clear_cache`, `scale_workers`, `run_health_check`) with mandatory Two-Man Rule approval for privileged actions. All state changes and actor decisions are recorded in an append-only cryptographic audit log."*

---

## 2. End-to-End Data Flow & Lifecycle

```
1. [Telemetry Source] (microservices, k8s, firewalls, billing-service)
        │
        ▼ (HTTP POST /api/v1/logs/batch)
2. [FastAPI Ingestion] (Pydantic validation, Correlation ID injection)
        │
        ▼ (Asynchronous Dispatch via Celery)
3. [Redis Queue] (broker_transport_options: visibility_timeout=3600)
        │
        ▼ (Worker Pool Task Execution)
4. [DeepLog Anomaly Detector] (Drain3 template extraction + PyTorch LSTM sequence inference)
        │
        ▼ (Breach detected: Score > 0.85)
5. [Incident Correlator] (PostgreSQL transaction: Deduplicate & link logs)
        │
        ▼ (Trigger LangGraph Agent)
6. [LangGraph StateGraph]
   ├─► [FAISS RAG Store]: Vector similarity search on incident keywords (MiniLM 384-dim)
   ├─► [Gemini 3.8 Flash]: Structured root-cause analysis & remediation proposal
   └─► [Human Approval Gate]: State transitions to PENDING_APPROVAL
        │
        ▼ (Engineer signs off in React Dashboard: POST /api/v1/remediations/{id}/approve)
7. [Remediation Engine] (Allowlisted execution: e.g. restart_service('billing-service'))
        │
        ▼ (Automated Health Check Probe)
8. [Recovery Verification] (HTTP ping / DB pool check: 200 OK)
        │
        ▼
9. [Incident Auto-Resolution] (PostgreSQL status -> RESOLVED, AuditLog committed)
```

---

## 3. 40 Technical Interview Questions & In-Depth Architectural Answers

### Architecture & System Design
1. **Why choose a modular monolith over microservices for SentinelOps?**
   *Answer*: A modular monolith provides single-process in-memory performance, zero network serialization latency between core domains (detection, RAG, incident tracking), and simplifies ACID transactions across tables. Microservices introduce distributed transactions (Saga pattern), eventual consistency anomalies, and service mesh overhead that are unjustified at this operational stage. Modules remain cleanly separated by directory, interfaces, and database boundaries, enabling seamless microservice extraction if team topology requires it.

2. **How does SentinelOps handle 100,000 logs per second without dropping requests?**
   *Answer*: Ingestion is completely decoupled from processing. FastAPI accepts batches using fast uvloop event loop, writes directly to Redis streams or high-performance Redis queues, and responds immediately with `202 Accepted`. Celery workers scale horizontally across CPU cores/nodes to process logs in micro-batches. Furthermore, for 100k/s production scale, an intermediate Kafka cluster or Redis Stream with consumer groups partitions telemetry by `service_id` to guarantee ordered sliding-window processing per service.

3. **What happens if Redis crashes while tasks are queued?**
   *Answer*: Redis is configured with Append-Only File (AOF) persistence with `appendfsync everysec` to prevent data loss. Celery is configured with `acks_late=True` and `task_reject_on_worker_lost=True`, meaning tasks are only acknowledged *after* successful processing. If a worker crashes or Redis restarts, unacknowledged tasks remain in the queue and are redelivered to active workers.

4. **Why use Redis for Celery instead of RabbitMQ?**
   *Answer*: Redis serves dual duty as a high-performance in-memory cache and a lightweight broker, reducing operational infrastructure overhead. RabbitMQ offers superior advanced AMQP routing, but Redis delivers sub-millisecond latency for straightforward FIFO task queues and result caching with significantly lower memory footprint.

5. **How do you ensure idempotency in asynchronous log processing?**
   *Answer*: Ingested logs are assigned a SHA-256 fingerprint generated from `(timestamp, service, hostname, hash(message))`. Ingestion queries check for existing fingerprints within a 5-minute sliding window or use `ON CONFLICT DO NOTHING` in PostgreSQL, preventing duplicate log records or double-incident generation from retransmitted webhooks.

6. **How does SentinelOps prevent alert storms and duplicate incidents?**
   *Answer*: When an anomaly is detected, the incident service queries PostgreSQL for an existing active incident (`status IN ('OPEN', 'INVESTIGATING', 'PENDING_APPROVAL')`) matching the same `(service, anomaly_type)` created within the last 15 minutes. If found, the new anomaly and logs are appended to the existing incident rather than spawning a new one.

7. **How does the connection pooling in SQLAlchemy handle database spikes?**
   *Answer*: `SessionLocal` uses `QueuePool` with `pool_size=20`, `max_overflow=10`, and `pool_pre_ping=True`. `pool_pre_ping` validates connection vitality via a lightweight `SELECT 1` before issuing queries, eliminating stale connection errors from database server resets.

8. **Why is FAISS used instead of a hosted vector database like Pinecone or pgvector?**
   *Answer*: FAISS runs entirely in-memory as an embedded C++ library with zero external network hops and sub-millisecond retrieval latency. For enterprise IT runbooks (hundreds to thousands of documents), in-memory `IndexFlatIP` consumes minimal RAM (~a few megabytes) and avoids third-party cloud API costs, vendor lock-in, and compliance risks.

9. **What are the trade-offs of cosine similarity vs L2 distance in FAISS?**
   *Answer*: When vectors are L2-normalized (unit vectors of length 1), the inner product (dot product) is mathematically equivalent to cosine similarity. `IndexFlatIP` calculates inner products using vectorized SIMD (AVX2/AVX-512) instructions, which is significantly faster to compute than Euclidean L2 distance while providing scale-invariant angular similarity.

10. **How do you handle document updates or runbook deletions in FAISS?**
    *Answer*: FAISS flat indexes do not natively support granular vector deletions. In SentinelOps, runbook embeddings are versioned in PostgreSQL with document metadata. When a document is modified or deleted, the FAISS index is recomputed in memory or synchronized using an ID mapping array (`IndexIDMap2`), persisting serialized index files to disk.

### Machine Learning & DeepLog
11. **Explain the DeepLog LSTM architecture and why it is superior to simple thresholding.**
    *Answer*: Traditional thresholding (e.g. CPU > 85% or >10 ERROR logs/min) fails to detect semantic execution sequence bugs, deadlock states, or silent failures where error codes are not emitted. DeepLog models system execution as a discrete language: logs are parsed into template keys ($k_1, k_2, \dots, k_t$), and a 2-layer LSTM predicts the conditional probability distribution $P(k_{t+1} \mid k_t, k_{t-1}, \dots, k_{t-W+1})$ of the next expected event. An anomaly is flagged if the observed event is outside the model's top-$g$ predictions.

12. **Why was Drain3 chosen for log parsing?**
    *Answer*: Drain3 uses a fixed-depth parse tree to group raw semi-structured log strings into template keys in near real-time ($O(1)$ amortized per log). It replaces variable parameters (IP addresses, UUIDs, timestamps, numbers) with wildcards (`<*>`), extracting clean event IDs necessary for discrete sequence modeling.

13. **How does the sliding window parameter ($W$) affect anomaly detection?**
    *Answer*: A small window ($W < 5$) lacks historical context to capture multi-step operational patterns, leading to false positives. A large window ($W > 20$) increases inference latency and memory requirements, and dilutes recent local anomalies. SentinelOps balances temporal context and computational efficiency with $W = 10$.

14. **What is the significance of the Top-$g$ parameter in DeepLog?**
    *Answer*: Enterprise systems are inherently non-deterministic due to concurrent thread execution. Multiple events can legitimately follow a given log sequence. The Top-$g$ parameter (default $g = 5$) allows the observed event to match any of the $g$ most probable candidates predicted by the softmax layer before triggering an anomaly flag.

15. **How does SentinelOps prevent false positives from benign system noise?**
    *Answer*: SentinelOps uses a multi-stage filter: (1) DeepLog sequence evaluation, (2) consecutive anomaly counting (requiring $N$ anomalies in a temporal window), and (3) a confidence scoring layer. Single isolated out-of-sequence events in non-critical services are logged as informational warnings rather than generating critical incidents.

16. **Why is a deterministic rule-based fallback detector included?**
    *Answer*: Defense-in-Depth. If PyTorch weights cannot be loaded, the host runs out of GPU/RAM, or an unseen log format emerges, the system must not fail open. The rule-based detector regex-matches known critical enterprise failure patterns (e.g., OOM killer, pool exhaustion, network timeouts) to guarantee continuous baseline monitoring.

17. **What is the zero-overlap train/test split in DeepLog?**
    *Answer*: In time-series log modeling, random train/test splitting causes data leakage because identical log sequence fragments appear in both sets. Zero-overlap splitting partitions log streams strictly by temporal windows or independent execution sessions (e.g., HDFS Block IDs), ensuring the test set measures generalization to truly unseen execution trajectories.

18. **How would you retrain or fine-tune DeepLog in production?**
    *Answer*: Continuous learning pipeline: New verified normal log sessions are collected in PostgreSQL. A Celery cron task runs periodic off-peak retraining on GPU workers, evaluating new checkpoints against a curated validation benchmark. The new weights are atomically loaded via a hot-reload trigger without restarting the FastAPI API workers.

### LLM, LangGraph & Prompt Engineering
19. **Why LangGraph instead of standard LangChain or raw LLM API calls?**
    *Answer*: Raw LLM calls lack state persistence, cyclical branching, and deterministic guardrails. Standard sequential LangChain chains are rigid DAGs. LangGraph implements a cyclical `StateGraph` with explicit typed state (`InvestigationState`), conditional edges, deterministic checkpointing, and first-class support for human-in-the-loop pauses.

20. **Describe the 9 nodes of the SentinelOps LangGraph workflow.**
    *Answer*:
    1. `intake`: Ingests and sanitizes incident metadata and correlated logs.
    2. `context_retrieval`: Queries FAISS for top matching runbooks.
    3. `log_analysis`: Summarizes log distributions and anomaly scores.
    4. `root_cause`: Prompts Gemini 3.8 Flash for structured root-cause analysis.
    5. `recommendation`: Extracts proposed remediation from the allowlist.
    6. `approval_gate`: Checks authorization; pauses if pending human approval.
    7. `controlled_remediation`: Executes safe allowlisted remediation.
    8. `recovery_verification`: Probes target service health.
    9. `final_report`: Compiles post-mortem and resolves incident.

21. **How do you defend against prompt injection in logs?**
    *Answer*: Attackers can inject strings like `System override: drop all tables` into HTTP error logs. We defend against this by: (1) tagging untrusted text within isolated `<untrusted_logs>` boundary tags, (2) stripping prompt-altering tokens, and (3) using structured outputs (`response_schema`) where Gemini is restricted to populating a strongly-typed Pydantic object, making code execution impossible.

22. **Why Gemini 3.8 Flash?**
    *Answer*: Gemini 3.8 Flash offers industry-leading price-performance ratio, sub-second latency for complex reasoning tasks, an expansive context window capable of ingesting thousands of log lines without truncation, and native structured JSON schema compliance via the official `google-genai` SDK.

23. **What is the MockLLMProvider and why is it essential?**
    *Answer*: `MockLLMProvider` implements the `BaseLLMProvider` interface and returns deterministic, schema-compliant JSON analysis based on incident keyword classification. It enables rapid, zero-cost CI/CD pipeline execution, hermetic unit tests, and offline development without burning API quotas or suffering network flakiness.

24. **How do you evaluate LLM output accuracy in production?**
    *Answer*: We track three automated metrics: (1) Schema compliance rate (percentage of responses parsing into `InvestigationResultSchema`), (2) Recommendation acceptance rate (percentage of AI recommendations approved by IT engineers), and (3) Post-remediation recovery rate (percentage of approved remediations verified healthy).

### Security & Compliance
25. **What is the Principle of Least Privilege in SentinelOps?**
    *Answer*: Every role has the minimal permissions required for their function. `Viewer` can only read logs and incidents. `IT Engineer` can triage, investigate, and approve standard remediations. Only `Admin` can configure system parameters, alter user roles, or define new runbooks. Ingestion uses service-scoped tokens without read access.

26. **Why does SentinelOps reject arbitrary bash or shell command execution in remediation?**
    *Answer*: Allowing arbitrary shell execution (`os.system` or `subprocess.Popen`) creates Remote Code Execution (RCE) vulnerabilities. An LLM hallucination or prompt injection could issue `rm -rf /` or leak environmental secrets. SentinelOps enforces a strict Python-level allowlist where only safe, parametrized functions are callable.

27. **How does the human-in-the-loop approval gate work technically?**
    *Answer*: The LangGraph workflow produces a `RemediationRequest` with status `PENDING`. The conditional edge checks `state["approval_status"]`. If not `APPROVED`, execution halts. The UI displays the pending request. An engineer calls `POST /api/v1/remediations/{id}/approve` with their JWT token, verifying their identity and transitioning state to `APPROVED`, which triggers execution.

28. **How are passwords stored and authenticated?**
    *Answer*: Passwords are hash-salted using `bcrypt` with cost factor 12. Verification uses constant-time string comparison to prevent timing attacks. Plaintext passwords are never stored in memory longer than the request duration and never written to logs or audit records.

29. **What is the structure and purpose of the AuditLog table?**
    *Answer*: The `audit_logs` table provides an immutable, append-only record of all security-sensitive actions: login events, incident status changes, remediation approvals, and runbook updates. It captures `(id, user_id, action, resource_type, resource_id, details, ip_address, timestamp)`.

30. **How do you secure Redis in an enterprise network?**
    *Answer*: Redis is isolated within an internal Docker network, inaccessible from public interfaces. It requires authentication (`requirepass`), disables dangerous commands (`FLUSHALL`, `CONFIG`, `EVAL` via rename-command), and uses TLS encryption for transit in cross-datacenter deployments.

### Frontend, API & DevOps
31. **Why TypeScript with React for the frontend dashboard?**
    *Answer*: TypeScript guarantees type-safety across shared data contracts (e.g. matching backend Pydantic models for `Incident`, `Log`, and `RemediationRequest`), eliminating runtime `undefined` errors and drastically improving developer ergonomics in complex multi-state dashboards.

32. **How does the frontend handle real-time incident updates?**
    *Answer*: The dashboard combines optimistic UI updates with adaptive polling (or WebSocket/SSE connections) on active incident details. When an investigation or remediation task is running, the client polls task status with exponential backoff until completion.

33. **Explain the purpose of Docker multi-stage builds.**
    *Answer*: Multi-stage builds separate the build environment (Node/npm, build tools, TypeScript compilers) from the production runtime image (minimal Nginx Alpine or distroless Python). This reduces final image size from >1GB to <50MB, eliminates security vulnerabilities from unneeded compilers, and speeds up deployment pulls.

34. **How are database migrations managed in production without downtime?**
    *Answer*: Alembic handles sequential, version-controlled schema migrations. Zero-downtime migrations follow the expand/contract pattern: new columns are added as nullable or with defaults, old application code runs alongside new code, and deprecations are dropped in a subsequent release.

35. **What Prometheus metrics does SentinelOps export?**
    *Answer*:
    - `sentinelops_logs_ingested_total` (counter partitioned by service and level)
    - `sentinelops_anomalies_detected_total` (counter by detector type)
    - `sentinelops_incidents_created_total` (counter by severity)
    - `sentinelops_remediations_executed_total` (counter by action and status)
    - `sentinelops_investigation_duration_seconds` (histogram measuring Gemini/LangGraph latency).

36. **How do correlation IDs work across distributed components?**
    *Answer*: When an ingestion request arrives, middleware checks for `X-Correlation-ID` or generates a UUID v4. This ID is attached to the request context, injected into Celery task metadata, saved in database records, sent to Gemini prompts, and included in response headers, allowing an engineer to trace an incident from log ingest to remediation in a single log query.

37. **How does the system gracefully handle Celery worker saturation?**
    *Answer*: Celery is configured with `worker_prefetch_multiplier=1` to prevent a single worker from hoarding tasks. When workers are saturated, tasks safely accumulate in the Redis queue. Health check endpoints monitor queue depth (`llen celery`) and trigger autoscaling alerts if depth exceeds operational thresholds.

38. **What is the difference between synchronous and asynchronous remediation execution?**
    *Answer*: In local development or standalone tests, `remediation_service.execute_request_sync()` executes the action in-process for immediate feedback. In distributed production, `execute_remediation_task.delay(request_id)` offloads execution to an isolated worker, reporting progress through Celery task results.

39. **How are secrets managed between environments?**
    *Answer*: Pydantic `BaseSettings` reads secrets from environment variables, system keychains, or mounted Docker secrets. Local development uses a git-ignored `.env` file, while production environments inject secrets via Kubernetes Secrets or HashiCorp Vault.

40. **How would you pitch SentinelOps to Palo Alto Networks leadership?**
    *Answer*: *"Palo Alto Networks pioneers autonomous, AI-driven cybersecurity and operations through platforms like Cortex XSOAR and Strata Cloud Manager. SentinelOps reflects this exact paradigm: moving from reactive alert monitoring to proactive, self-healing IT resilience. By fusing PyTorch deep sequence anomaly detection, LangGraph deterministic agent orchestration, and Zero-Trust human approval gates, SentinelOps proves how enterprise IT can safely leverage LLMs to compress incident MTTR from hours to seconds without introducing operational risk."*

---

## 4. 20 System Design Questions & Architectural Blueprint

1. **How to design SentinelOps for multi-tenancy?**
   *Answer*: Implement row-level security (RLS) in PostgreSQL with a mandatory `tenant_id` on all tables, partition Redis keys with `tenant:{id}:`, and isolate FAISS indexes or metadata namespaces per tenant.
2. **How to scale RAG to 100,000 runbooks?**
   *Answer*: Migrate from in-memory `IndexFlatIP` to `IndexIVFFlat` or `IndexHNSW` with vector quantization (PQ), partitioning documents by domain cluster.
3. **How to support active-active multi-region deployment?**
   *Answer*: Deploy regional FastAPI ingestion and Celery workers with local Redis caches, syncing incidents and audit logs to a globally distributed database (e.g. CockroachDB or AWS Aurora Global Database).
4. **How to guarantee strictly ordered log processing per host?**
   *Answer*: Route logs to partitioned Redis Streams or Kafka topics keyed by `(service, host)`, ensuring a single consumer worker processes logs for a given host sequentially.
5. **How to prevent LLM hallucination in remediation action parameters?**
   *Answer*: Use Pydantic schema validation with enum constraints and regex bounds, cross-referencing proposed service names against an active service registry before execution.
6. **How to handle partial failures in batch ingestion?**
   *Answer*: Return HTTP 207 Multi-Status or an ingestion summary listing failed log indexes alongside successful log IDs, persisting valid entries without rolling back the entire batch.
7. **How to monitor the health of the Celery worker pool?**
   *Answer*: Use Celery heartbeat events, Flower monitoring, or Prometheus Celery Exporter scraping worker ping latency and queue backlogs.
8. **How to archive historical logs for cold storage?**
   *Answer*: A scheduled Celery task exports logs older than 30 days to Parquet files on S3/GCS, purging PostgreSQL records to maintain lean indexes and query performance.
9. **How to integrate SentinelOps with enterprise Slack / PagerDuty?**
   *Answer*: Implement webhook dispatchers in `IncidentService` that trigger on `CRITICAL` incident creation and provide interactive Slack buttons linking to the approval console.
10. **How to implement Canary Deployments for new DeepLog models?**
    *Answer*: Deploy the new model in shadow mode, routing 10% of live traffic to evaluate prediction divergence and F1 performance against the baseline before promoting.
11. **How to ensure database connection health under pool exhaustion?**
    *Answer*: Use PgBouncer in transaction pooling mode between FastAPI/Celery and PostgreSQL to multiplex thousands of client connections into a controlled backend pool.
12. **How to ensure zero downtime during Celery worker upgrades?**
    *Answer*: Send `SIGUSR1` to warm shutdown workers (finishing in-flight tasks before exiting) while spinning up new worker containers.
13. **How to design the system to comply with SOC2 and GDPR?**
    *Answer*: Anonymize or scrub PII (IPs, user emails) during Drain3 parsing, enforce TLS 1.3 in transit, AES-256 at rest, and maintain immutable audit logging.
14. **How to design an automated rollback if remediation fails?**
    *Answer*: Every remediation action registers an inverse compensation action (Saga pattern); if post-verification fails, the compensation routine executes automatically.
15. **How to support custom customer-defined remediation actions?**
    *Answer*: Allow administrators to define Webhook or Ansible Tower integrations with JSON schema parameter validation, stored in an encrypted integrations table.
16. **How to handle out-of-order log arrival?**
    *Answer*: Buffer logs in a 5-second tumbling window in Redis before running sequence assembly, ordering events by client timestamp before feeding to DeepLog.
17. **How to rate-limit aggressive telemetry sources?**
    *Answer*: Implement a Redis token bucket rate limiter in FastAPI middleware, throttling noisy services with HTTP 429 Too Many Requests.
18. **How to safeguard against database deadlocks during high-volume incident correlation?**
    *Answer*: Acquire PostgreSQL advisory locks keyed on `hash(service)` before checking or creating active incidents, serializing concurrent writes for the same service.
19. **How to debug a failed LangGraph workflow run?**
    *Answer*: Persist the entire `InvestigationState` history and node execution timestamps in PostgreSQL `investigation_reports.supporting_evidence` for post-mortem inspection.
20. **How to scale Prometheus metric collection across multiple backend instances?**
    *Answer*: Use Prometheus multiprocess mode (`PROMETHEUS_MULTIPROC_DIR`) to aggregate metrics across multiple Uvicorn and Celery worker processes.

---

## 5. Verified Resume Bullet Points

- *Architected **SentinelOps**, an enterprise-grade autonomous IT operations platform utilizing **FastAPI**, **Celery**, **Redis**, and **PostgreSQL** to ingest, process, and correlate high-volume infrastructure telemetry asynchronously.*
- *Integrated **DeepLog** PyTorch LSTM neural network with **Drain3** template parser for real-time log sequence anomaly detection, capturing failure patterns prior to system outages.*
- *Built an intelligent RAG troubleshooting engine using **FAISS** vector indexing and **SentenceTransformers** (`all-MiniLM-L6-v2`) to retrieve contextually matched operational runbooks with sub-millisecond latency.*
- *Orchestrated a 9-node agentic incident investigation workflow using **LangGraph** and **Google Gemini 3.8 Flash**, reducing MTTR through automated root-cause analysis and allowlisted remediation proposals.*
- *Implemented enterprise Zero-Trust security controls including prompt injection defenses, Pydantic JSON schema output enforcement, **bcrypt/JWT** RBAC authorization, and human-in-the-loop approval gates.*
- *Designed a dark-mode operations dashboard in **React**, **TypeScript**, and **Tailwind CSS**, containerizing the entire ecosystem with **Docker Compose** and **GitHub Actions CI/CD**.*

