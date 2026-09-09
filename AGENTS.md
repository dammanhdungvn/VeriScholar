# AGENTS.md — VeriScholar Engineering & AI Agent Protocol

Behavioral guidelines, architectural laws, clean code standards, and workflow instructions for AI agents and engineers contributing to **VeriScholar**.

---

## 1. CORE BEHAVIORAL PROTOCOL

### 1.1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State your assumptions explicitly before coding. If uncertain, ask.
- If multiple interpretations exist, present them — do not pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear or ambiguous, **STOP**. Name what is confusing. Ask.

### 1.2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that was not requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Ask yourself: *"Would a senior engineer say this is overcomplicated?"* If yes, simplify.

### 1.3. Surgical Changes & Monorepo Atomicity
**Touch only what you must. Clean up only your own mess.**
- When editing existing code:
  - Do not "improve" adjacent code, comments, or formatting.
  - Do not refactor things that are not broken.
  - Match existing style, even if you would do it differently.
  - If you notice unrelated dead code, mention it — do not delete it.
- When your changes create orphans:
  - Remove imports/variables/functions that **your** changes made unused.
  - Do not remove pre-existing dead code unless explicitly requested.
- **Internal Compatibility Invariant:**
  - When modifying interfaces, schemas, or models in `packages/core`, ensure immediate atomic compatibility updates across all dependent consumers (`apps/api`, `apps/web`) within the same commit. Never leave downstream packages broken.
- The test: **Every changed line should trace directly to the user's request.**

### 1.4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
- Transform tasks into verifiable goals:
  - *"Add validation"* → Write tests for invalid inputs, then make them pass.
  - *"Fix the bug"* → Write a test that reproduces it, then make it pass.
  - *"Refactor X"* → Ensure tests pass before and after.
- For multi-step tasks, state a brief plan:
  ```text
  1. [Step] → verify: [check]
  2. [Step] → verify: [check]
  3. [Step] → verify: [check]
  ```

---

## 2. DEV ENVIRONMENT TIPS

- **Monorepo Navigation:**
  - The repository is organized as a `uv workspace` for Python services and `pnpm` for web UI.
  - Core domain logic lives in `packages/core`.
  - Backend ASGI API server lives in `apps/api`.
  - Web client lives in `apps/web`.
- **Backend Sync & Run (`uv`):**
  - Sync all Python workspace members: `uv sync --all-packages`
  - Add dependency to API: `uv add --package api <package-name>`
  - Add dependency to Core: `uv add --package core <package-name>`
  - Run API backend: `uv run --package api api` (fallback: `uv run --package api python -m api`). Hot reload watches `apps/api/src` and `packages/core/src`.
- **Frontend Commands (`apps/web` via `pnpm`):**
  - Install frontend dependencies: `pnpm --prefix apps/web install`
  - Run frontend dev server: `pnpm --prefix apps/web dev`
  - Frontend typecheck & lint: `pnpm --prefix apps/web exec tsc -b` and `pnpm --prefix apps/web lint`
  - Build validation: `pnpm --prefix apps/web build`
- **Inter-Package Boundaries & Invariants:**
  - `apps/api` depends on `packages/core`.
  - `packages/core` must **NEVER** import from `apps/api` or `apps/web`.
- **Atomic Evidence Invariant & Coordinate Norms:**
  - `DocumentChunk` is the immutable unit of retrieval across the system.
  - Every parser, chunker, and search retriever MUST preserve normalized `BoundingBox` coordinates `[x0, y0, x1, y1, page]`:
    - `page`: Strictly **1-indexed integer** (`page >= 1`). Adapters (e.g. PyMuPDF `0-indexed` page numbers) must normalize: `page = raw_page_index + 1`.
    - Coordinates `[x0, y0, x1, y1]`: Normalized floats `[0.0, 1.0]` relative to page dimensions (`0.0 <= x0 < x1 <= 1.0`, `0.0 <= y0 < y1 <= 1.0`).
    - Origin `(0, 0)` is strictly **Top-Left** (standard for PDF rendering & Web Canvas).
  - **NEVER** strip bounding boxes or downgrade evidence chunks to raw unstructured strings.
- **Document Ingestion Idempotency Invariant:**
  - Ingestion pipelines must compute a `SHA-256` content hash of any ingested document before indexing.
  - Ingestions with identical SHA-256 hashes must be strictly idempotent (reuse existing document ID and chunk vectors) to prevent index bloat and duplicated retrieval hits.

