# API Evaluation Snapshot: POST /api/v1/documents/{document_id}:parse

> **Audit Header**: Session Tag: `test_eval_aa57ec6e` | Mode: Automated Autotest  
> **Raw Artifacts**: `tests/.artifacts/post_documents_parse/`  
> **Quality Gate**: **PASSED**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status | Latency | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Trigger Parse Pipeline (HTTP 202 Accepted) | `202` | 15.6 ms | PASS | Status: processing, Stage: validation |
| Idempotent Replay Caching (24h Window) | `202` | 3.6 ms | PASS | X-Cache header: Idempotent-Hit |
| State Machine Guard (HTTP 409 DOCUMENT_PROCESSING) | `409` | 5.4 ms | PASS | Error code: DOCUMENT_PROCESSING |
| Validation Guard (chunk_overlap >= chunk_size -> HTTP 422) | `422` | 4.4 ms | PASS | Status: 422 |
| Deep Output Quality (Spatial Geometry & Canvas Sanity) | `200` | 0.5 ms | PASS | Audited 0 page bounds, 0 anomalies |

---

## 2. Invariants & Contract Adherence
- **Asynchronous 202 Ingress**: Long-running ingestion jobs return `202 Accepted`.
- **Idempotency Guard**: 24-hour deduplication window verified with identical cached replay.
- **State Machine Guard**: Prevents race conditions with `HTTP 409 DOCUMENT_PROCESSING`.
- **Schema Boundary**: Semantic validation rejects overlap >= chunk_size with `HTTP 422`.
- **Spatial Geometry Sanity**: Verified bounding box bounds and normalized canvas coordinates.
