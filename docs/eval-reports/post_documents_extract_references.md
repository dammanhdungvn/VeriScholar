# API Evaluation Snapshot: POST /api/v1/documents/{document_id}:extract-references

> **Audit Header**: Session Tag: `test_eval_aa57ec6e` | Mode: Golden Dataset Cascading Matcher  
> **Raw Artifacts**: `tests/.artifacts/post_documents_extract_references/`  
> **Payload Checksums (SHA-256)**:  
> - `doc_1706.03762v7_references.json`: `d58abd9fe7ea185226500825d5321c431ded6609514eda60ca975d35f74cd7cb`
> - `doc_2504.19754v1_references.json`: `1fce5d0c8629ecd8442e49c48315d44369e09b45bb9f4948bd1f1d8873837d5d`
> - `doc_2507.12425v1_references.json`: `27b1faa452ded4fab39175836adabcb34c656515bda027edfa5303725b3fb70d`  
> **Quality Gate**: **PASSED** (Recall >= 90%, Precision >= 95%)

---

## 1. Executive Summary & Ground Truth Verification

| Scenario | Status | Latency | Extracted / Expected | Recall | Precision | Quality Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Reference Parsing (1706.03762v7.pdf) | `200` | 180.9 ms | 40 / 40 | 100.0% | 100.0% | PASS |
| Reference Parsing (2504.19754v1.pdf) | `200` | 54.3 ms | 20 / 20 | 100.0% | 95.0% | PASS |
| Reference Parsing (2507.12425v1.pdf) | `200` | 36.5 ms | 22 / 22 | 100.0% | 100.0% | PASS |

---

## 2. Zero-Token Semantic Linter Log
- `[1706.03762v7.pdf] Entity Anomaly: TITLE_TOO_SHORT - Title 'Le' is fewer than 3 chars.`
- `[1706.03762v7.pdf] Entity Anomaly: AUTHOR_TOO_LONG - Author name length 64 > 60.`
- `[1706.03762v7.pdf] Entity Anomaly: AUTHOR_TOO_LONG - Author name length 105 > 60.`
- `[2507.12425v1.pdf] Entity Anomaly: AUTHOR_TOO_SHORT - Author name 'R' too short (< 2).`
- `[2507.12425v1.pdf] Entity Anomaly: AUTHOR_TOO_SHORT - Author name 'A' too short (< 2).`
- `[2507.12425v1.pdf] Entity Anomaly: AUTHOR_TOO_SHORT - Author name 'Y' too short (< 2).`
- `[2507.12425v1.pdf] Entity Anomaly: AUTHOR_TOO_SHORT - Author name 'K' too short (< 2).`
- `[2507.12425v1.pdf] Entity Anomaly: AUTHOR_TOO_SHORT - Author name 'J' too short (< 2).`

---

## 3. Invariants & Contract Adherence
- **Cascading Matcher**: Resolves via Tier 1 (DOI/arXiv) and Tier 2 (Token Jaccard >= 0.85 + Year).
- **Zero Hallucination / Anti-Tampering**: Precision directly maps to actual GT identifiers.
- **Hermetic Lifecycle**: Ephemeral test documents cascade and purge cleanly upon evaluation exit.