---

## 3. TESTING INSTRUCTIONS

- **Backend Test Suites (`uv`):**
  - Run all workspace tests: `uv run pytest`
  - Test only backend API: `uv run pytest apps/api/tests`
  - Test only core domain: `uv run pytest packages/core/tests`
  - Run targeted step test: `uv run pytest -k "<test_name>"`
  - Run with verbose output: `uv run pytest -s -v`
- **Testing Boundaries (In-Memory Isolation):**
  - Unit tests in `packages/core/tests` must run 100% in-memory with zero external dependencies (no live DB, no network calls).
  - Use Ports & Adapters mocks/fakes for external drivers. Integration tests requiring PostgreSQL/`pgvector` must reside strictly in designated integration test suites.
- **Frontend Verification (`apps/web`):**
  - Run linter: `pnpm --prefix apps/web lint`
  - Run TypeScript compile check: `pnpm --prefix apps/web exec tsc -b`
- **Quality Assurance & Verification:**
  - After moving files or updating imports, run `uv run ruff check .` and `uv run ruff format --check .` to verify formatting and linting.
  - Ensure all async tests use `pytest-asyncio` markers (`@pytest.mark.asyncio`).
  - Add or update tests for every code change, even if not explicitly requested.

---

## 4. PR INSTRUCTIONS

- **Title Format:**
  - Follow Conventional Commits: `[<package_name>] <type>: <description>`
  - Examples:
    - `[api] feat: implement pure asgi tracing middleware`
    - `[core] fix: resolve bounding box calculation for two-column pdf`
    - `[web] feat: render bounding box overlay on pdf page`
    - `[docs] docs: update guide logging system with eval suite`
