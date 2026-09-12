---
name: postgres-patterns
description: PostgreSQL database patterns for query optimization, schema design, indexing, pgvector, and security. Optimized for VeriScholar's Hybrid RAG architecture (PostgreSQL 16 + pgvector). Use when designing PostgreSQL schemas, vector indexes, or optimizing slow queries.
metadata:
  origin: ECC (adapted for VeriScholar)
---

# PostgreSQL Patterns

Quick reference for PostgreSQL best practices, indexing strategies, and `pgvector` optimization for Advanced Hybrid RAG.

## When to Activate

- Writing SQL queries, SQLAlchemy async models, or migrations
- Designing vector embeddings and document chunk schemas
- Optimizing dense vector search (`HNSW`) or lexical search (`tsvector` + GIN)
- Tuning PostgreSQL memory and connection limits for high-concurrency async workloads

## Quick Reference

### Index Cheat Sheet

| Query Pattern | Index Type | Example |
|--------------|------------|---------|
| `WHERE col = value` | B-tree (default) | `CREATE INDEX idx ON t (col)` |
| `WHERE col > value` | B-tree | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Composite | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ query` (BM25) | GIN | `CREATE INDEX idx ON t USING gin (tsv)` |
| Dense Vector Cosine (`<=>`) | HNSW | `CREATE INDEX idx ON t USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)` |
| Dense Vector L2 (`<->`) | HNSW | `CREATE INDEX idx ON t USING hnsw (embedding vector_l2_ops)` |
| Time-series ranges | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

### Data Type Quick Reference

| Use Case | Correct Type | Avoid |
|----------|-------------|-------|
| IDs | `uuid` (via `uuid-ossp`) or `bigint` | `int`, raw string UUID |
| Dense Vector (BGE-M3) | `vector(1024)` | `float[]`, `json`, `text` |
| Text Chunks | `text` | `varchar(255)` |
| Timestamps | `timestamptz` | `timestamp` |
| Bounding Boxes | `jsonb` or `float4[5]` (`[x0, y0, x1, y1, page]`) | unstructured string |
| Full-Text Search | `tsvector` (generated column) | runtime `to_tsvector` in `WHERE` |

---

## 🚀 pgvector & Hybrid Search Patterns

### 1. High-Performance HNSW Vector Index
```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Define table with dense vector
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    bounding_boxes JSONB NOT NULL DEFAULT '[]',
    token_count INT NOT NULL,
    embedding vector(1024), -- BGE-M3 1024-dim
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- HNSW Index for fast approximate nearest neighbor search (< 10ms)
CREATE INDEX idx_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- GIN Index for lexical full-text search
CREATE INDEX idx_chunks_tsv ON document_chunks USING gin (tsv);
```

### 2. Hybrid Search with Reciprocal Rank Fusion (RRF)
Combines semantic vector proximity and exact lexical keywords in a single SQL query:
```sql
WITH semantic AS (
    SELECT id, RANK() OVER (ORDER BY embedding <=> :query_embedding) AS rank
    FROM document_chunks
    WHERE document_id = :doc_id
    ORDER BY embedding <=> :query_embedding
    LIMIT 20
),
lexical AS (
    SELECT id, RANK() OVER (ORDER BY ts_rank_cd(tsv, plainto_tsquery('english', :query_text)) DESC) AS rank
    FROM document_chunks
    WHERE document_id = :doc_id AND tsv @@ plainto_tsquery('english', :query_text)
    LIMIT 20
)
SELECT 
    c.id,
    c.content,
    c.bounding_boxes,
    COALESCE(1.0 / (60 + s.rank), 0.0) + COALESCE(1.0 / (60 + l.rank), 0.0) AS rrf_score
FROM semantic s
FULL OUTER JOIN lexical l ON s.id = l.id
JOIN document_chunks c ON c.id = COALESCE(s.id, l.id)
ORDER BY rrf_score DESC
LIMIT 5;
```

---

## Common SQL & Schema Patterns

### Composite Index Order
```sql
-- Equality columns first, then range columns
CREATE INDEX idx ON orders (status, created_at);
-- Works for: WHERE status = 'pending' AND created_at > '2024-01-01'
```

### Covering Index
```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- Avoids table lookup for SELECT email, name, created_at
```

### Cursor Pagination
```sql
SELECT * FROM document_chunks 
WHERE document_id = $doc_id AND chunk_index > $last_index 
ORDER BY chunk_index ASC 
LIMIT 50;
-- O(1) performance vs OFFSET which is O(n)
```

---

## Monitoring & Anti-Pattern Detection

```sql
-- Find unindexed foreign keys
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;
```
