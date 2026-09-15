# API Evaluation Snapshot: POST /api/v1/documents

> **Audit Header**: Session Tag: `test_eval_9ca5d981` | Mode: CAS Ingestion & Deduplication  
> **Target Output**: `temp/output/test/post_documents_upload.md`  
> **Raw Artifacts**: `tests/.artifacts/post_documents_upload/`  
> **Payload Checksums (SHA-256)**:  
> - `Attention Is All You Need_initial.json`: `4486c5a6af0a105749a4dbc544e53d4db41bb768d20d8c47c634a82769e2467d`
> - `Attention Is All You Need_duplicate.json`: `730e7e407faf097b8482dd6926e01c66cc8aa7e1b1ce1794b1d7cac9a5545b50`  
> **Quality Gate**: **PASSED**

---

## 1. Executive Summary & Verification Matrix

| Scenario | Status | Latency | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Valid PDF Upload (Attention Is All You Need.pdf) | `201` | 83.0 ms | PASS | Doc ID: 5b44ba0d-3986-4383-8f7d-8093cbd94526 | Hash: bdfaa68d8984... |
| CAS Deduplication (Attention Is All You Need.pdf) | `201` | 13.9 ms | PASS | CAS Dedup Matched Hash: bdfaa68d8984... |

---

## 2. Invariants & Storage Integrity
- **Content-Addressable Storage (CAS)**: Cryptographic SHA-256 matches bitwise identical uploads.
- **Zero-Retention Hermetic Safety**: Temporary test documents are tracked and cascade-purged on context exit (or retained via `--keep-data`).
- **Robust Multipart Parsing**: Validates special character preservation in filename payloads.
- **Deterministic Refresh**: Output markdown refreshed cleanly at `temp/output/test/post_documents_upload.md`.

---

## 3. Full Raw Payloads (Untruncated)

### Case 1: Valid PDF Upload (Attention Is All You Need.pdf) (Status: `201`)
```json
{
  "success": true,
  "data": {
    "id": "5b44ba0d-3986-4383-8f7d-8093cbd94526",
    "filename": "Attention Is All You Need.pdf",
    "file_size_bytes": 2215244,
    "content_hash": "bdfaa68d8984f0dc02beaca527b76f207d99b666d31d1da728ee0728182df697",
    "status": "uploaded",
    "stage": "queued",
    "progress": 0,
    "is_persistent": false,
    "session_id": null,
    "created_at": "2026-09-15T12:21:30.294849Z",
    "links": {
      "self_url": "/api/v1/documents/5b44ba0d-3986-4383-8f7d-8093cbd94526",
      "status_url": "/api/v1/documents/5b44ba0d-3986-4383-8f7d-8093cbd94526/status",
      "file_url": "/api/v1/documents/5b44ba0d-3986-4383-8f7d-8093cbd94526/file",
      "parse_url": "/api/v1/documents/5b44ba0d-3986-4383-8f7d-8093cbd94526:parse"
    }
  },
  "meta": {
    "request_id": "req_8931c39395bd",
    "timestamp": "2026-09-15T12:21:30.300277Z"
  }
}
```

### Case 2: CAS Deduplication (Attention Is All You Need.pdf) (Status: `201`)
```json
{
  "success": true,
  "data": {
    "id": "99c55a31-c222-40e2-acc6-b0225a55d442",
    "filename": "copy_Attention Is All You Need.pdf",
    "file_size_bytes": 2215244,
    "content_hash": "bdfaa68d8984f0dc02beaca527b76f207d99b666d31d1da728ee0728182df697",
    "status": "uploaded",
    "stage": "queued",
    "progress": 0,
    "is_persistent": false,
    "session_id": null,
    "created_at": "2026-09-15T12:21:30.314367Z",
    "links": {
      "self_url": "/api/v1/documents/99c55a31-c222-40e2-acc6-b0225a55d442",
      "status_url": "/api/v1/documents/99c55a31-c222-40e2-acc6-b0225a55d442/status",
      "file_url": "/api/v1/documents/99c55a31-c222-40e2-acc6-b0225a55d442/file",
      "parse_url": "/api/v1/documents/99c55a31-c222-40e2-acc6-b0225a55d442:parse"
    }
  },
  "meta": {
    "request_id": "req_4dfe5423072f",
    "timestamp": "2026-09-15T12:21:30.315585Z"
  }
}
```