- **Pre-Commit Verification:**
  - Backend: Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pytest`.
  - Frontend (if modified): Run `pnpm --prefix apps/web lint`, `pnpm --prefix apps/web exec tsc -b`, and `pnpm --prefix apps/web build`.
  - Ensure no sensitive tokens, API keys, or `.env` files are tracked by git.
  - Verify all database mutations are wrapped inside explicit transactions (`async with session.begin():`).

---

## 5. ARCHITECTURAL & DESIGN LAWS

1. **The Dependency Rule:**
   - Source code dependencies must always point inward toward high-level business policies.
   - Frameworks, databases, HTTP transports, and UI are external implementation details.
   - `packages/core` must remain 100% agnostic of FastAPI, HTTP requests, and web frameworks.

2. **The Humble Object Pattern:**
   - Always decouple core domain computation from volatile infrastructure (networks, file systems, databases).
   - Abstract I/O behind Ports & Interfaces.
   - Domain logic must be 100% unit-testable in-memory without requiring live databases or mock web servers.

3. **The First Law of Software Architecture:**
   - *Everything in software architecture is a trade-off.*
   - Never present a proposal as "universally optimal".
   - Always explicitly articulate trade-offs across latency, throughput, complexity, operational overhead, and developer ergonomics.

4. **The Second Law of Software Architecture:**
   - *"Why" is more important than "How".*
   - Major structural decisions must document their context and reasoning.
   - Record significant architecture shifts as Architectural Decision Records (ADRs): Title, Status, Context, Decision, and Consequences.

5. **Avoid Architecture Sinkholes:**
   - Prohibit empty pass-through layers or boilerplate proxy classes that merely delegate calls without transforming data or applying business rules.

6. **No Speculative Generality (YAGNI):**
   - Do not write speculative abstractions, pluggable interfaces for single implementations, or unused configuration knobs.
   - Build the simplest solution that works today; refactor when real evidence of variance emerges.

7. **Fail Fast & Early Input Validation:**
   - Validate input contracts immediately at the system boundary (e.g. via Pydantic v2 schemas) before allocating heavy resources (DB connections, PDF parsing threads, LLM API calls).

8. **Minimal High-Signal Context (Anti-Bloat):**
   - Context injected into LLM prompts or agent workflows must be strictly minimized to the highest-signal tokens.
   - Do NOT dump raw entire repository files, voluminous log traces, or redundant metadata into agent contexts.
   - Single-doc retrieval for Module 1 must remain a deterministic, linear pipeline (Hybrid Search → Cross-Encoder Rerank → Grounded LLM Stream; SLA < 5s). Do NOT inject unrequested autonomous agentic graph loops.

---

## 6. CLEAN CODE & OBJECT-ORIENTED PRINCIPLES

1. **Single Responsibility Principle (SRP):**
   - Each module, class, or function must have only one reason to change.
   - Avoid "god objects" or "do-it-all" utility modules.

2. **Open-Closed Principle (OCP):**
   - Software entities should be open for extension, but closed for modification.
   - Encapsulate what varies behind interfaces (e.g., `DocumentParserPort` for PyMuPDF / Docling).

3. **Dependency Inversion Principle (DIP):**
   - High-level business logic must depend on abstractions (Protocols / Abstract Base Classes), not on concrete implementations.

4. **Interface Segregation (ISP) & The Hollywood Principle:**
   - Clients should not be forced to depend on methods they do not use.
   - Employ *"Don't call us, we'll call you"* hooks and inversion of control where frameworks orchestrate behavior.

5. **Principle of Least Knowledge (Law of Demeter):**
   - A component should only converse with its immediate collaborators.
   - Avoid long method chains (`a.get_b().get_c().do_something()`).

6. **Consistent Naming & Ubiquitous Language:**
   - Use identical names for identical domain concepts (`BoundingBox`, `DocumentChunk`, `GroundingCitation`).
   - Never conflate terms across boundaries (e.g., do not alternate between `topic`, `channel`, and `stream` for the same entity).

---

## 7. API & CONTRACT DESIGN DISCIPLINE

1. **Predictable & Consistent Data Structures:**
   - Keep schema structures flat and minimize nested depth.
   - Standardize error codes and envelope responses across all endpoints.

2. **Exhaustive Error Feedback:**
   - Return structured, machine-readable error responses detailing exactly which field was invalid and actionable steps to resolve it.

3. **Stateless & Straightforward Flows:**
   - Each HTTP/SSE endpoint must be strictly stateless and perform a single cohesive operation.

4. **Backward Compatibility & Staged N-1 Rollouts:**
   - Any schema modification that alters existing consumer contracts must undergo a deprecation transition supporting N-1 versions.
   - Coordinate breaking changes in four distinct phases: (1) Schema migration with N-1 support, (2) Data backfill, (3) Agent/API code deployment, (4) Cleanup of legacy elements.

---

## 8. PRODUCTION QUALITY GATE CHECKLIST

Before considering any task complete, cross-check and verify every item:

- [ ] **No Absorbed Exceptions:** No empty `except` blocks or swallowed errors; every exception is logged with full context or properly handled.
- [ ] **No Hardcoded Magic Strings/Numbers:** Extract all fixed values, thresholds, and configuration strings into named constants or `Pydantic Settings`.
- [ ] **Zero Warning / Zero Lint:** `uv run ruff check .` and `uv run ruff format --check .` exit cleanly with zero errors and warnings.
- [ ] **Frontend Verification Passed:** If frontend changes are made, `pnpm --prefix apps/web lint`, `pnpm --prefix apps/web exec tsc -b`, and `pnpm --prefix apps/web build` pass with zero errors.
- [ ] **Async Execution Hygiene:** No blocking synchronous I/O or heavy CPU operations (e.g., PyMuPDF rendering, Docling layout analysis) run directly inside the async event loop; always offloaded via `asyncio.to_thread()`.
- [ ] **Database Transaction Integrity:** All database write/mutation operations are scoped inside explicit transaction context managers (`async with session.begin():`); no partial writes or dangling uncommitted transactions.
- [ ] **Automated Verifications Passed:** All unit and integration tests covering the affected codebase pass (`uv run pytest`).
- [ ] **Observability & PII Safe:** Log outputs adhere to `GUIDE_LOGGING_SYSTEM.md`, sanitize tokens/keys, and propagate `X-Request-ID`.
- [ ] **Atomic Evidence Preserved:** Normalized `BoundingBox` coordinates are preserved on all `DocumentChunk` instances (`page >= 1`, Top-Left origin `[0.0, 1.0]`); never downgraded to raw unstructured text.
- [ ] **Ingestion Idempotency Enforced:** Documents calculate SHA-256 hash to prevent duplicate chunking and vector index pollution.
- [ ] **Contract & Schema Safety:** Any modified API routes return predictable, structured error envelopes and follow the staged N-1 rollout discipline.
