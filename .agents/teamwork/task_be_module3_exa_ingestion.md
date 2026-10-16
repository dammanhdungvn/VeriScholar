# TASK CONTRACT: Backend Implementation of Module 3 (PRD §3.3)
# Academic Reference Resolver, Exa Search, In-Session Ingestion & Citation Graph

## 1. Context & Objectives
You are the **Senior Backend Specialist** on VeriScholar.
Module 2 is 100% closed, certified, and committed.
Your mission is to implement the backend foundation for **Module 3: Multi-Paper Cross Synthesis & Academic Literature Expansion (PRD §3.3)**.

### Objectives:
1. Implement `IAcademicSearchResolverPort` in `packages/core/src/core/ports/academic_resolver.py`.
2. Implement `ExaAcademicResolverAdapter` in `packages/core/src/core/services/exa_resolver.py` using `EXA_API_KEY` (configured in `apps/api/.env` and `~/.bashrc`), with fallback to `InMemoryAcademicResolverAdapter` for deterministic unit testing.
3. Implement `GlobalAcademicCache` with normalized DOI/arXiv keys (< 10ms hit) and strict **Public-Only Cache Isolation** (do NOT cache private user unpublished drafts).
4. Implement REST endpoints:
   - `POST /api/v1/documents/{document_id}/references:resolve`: Resolves extracted references via Exa / deterministic resolvers.
   - `POST /api/v1/sessions/{session_id}/references:ingest`: Ingests open-access references into session documents, strictly enforcing **Session Capacity Cap <= 5 papers** (returns HTTP 422 if `current + len(selected) > 5`).
   - `GET /api/v1/sessions/{session_id}/citation-graph`: Constructs citation graph (`CITES`, `EXTENDS`, `BENCHMARKS_ON`) with **Graph Cycle Breaking & Max-Hop Constraint ($k \le 2$)**.
5. Write thorough unit and integration test suites:
   - `packages/core/tests/services/test_exa_resolver.py`
   - `apps/api/tests/test_academic_resolver.py`
   - `apps/api/tests/test_reference_ingestion.py`
   - All tests must pass with `uv run pytest`.

---

## 2. Technical Specifications & Invariants

### A. Academic Resolver Port & Entities
Create in `packages/core/src/core/ports/academic_resolver.py` and `packages/core/src/core/domain/entities/reference.py`:

```python
class ResolvedAcademicReference(BaseModel):
    ref_index: int
    raw_text: str
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    open_access_pdf_url: str | None = None
    abstract: str | None = None
    citation_count: int | None = None
    sources: list[str] = Field(default_factory=list) # e.g. ["Exa", "arXiv", "Crossref"]
    landing_url: str | None = None
    is_ingested: bool = False
    resolved_document_id: UUID | None = None

class IAcademicSearchResolverPort(ABC):
    @abstractmethod
    async def resolve_reference(self, reference: ExtractedReference) -> ResolvedAcademicReference:
        pass

    @abstractmethod
    async def resolve_batch(self, references: list[ExtractedReference]) -> list[ResolvedAcademicReference]:
        pass
```

### B. Exa Adapter (`packages/core/src/core/services/exa_resolver.py`)
- Reads `EXA_API_KEY` from environment.
- Constructs query using paper title and authors.
- Calls Exa HTTP API (`POST https://api.exa.ai/search`) with:
  ```json
  {
    "query": query,
    "category": "research paper",
    "numResults": 1,
    "contents": {"highlights": true, "summary": true}
  }
  ```
- Extracts `doi`, `citationCount`, `authors`, `abstract`, detects open-access PDF (e.g. `https://arxiv.org/abs/{id}` -> `https://arxiv.org/pdf/{id}.pdf`).
- Graceful degradation: If Exa key is empty, network is unreachable, or Exa returns 0 results, fall back to deterministic parsing or `InMemoryAcademicResolverAdapter`.

### C. Public-Only Cache Isolation
- Cache resolved public papers by normalized key (`doi:10.xxx` or `arxiv:xxxx.xxxxx`).
- Cache TTL: 24 hours.
- Invariant: User unstarred/private preprints MUST NOT be stored in global cache.

### D. Session Ingestion & Capacity Constraint (PRD §3.3)
In `POST /api/v1/sessions/{session_id}/references:ingest`:
- Payload: `{"document_id": UUID, "selected_ref_indices": list[int]}`
- Check current document count in `SessionDocumentModel` for this session.
- If `current_doc_count + len(selected_ref_indices) > 5`:
  Raise `HTTP 422 Unprocessable Entity`:
  `detail={"code": "SESSION_CAPACITY_EXCEEDED", "message": "Phiên đọc sâu giới hạn tối đa 5 bài báo. Vui lòng bỏ bớt bài hoặc lưu vào Thư viện (Module 4) để quản lý kho lớn hơn", "action": "Reduce selected references or manage documents in library."}`
- For each selected reference:
  - If open_access_pdf_url is present, download bytes or create mock/processed `DocumentModel`.
  - Add to `SessionDocumentModel` with `display_order = current_doc_count + i`.
  - Update `ReferenceItemModel.resolved_document_id = new_doc.id`.

### E. Citation Graph & Cycle Breaking (PRD §3.3)
In `GET /api/v1/sessions/{session_id}/citation-graph`:
- Nodes: All session documents + their 1-hop and 2-hop connected references.
- Edges: Typed relationships (`CITES`, `EXTENDS`, `BENCHMARKS_ON`) with confidence scores.
- **Cycle Breaking Invariant**:
  - Max depth traversal $\le 2$ (`k-hop <= 2`).
  - Maintain a `visited: set[str]` to detect and break circular citation loops ($A \to B \to A$ or $A \to B \to C \to A$).
- Return topological / foundational reading path ordering.

---

## 3. Execution Instructions
1. Run isolated unit and integration tests.
2. Ensure strict code formatting with `uv run ruff check --fix` and `uv run ruff format`.
3. Provide full reproduction commands and test output in your completion summary.
