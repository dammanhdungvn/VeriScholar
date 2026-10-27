# Langfuse Full Observability Tree Tracing for Discovery & Task Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa hệ thống quan sát toàn trình dạng cây phân cấp (Tree Tracing) trên Langfuse cho tính năng "Tìm bài báo" (Discovery Search) và phân tách nhiệm vụ (Task/Query Decomposition). Đảm bảo mỗi bước đều ghi nhận Input, Output, Metadata và độ trễ, trong đó Output của node trước là Input nuôi node sau, tạo thành quyển nhật ký kiểm toán AI hoàn chỉnh.

**Architecture:** Áp dụng Pipeline Orchestrator Pattern với `AITracingService` của Langfuse:
Trace cha `discovery_search` quản lý 4 child spans tuần tự liên kết dữ liệu chặt chẽ:
1. `Span 1: query_decomposition` (Input: Raw Query $\rightarrow$ Output: Phân loại ý định, DOI/arXiv ID, Semantic Sub-query, Boolean query).
2. `Span 2: exa_neural_search` (Input: Semantic Query từ Span 1 $\rightarrow$ Output: Danh sách bài báo Exa AI Neural Search kèm highlights, scores).
3. `Span 3: arxiv_api_search` (Input: Boolean Query / ID từ Span 1 $\rightarrow$ Output: Danh sách bài báo arXiv Atom XML).
4. `Span 4: academic_rank_fusion` (Input: Danh sách gộp từ Span 2 & Span 3 $\rightarrow$ Output: Danh sách cuối cùng đã khử trùng lặp, xếp hạng theo uy tín học thuật peer-reviewed).

**Tech Stack:** Python 3.12, FastAPI, Langfuse SDK, Exa AI Search API, arXiv Atom API, Pytest, Structlog.

**Spec:** `docs/specs/02-discovery-and-documents.md`, `docs/specs/06-ai-orchestration-and-rag.md`, `docs/PRD/PRD-02-unified-discovery-and-library.md`.

## Global Constraints
- Tuân thủ nghiêm ngặt 4 Verification Gates (`ruff`, `pytest`, `npm test`, `npm run build`).
- TDD bắt buộc: Viết test đỏ trước $\rightarrow$ Viết code xanh tối thiểu $\rightarrow$ Refactor.
- Hexagonal Isolation: Core domain độc lập với web frameworks; adapters chịu trách nhiệm tích hợp I/O.
- Zero Data Retention (ZDR) & Privacy: Không lưu PII; ID người dùng phải được băm qua HMAC-SHA256 (`pseudonymize_user_id`) trước khi gửi lên Langfuse.
- Fail-Safe Invariant: Bất kỳ lỗi kết nối Langfuse hay Exa API đều được xử lý an toàn (graceful fallback), không bao giờ làm sập luồng tìm kiếm bài báo của người dùng.
- In-Plan VPS Auto-Sync: Sau mỗi task hoàn tất commit, tự động chạy `bash scripts/deploy_to_vps.sh --fast`.

## Review Focus
1. **Missing Exa API Key Handling:** Không cấu hình `EXA_API_KEY` trong môi trường kiểm thử $\rightarrow$ Tự động ghi nhận span Exa với metadata `fallback=True`, không raise ngoại lệ làm hỏng kết quả.
2. **Input/Output Data Binding:** Output của `query_decomposition` phải ánh xạ trực tiếp thành input của `exa_neural_search` và `arxiv_api_search`.
3. **Langfuse Tree Hierarchy Structure:** Tất cả spans con phải nằm trong cùng một Trace ID và có quan hệ phân cấp rõ ràng trên dashboard Langfuse.
4. **Peer-reviewed Classification Metadata:** Bổ sung thông tin phân loại `is_peer_reviewed`, `venue`, `doi` vào output metadata của từng bài báo trên Langfuse.
5. **Error Stack Trace Capturing:** Khi Exa hoặc arXiv gặp lỗi mạng/timeout, span con phải bắt trọn error message và gán `level="ERROR"` vào Langfuse span.

---

### Task 1: Core Query Decomposition Engine with Structured Academic Outputs

**Files:**
- Create: `apps/api/src/api/services/query_decomposer.py`
- Create Test: `apps/api/tests/unit/test_scholarly_query_decomposer.py`

**Interfaces:**
- Consumes: `raw_query: str`
- Produces: `DecomposedQuery(intent: str, identifier: str | None, semantic_query: str, boolean_arxiv_query: str, sub_topics: list[str])`

- [x] **Step 1: Write the failing unit test**
Test các kịch bản:
- Truy vấn DOI (`10.1109/CVPR.2016.90`) $\rightarrow$ nhận diện `intent="doi_lookup"`, `identifier="10.1109/CVPR.2016.90"`.
- Truy vấn arXiv (`2305.18290` hoặc `arXiv:1706.03762`) $\rightarrow$ nhận diện `intent="arxiv_lookup"`, `identifier="2305.18290"`.
- Truy vấn ngữ nghĩa dài (`Attention Is All You Need Transformer architectures for NLP`) $\rightarrow$ nhận diện `intent="keyword_search"`, trích xuất `semantic_query` sạch và `boolean_arxiv_query` chuẩn.

