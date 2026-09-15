# API Evaluation Snapshot: POST /api/v1/documents/{document_id}:extract-references

> **Audit Header**: Session Tag: `test_eval_a650fdf7` | Mode: Golden Dataset Cascading Matcher  
> **Raw Artifacts**: `tests/.artifacts/post_documents_extract_references/`  
> **Payload Checksums (SHA-256)**:  
> - `doc_1706.03762v7_references.json`: `bdb99a00a8c8ee3df94f3d701bd2e39096962eb360e2fa6d44f03c3ef4e80f3e`
> - `doc_2504.19754v1_references.json`: `f06379da1becdef9630bf1117b0cd2ecd9f7f1746c5e151c127bfba653348eff`
> - `doc_2507.12425v1_references.json`: `489c6fcd70c1f9c5add7397c923ce3764ae83e5d87c7be33798670a18faafbc8`  
> **Quality Gate**: **PASSED** (Recall >= 90%, Precision >= 95%)

---

## 1. Executive Summary & Ground Truth Verification

| Scenario | Status | Latency | Extracted / Expected | Recall | Precision | Quality Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Reference Parsing (1706.03762v7.pdf) | `200` | 166.8 ms | 40 / 40 | 100.0% | 100.0% | PASS |
| Reference Parsing (2504.19754v1.pdf) | `200` | 48.7 ms | 20 / 20 | 100.0% | 95.0% | PASS |
| Reference Parsing (2507.12425v1.pdf) | `200` | 33.3 ms | 22 / 22 | 100.0% | 100.0% | PASS |

---

## 2. Zero-Token Semantic Linter Log
- `[OK]` All extracted references passed semantic validity heuristics.

---

## 3. Invariants & Contract Adherence
- **Cascading Matcher**: Resolves via Tier 1 (DOI/arXiv) and Tier 2 (Token Jaccard >= 0.85 + Year).
- **Zero Hallucination / Anti-Tampering**: Precision directly maps to actual GT identifiers.
- **Hermetic Lifecycle**: Ephemeral test documents cascade and purge cleanly upon evaluation exit.
