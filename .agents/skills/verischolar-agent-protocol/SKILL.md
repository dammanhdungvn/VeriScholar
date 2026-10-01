---
name: verischolar-agent-protocol
description: >-
  Essential engineering protocols, architectural laws, and domain invariants for VeriScholar.
  Use when developing, modifying, or testing features across apps/api, apps/web, and packages/core,
  especially when handling PDF parsing, bounding boxes, chat streaming, sessions, or quality gates.
---

# VeriScholar Agent Protocol

This skill guides AI agents and engineers on how to build, refactor, and verify features within the **VeriScholar** monorepo according to core architectural laws and domain invariants.

## When to Activate

- Adding or modifying features in `apps/api`, `apps/web`, or `packages/core`.
- Working with PDF ingestion, layout analysis, chunks, or bounding boxes.
- Handling Socratic chat streaming, citation badges, or LLM reasoning.
- Implementing session management or workspace standby flows.
- Running pre-commit verifications and production quality gates.

---

## 1. Core Domain Invariants (Non-Negotiable)

### 1.1. Atomic Evidence Invariant & Coordinate Norms
`DocumentChunk` is the immutable unit of retrieval across the system.
- **`page`**: Strictly **1-indexed integer** (`page >= 1`).
  - PyMuPDF is 0-indexed by default; you must normalize: `page = raw_page_index + 1`.
- **Coordinates `[x0, y0, x1, y1]`**: Normalized floats in `[0.0, 1.0]` relative to page dimensions (`0.0 <= x0 < x1 <= 1.0`, `0.0 <= y0 < y1 <= 1.0`).
- **Origin `(0, 0)`**: Strictly **Top-Left** (standard for PDF rendering & Web Canvas).
- **Rule**: NEVER strip bounding boxes or downgrade evidence chunks to raw unstructured strings.

### 1.2. Zero DB Junk & Standby Flow
- Entering the `/dashboard` workspace begins in **Standby Mode**.
- Bấm "Đoạn chat mới" or navigating to dashboard MUST NOT call `POST /api/v1/sessions` until a document is ingested or the user explicitly sends their first prompt.
- Never pollute the database with empty, orphaned sessions.

### 1.3. Ingestion Idempotency (SHA-256)
- Ingestion pipelines must compute a `SHA-256` content hash of any ingested document before indexing.
- Ingestions with identical SHA-256 hashes must be strictly idempotent (reuse existing document ID and chunk vectors) to prevent vector index bloat and duplicated retrieval hits.

### 1.4. Monorepo Dependency Rule
- `apps/api` depends on `packages/core`.
- `apps/web` communicates via HTTP/SSE API contracts with `apps/api`.
- `packages/core` must **NEVER** import from `apps/api` or `apps/web`.
- Core domain logic must remain 100% agnostic of FastAPI, HTTP requests, and web frameworks.

---

## 2. Progressive Step-by-Step Procedure

### Step 1: Pre-Implementation Analysis & Sanity Check
1. State assumptions explicitly before coding.
2. Check `AGENTS.md` and relevant reference docs:
   - [Architectural Invariants](references/architectural-invariants.md)
   - [Standby & Session Flow](references/standby-session-flow.md)
   - [AI Guardrails Specification](references/guardrails-spec.md)
3. Ensure no speculative abstractions or unnecessary dependencies are introduced (YAGNI).

### Step 2: Implementation & Monorepo Atomicity
1. Make surgical changes only.
2. When modifying interfaces, schemas, or models in `packages/core`, immediately update all dependent consumers in `apps/api` and `apps/web` within the same commit.
3. Keep single-doc retrieval linear (Hybrid Search → Cross-Encoder Rerank → Grounded LLM Stream; SLA < 5s).

### Step 3: Run Deterministic Verification
Execute the bundled verification script to ensure all quality gates pass:
```bash
bash .agents/skills/verischolar-agent-protocol/scripts/verify_quality_gate.sh
```
Or execute individually:
- Backend Lint & Format: `uv run ruff check .` && `uv run ruff format --check .`
- Backend Tests (In-Memory Isolation): `uv run pytest apps/api/tests/` && `uv run pytest packages/core/tests/`
- Frontend Lint & Typecheck: `pnpm --prefix apps/web lint` && `pnpm --prefix apps/web exec tsc -b`
- Frontend Build: `pnpm --prefix apps/web build`

---

## 3. Decision Matrix

| Scenario | Recommended Approach | Prohibited Approach |
| :--- | :--- | :--- |
| **New Chat Session** | Client-side Standby state; lazy create on first message or doc upload | Calling `POST /api/v1/sessions` on page load |
| **PDF Extraction** | PyMuPDF with normalized `[x0, y0, x1, y1]` (Top-Left) + 1-indexed page | Stripping bounding boxes to plain text string |
| **LLM Reasoning (gpt-5.6-luna)** | Omit `temperature` (or keep 1.0); use `stream=True` via SSE | Passing `temperature: 0.3` (triggers HTTP 400) |
| **Testing** | In-memory fakes/mocks (`InMemory*Store`) with zero external network | Calling real OpenAI API or requiring live PostgreSQL during unit tests |
| **Monorepo Imports** | Import `core` into `api` | Importing `api` into `core` |