- [x] **Step 2: Run test to verify it fails**
Run: `uv run pytest apps/api/tests/unit/test_scholarly_query_decomposer.py -v`
Expected: FAIL (module not found).

- [x] **Step 3: Implement `QueryDecomposer` in `apps/api/src/api/services/query_decomposer.py`**

- [x] **Step 4: Run test to verify it passes**
Run: `uv run pytest apps/api/tests/unit/test_scholarly_query_decomposer.py -v`
Expected: 100% tests pass.

- [x] **Step 5: Commit & Auto VPS Sync**
```bash
git add apps/api/src/api/services/query_decomposer.py apps/api/tests/unit/test_scholarly_query_decomposer.py
git commit -m "feat(discovery): implement structured academic query decomposition engine"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 2: Exa AI Neural Search Integration in `ScholarlySearchAdapter`

**Files:**
- Modify: `apps/api/src/api/adapters/scholarly_search_adapter.py`
- Create Test: `apps/api/tests/unit/test_scholarly_search_exa.py`

**Interfaces:**
- Consumes: `semantic_query: str`, `limit: int`, `api_key: str | None`
- Produces: `list[ScholarlyPaperSearchResult]` từ Exa Search API (`https://api.exa.ai/search`) với `type="neural"`, trích xuất highlights, tác giả, năm và phân loại peer-reviewed.

- [x] **Step 1: Write the failing unit test with mocked Exa API responses**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `_search_exa()` and integrate into `search()` in `ScholarlySearchAdapter`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit & Auto VPS Sync** (Commit: `9638789`)

```bash
git add apps/api/src/api/adapters/scholarly_search_adapter.py apps/api/tests/unit/test_scholarly_search_exa.py
git commit -m "feat(discovery): integrate exa neural academic search into scholarly search adapter"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 3: Langfuse Hierarchical Tree Tracing in `ScholarlySearchAdapter` & Discovery Endpoint

**Files:**
- Modify: `apps/api/src/api/adapters/scholarly_search_adapter.py`
- Modify: `apps/api/src/api/v1/endpoints/discovery.py`
- Modify: `apps/api/src/api/deps.py`
- Create Test: `apps/api/tests/unit/test_discovery_langfuse_tracing.py`

**Interfaces:**
- Consumes: `ai_tracing: AITracingService`, `current_user: UserModel`, `query: str`
- Produces: Cây trace hoàn chỉnh trên Langfuse:
  - `Trace: discovery_search`
    - `Span 1: query_decomposition` [Input: Raw Query $\rightarrow$ Output: Decomposed Query]
    - `Span 2: exa_neural_search` [Input: Semantic Query từ Span 1 $\rightarrow$ Output: Exa Papers]
    - `Span 3: arxiv_api_search` [Input: Boolean Query từ Span 1 $\rightarrow$ Output: arXiv Papers]
    - `Span 4: academic_rank_fusion` [Input: Exa + arXiv candidates $\rightarrow$ Output: Final Ranked Papers]

- [x] **Step 1: Write unit tests verifying tree trace hierarchy and input/output chaining**
- [x] **Step 2: Run test to verify it fails**
Run: `uv run pytest apps/api/tests/unit/test_discovery_langfuse_tracing.py -v`
Expected: FAIL.

- [x] **Step 3: Implement tree tracing orchestration in `ScholarlySearchAdapter` & `discovery.py`**

- [x] **Step 4: Run test to verify it passes**
Run: `uv run pytest apps/api/tests/unit/test_discovery_langfuse_tracing.py -v`
Expected: 100% tests pass.

- [ ] **Step 5: Commit & Auto VPS Sync**
```bash
git add apps/api/src/api/adapters/scholarly_search_adapter.py apps/api/src/api/v1/endpoints/discovery.py apps/api/src/api/deps.py apps/api/tests/unit/test_discovery_langfuse_tracing.py
git commit -m "feat(observability): instrument complete tree tracing on langfuse for discovery search pipeline"
bash scripts/deploy_to_vps.sh --fast
```

---

### Task 4: End-to-End Verification across the 4 Mandatory Verification Gates

**Files:**
- Repository-wide verification across all 4 gates.

- [ ] **Step 1: Run Gate 1 (Python Linter & Formatter)**
Run: `uv run ruff check . && uv run ruff format --check .`
Expected: 0 errors, 0 format warnings.

- [ ] **Step 2: Run Gate 2 (Backend Unit & Integration Tests)**
Run: `uv run pytest`
Expected: 100% tests passed.

- [ ] **Step 3: Run Gate 3 (Frontend Unit Tests)**
Run: `npm --prefix apps/web run test`
Expected: 100% tests passed.

- [ ] **Step 4: Run Gate 4 (Production Build Frontend)**
Run: `npm --prefix apps/web run build`
Expected: Exit code 0, build thành công.

- [ ] **Step 5: Live Verification & Deploy to VPS**
Run: `bash scripts/deploy_to_vps.sh --fast`
Expected: Exit code 0, triển khai thành công lên `https://verischolar.duckdns.org`.
