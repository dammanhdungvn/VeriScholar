# API Evaluation Snapshot: POST /api/v1/documents

> **Audit Header**: Session Tag: `test_eval_a650fdf7` | Mode: Automated Autotest  
> **Raw Artifacts**: `tests/.artifacts/post_documents_upload/`  
> **Payload Checksums (SHA-256)**:  
> - `1706.03762v7_initial.json`: `8e9f906c297768d21fc47d685ff813ad5ac03b801fb63bfdbc294ba96f14ea80`
> - `1706.03762v7_duplicate.json`: `c768c247a095a47bc56bb9c5617da4c78a4b90a46cf807a09bea82613a1e1f61`
> - `2504.19754v1_initial.json`: `43f7b1f7b921c2ad278e3167700c7706ba4a4d85e5bfce60418add0e6deccc82`
> - `2504.19754v1_duplicate.json`: `bef5a2dcee86f1fc322f11128a6f702a25576eee73cc26bf265c4a8e761acab7`
> - `2507.12425v1_initial.json`: `ae61002193b095b9701ff83682297aa22a102f048c2f5fa9fbc1c8fe9bf6bc1e`
> - `2507.12425v1_duplicate.json`: `30dfc8efe17f83e38313aed92a74606a621070f4b91e63d2b3be388edd2322cf`
> - `corrupted_structure.json`: `aa3ebf045ef747ed680e20274577fcae8bdbd1ac47e53a8c93db2c0a3e38b934`  
> **Quality Gate**: **PASSED**

---

## 1. Executive Summary & Verification Matrix

| Test Scenario | HTTP Status | Latency | Status |
| :--- | :--- | :--- | :--- |
| Valid PDF Upload (1706.03762v7.pdf) | `201` (exp: `201`) | 81.1 ms | PASS |
| CAS Deduplication Check (1706.03762v7.pdf) | `201` (exp: `201`) | 17.5 ms | PASS |
| Valid PDF Upload (2504.19754v1.pdf) | `201` (exp: `201`) | 10.7 ms | PASS |
| CAS Deduplication Check (2504.19754v1.pdf) | `201` (exp: `201`) | 9.7 ms | PASS |
| Valid PDF Upload (2507.12425v1.pdf) | `201` (exp: `201`) | 10.4 ms | PASS |
| CAS Deduplication Check (2507.12425v1.pdf) | `201` (exp: `201`) | 12.5 ms | PASS |
| Corrupted PDF Header Rejection | `400` (exp: `400`) | 4.0 ms | PASS |

---

## 2. Invariants & Architecture Checks
- **CAS Deduplication**: Re-uploading identical binary computes exact SHA-256.
- **Validation Ingress Barrier**: Corrupted PDF binary is rejected with HTTP 400.
- **Zero-Storage Retention**: Ephemeral test tenant cleaned up on evaluation exit.
- **Payload Integrity**: Checksums cryptographically bound to raw json artifacts.
