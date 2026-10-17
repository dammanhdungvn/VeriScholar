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

### 1.5. Mandatory Multi-Agent Delegation Invariant
**Không làm việc đơn độc khi có các AI chuyên trách đang hoạt động. Luôn luôn giao việc theo đúng rules/chuyên môn.**
- **Zero Solo-Work Invariant:** Tuyệt đối **KHÔNG ĐƯỢC** một mình tự ôm đồm thực hiện toàn bộ quy trình (từ code backend, code frontend, viết test đến tự nghiệm thu) khi trong phiên làm việc đang có các AI chuyên trách khác (Backend Specialist, Frontend Specialist, Lead Reviewer, v.v.) hoạt động hoặc sẵn sàng.
- **Phân chia công việc theo đúng vai trò & rules:**
  - **Backend Specialist:** Chịu trách nhiệm toàn bộ logic nghiệp vụ máy chủ, API endpoints, CSDL/migrations, NLI verification services, backend unit/integration tests (`pytest`) và linter Ruff.
  - **Frontend Specialist:** Chịu trách nhiệm toàn bộ giao diện web, UI components, state management, API client, streaming SSE hooks, TypeScript compilation (`tsc -b`), Vitest tests và UI Error Boundaries.
  - **Lead Reviewer / Gatekeeper:** Chịu trách nhiệm kiểm tra độc lập git diff, đối chiếu kiến trúc Hexagonal, chạy các bộ AI benchmark/eval tự động và cấp chứng chỉ nghiệm thu kỹ thuật khách quan.
  - **Coordinator / CTO:** Giữ vai trò đầu mối điều phối duy nhất, phân rã yêu cầu thành các gói công việc (task decomposition), giao việc cụ thể kèm tiêu chí nghiệm thu rõ ràng (Definition of Done), giám sát tiến độ và tổng hợp báo cáo.
- **Quy tắc phối hợp:**
  - Phải ủy quyền công việc qua cơ chế điều phối runtime chuẩn (`herdr agent prompt <target> ...` hoặc `invoke_subagent`).
  - Phải chờ kết quả phản hồi từ đồng đội AI, kiểm tra chéo và đối chiếu bằng chứng khách quan trước khi xác nhận hoàn thành cho User / Product Owner.

### 1.6. Runtime Introspection Invariant (Cấm Đoán Mò Hiện Trạng Hoạt Động)
**Mọi AI Agent không được phép dừng lại ở việc đọc code tĩnh mà phải truy cập sâu vào trạng thái thực thi runtime.**
- **Cấm suy diễn tĩnh:** Tuyệt đối không phỏng đoán ứng dụng có chạy hay không, CSDL có dữ liệu hay không, hoặc vì sao CI thất bại.
- **Sử dụng MCP Server `verischolar-runtime` & `github`:**
  - Kiểm tra trạng thái dịch vụ sống: `check_services_health()` hoặc `systemctl is-active verischolar-api.service`.
  - Thăm dò endpoint thực tế: `probe_api("/health")` hoặc `curl -s http://127.0.0.1:8000/health`.
  - Khảo sát dữ liệu sống: `query_database_readonly("summary")` hoặc câu lệnh `SELECT count(*)`.
  - Đọc nhật ký thời gian thực: `read_service_logs("api", 50)` hoặc `journalctl -u verischolar-api -n 50 --no-pager`.
  - Kiểm tra lỗi CI/CD tự động: `inspect_github_ci_status(pr_number)` hoặc `gh run view <id> --log-failed` để đọc trực tiếp stack trace của bước bị fail trên GitHub Actions.
- **Kích hoạt Kỹ năng:** Tham khảo chi tiết tại `.agents/skills/runtime-diagnostics/SKILL.md`.

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
  - Backend: Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pytest``.
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
- [ ] **Observability & PII Safe:** Log outputs adhere to `docs/vi/guide-logging-system.md`, sanitize tokens/keys, and propagate `X-Request-ID`.
- [ ] **Atomic Evidence Preserved:** Normalized `BoundingBox` coordinates are preserved on all `DocumentChunk` instances (`page >= 1`, Top-Left origin `[0.0, 1.0]`); never downgraded to raw unstructured text.
- [ ] **Ingestion Idempotency Enforced:** Documents calculate SHA-256 hash to prevent duplicate chunking and vector index pollution.
- [ ] **Contract & Schema Safety:** Any modified API routes return predictable, structured error envelopes and follow the staged N-1 rollout discipline.
- [ ] **Mandatory Resource & Tool Evidence Attached:** Task completion report explicitly lists tools/skills used, concrete empirical evidence (test logs, traces, browser screenshots), or domain-specific rationale if no secondary tool was needed.
- [ ] **Multi-Agent Delegation Verified:** Đã phân chia công việc cho các AI chuyên trách tương ứng (Backend, Frontend, Reviewer); tuyệt đối không tự ý làm việc đơn độc khi có đồng đội AI hoạt động.

---

## 9. MANDATORY TOOL & RESOURCE SELECTION PROTOCOL

Lựa chọn và sử dụng tài nguyên phù hợp là **bước bắt buộc** trong quy trình thực hiện task của toàn đội, không phải gợi ý tùy chọn.

### 9.1. Quy Trình Trước Khi Thực Hiện Mỗi Task Có Ý Nghĩa
1. **Xác định nhu cầu:** Phân loại rõ mục tiêu: nghiên cứu (research), thiết kế kiến trúc (design), lập trình (coding), gỡ lỗi (debug), kiểm thử (test/eval) hay nghiệm thu (review).
2. **Khảo sát tài nguyên thực tế phù hợp:**
   - Skills có sẵn trong repository: `.agents/skills/*` (`ui-styling`, `fastapi`, `langfuse`, `e2e-testing`, `verification-loop`, `hexagonal-architecture`, `postgres-patterns`, v.v.).
   - Năng lực native Antigravity, Herdr / Multi-Agent runtime CLI (`herdr agent`, `herdr pane`, `herdr workspace`), MCP servers, CLI công cụ và tài liệu chính thức theo đúng phiên bản.
3. **Đọc tài liệu & kích hoạt tài nguyên:**
   - Đọc hướng dẫn/SKILL.md của tài nguyên được chọn trước khi thao tác.
   - Sử dụng khi mang lại lợi ích thiết thực và ghi rõ yêu cầu sử dụng/kiểm chứng vào task bàn giao.
   - Tuyệt đối không chỉ liệt kê công cụ trên danh nghĩa rồi bỏ qua hoặc tuyên bố dùng mà không thực hiện.

### 9.2. Ma Trận Ứng Dụng Thực Tiễn Theo Miền Task
- **Sửa UI / Frontend:** Đọc skill frontend liên quan (`ui-styling`, `react-patterns`), mở ứng dụng bằng browser (Playwright browser), tái hiện lỗi trực quan, sửa mã nguồn, sau đó kiểm tra lại trên giao diện; không chỉ dựa vào `pnpm build` hay jsdom unit test.
- **Debug RAG & Tracing:** Sử dụng skill Langfuse / CLI / trace API để kiểm tra trace được cấp quyền, định vị chính xác span/bước lỗi trước khi sửa, và chạy eval suite đối chuẩn trước/sau khi vá lỗi.
- **Sửa API, Endpoint hoặc Auth:** Đọc kỹ contract OpenAPI và skill backend/security (`fastapi`, `security-review`, `api-design`), gửi request HTTP thực tế, kiểm tra phân quyền và chạy kiểm thử chéo bằng tối thiểu 2 tài khoản khác nhau.
- **Tích hợp Thư viện / CLI:** Đọc tài liệu chính thức đúng phiên bản phát hành, kiểm tra compatibility matrix, thực hiện smoke test độc lập; cấm đoán mò API signature.
- **Refactor Phức Tạp & Kiến Trúc:** Cân nhắc khả năng điều phối subagents/teamwork độc lập để phân tích phản biện; chỉ kích hoạt khi giá trị vượt chi phí điều phối.
- **Coding Song Song:** Sử dụng Herdr orchestration và worktrees riêng biệt cho từng worker; giao việc kèm task tracking, nhận `worker_done` và thực hiện review độc lập trên bản đã tích hợp.
- **Sửa Tài Liệu Đơn Giản:** Đọc code/hướng dẫn liên quan, kiểm tra link tài liệu và câu lệnh mẫu; không dựng thêm agent hay MCP cồng kềnh khi không cần thiết.

### 9.3. Báo Cáo Bắt Buộc Khi Hoàn Thành Task (`worker_done`)
Mỗi worker khi báo cáo hoàn thành nhiệm vụ bắt buộc phải đính kèm:
1. **Tài nguyên đã dùng:** Tên công cụ/skill/CLI/tài liệu, mục đích sử dụng và kết quả cụ thể.
2. **Bằng chứng khách quan:** Log lệnh/stdout thực tế, đường dẫn artifact, span/trace ID hoặc kết quả kiểm tra thực nghiệm (UI screenshot, test output).
3. **Nếu không dùng tài nguyên bổ sung:** Nêu rõ lý do cụ thể gắn liền với tính chất công việc.
4. **An toàn dữ liệu:** Tuyệt đối không đưa API keys, JWT tokens hoặc dữ liệu nhạy cảm vào bằng chứng báo cáo.

### 9.4. Trách Nhiệm Thẩm Định & Giới Hạn Chi Phí
- **Reviewer:** Kiểm tra nghiêm ngặt phần bằng chứng tài nguyên; nếu thiếu bằng chứng thực tế, yêu cầu worker bổ sung, tuyệt đối không phê duyệt hoặc đóng task sớm.
- **Tiêu chí tối ưu:** Chọn công cụ theo chất lượng, thời gian và chi phí; không ép buộc nạp mọi skill hay tạo agent tràn lan cho việc nhỏ. Nếu công cụ không khả dụng, nêu rõ nguyên nhân và áp dụng phương án thay thế khả thi.
- **Vai trò điều phối:** Antigravity Coordinator là đầu mối điều phối duy nhất; Herdr là lớp runtime đa tác tử chính. Tuân thủ nghiêm ngặt PRD, bảo mật và thẩm quyền được giao.

---

## 10. MULTI-AGENT TEAM COLLABORATION & DELEGATION MANDATE (QUY CHUẨN PHỐI HỢP ĐA TÁC TỬ)

Quy chuẩn bắt buộc về phối hợp đa tác tử áp dụng cho toàn bộ AI agents và kỹ sư đóng góp vào **VeriScholar**:

### 10.1. Nguyên Tắc Cấm Tự Thực Hiện Đơn Độc (Zero Solo-Work Invariant)
1. **Kiểm tra đội ngũ trước khi hành động:**
   - Trước khi bắt đầu bất kỳ nhiệm vụ nào có quy mô từ 2 bước trở lên, Coordinator/CTO bắt buộc phải kiểm tra trạng thái các tác tử đang chạy (`herdr agent list`, `herdr pane list`, hoặc `manage_subagents list`).
2. **Bắt buộc phân rã và giao việc theo đúng chuyên môn & rules:**
   - **Tuyệt đối KHÔNG ĐƯỢC** một mình tự thực hiện trọn gói khi trong phiên làm việc đang có các AI chuyên trách (`backend`, `frontend`, `reviewer`) hoạt động hoặc ở trạng thái sẵn sàng (`idle` / `done`).
   - Mọi tác vụ Python/FastAPI/Pydantic/PostgreSQL/ONNX NLI/Pytest $\rightarrow$ **Giao cho Backend Specialist**.
   - Mọi tác vụ React/Vite/Tailwind CSS/TypeScript/Vitest/Oxlint/Web UI $\rightarrow$ **Giao cho Frontend Specialist**.
   - Mọi tác vụ thẩm định mã nguồn độc lập, audit git diff, đánh giá kiến trúc, kiểm tra Quality Gate, chạy benchmark suite $\rightarrow$ **Giao cho Lead Reviewer**.
3. **Không lấn sân (No Overstepping):**
   - Coordinator chỉ đóng vai trò phân rã bài toán, giao việc, đôn đốc và tổng hợp kết quả nghiệm thu cuối cùng.
   - Không được tự ý sửa mã nguồn thuộc phạm vi của chuyên gia khác trừ khi tác tử đó gặp sự cố bất khả kháng hoặc cần can thiệp xử lý xung đột tích hợp liên miền sau khi các bên đã bàn giao.

### 10.2. Quy Chuẩn Lệnh Giao Việc (Prompt Delegation Protocol)
Mỗi lệnh giao việc cho tác tử khác (`herdr agent prompt <target> "..."` hoặc `invoke_subagent`) phải tuân thủ chặt chẽ cấu trúc 4 phần:
1. **Mục tiêu & Ngữ cảnh (Goal & Context):** Mô tả rõ ràng mục tiêu cần đạt, ngữ cảnh nghiệp vụ và nhánh git hiện tại.
2. **Phạm vi tác động (File Scope):** Liệt kê chính xác các file/thư mục thuộc trách nhiệm xử lý.
3. **Lệnh kiểm thử & công cụ bắt buộc:** Chỉ định rõ câu lệnh linter, format và test suite mà tác tử phải chạy để tự chứng minh tính đúng đắn.
4. **Tiêu chí hoàn thành (Definition of Done - DoD):** Nêu rõ các điều kiện tiên quyết để tác tử được phép báo cáo hoàn thành (`worker_done`).

### 10.3. Cơ Chế Thẩm Định & Nghiệm Thu Chéo (Peer Review & Gatekeeping)
1. **Không tự chứng nhận (No Self-Certification):**
   - Người viết code không được tự duyệt code của mình.
   - Mọi thay đổi từ `backend` hoặc `frontend` đều phải chuyển qua `reviewer` để audit độc lập trước khi Coordinator báo cáo cho User.
2. **Bằng chứng khách quan bắt buộc:**
   - Báo cáo hoàn thành chỉ được chấp thuận khi đi kèm log kiểm thử thực tế (100% tests passed, 0 linter warnings, 0 type errors).
   - Nếu phát hiện vi phạm kiến trúc, linter hoặc thiếu test, Reviewer phải từ chối nghiệm thu và yêu cầu tác tử phụ trách khắc phục triệt để.

---

## 11. MONOREPO ENVIRONMENT VARIABLES & SECRETS ARCHITECTURE (QUY CHUẨN QUẢN TRỊ FILE .ENV)

Nhằm triệt tiêu vĩnh viễn sự nhầm lẫn giữa các file `.env` và ngăn chặn tình trạng cấu hình bị phân mảnh (Configuration Drift) giữa các AI agents trong quá trình phát triển, toàn bộ dự án tuân thủ nghiêm ngặt các thiết chế kiến trúc sau:

### 11.1. Bản Đồ Phân Định Vị Trí & Trách Nhiệm (Directory & Ownership Map)
1. **Monorepo Root Master `.env` (`/home/VeriScholar/Workspace/VeriScholar/.env`):**
   - **Trách nhiệm:** Lưu trữ **TOÀN BỘ** bí mật hệ thống (Secrets), cấu hình kết nối CSDL PostgreSQL/pgvector, API Keys nhà cung cấp AI (OpenAI, Cohere, Azure Document Intelligence, Exa, Langfuse), cấu hình máy chủ Uvicorn (`HOST`, `PORT`, `DEBUG`), tham số Logging, JWT Token Secrets, SMTP Mailer, và Dynamic DNS (`DUCKDNS_DOMAIN`, `DUCKDNS_TOKEN`).
   - **Thẩm quyền:** Là **Single Source of Truth vật lý DUY NHẤT** cho toàn bộ Backend (`apps/api`), Workers (`arq`), Scripts (`scripts/eval`, `scripts/benchmark`), DevOps (`docker-compose`), và Systemd Service (`verischolar-api.service`).
2. **Backend Symlink (`apps/api/.env`):**
   - **Trách nhiệm:** Đóng vai trò cầu nối tương thích cho các công cụ chạy trực tiếp bên trong thư mục `apps/api`.
   - **Cơ chế:** Bắt buộc phải là một **Relative Symlink** trỏ về root: `apps/api/.env -> ../../.env`.
   - **Nghiêm cấm:** Tuyệt đối **CẤM** xóa symlink để tạo file vật lý riêng tại `apps/api/.env`. Mọi thao tác ghi vào `apps/api/.env` bản chất là ghi trực tiếp vào root `.env`.
3. **Frontend Client Config (`apps/web/.env`):**
   - **Trách nhiệm:** Chỉ phục vụ tiến trình build và runtime của trình duyệt web (Vite/React).
   - **Phạm vi biến:** **CHỈ CHỨA** các biến công khai có tiền tố `VITE_*` (ví dụ: `VITE_API_BASE_URL`, `VITE_API_PREFIX`, `VITE_APP_TITLE`, `VITE_MAX_UPLOAD_SIZE_BYTES`).
   - **Cô lập an ninh (Security Boundary):** Tuyệt đối **CẤM** đưa bất kỳ bí mật máy chủ nào (`DATABASE_URL`, API Keys, JWT Secret, Token) vào `apps/web/.env` vì Vite sẽ đóng gói công khai vào file JavaScript tĩnh tải về máy người dùng.

### 11.2. Bốn Bất Biến Kiến Trúc (Architectural Invariants)
- **Invariant 1 — Zero-Drift Single Source of Truth:**
  Khi cần thêm, sửa hoặc xóa bất kỳ biến môi trường nào cho CSDL, AI Models, Logging hoặc Third-party APIs, AI Agent **CHỈ ĐƯỢC PHÉP** chỉnh sửa file `/home/VeriScholar/Workspace/VeriScholar/.env`. Không được tạo file phụ trùng lặp.
- **Invariant 2 — Symlink Preservation Invariant:**
  Trước khi hoàn thành nhiệm vụ, AI Agent / Reviewer phải xác nhận `apps/api/.env` vẫn là symlink (`ls -l apps/api/.env` hiển thị `-> ../../.env`). Nếu symlink bị gãy hoặc bị thay thế bằng file vật lý, phải khôi phục ngay: `cd apps/api && ln -sf ../../.env .env`.
- **Invariant 3 — Frontend Secret Isolation Invariant:**
  Không bao giờ gộp cấu hình backend vào `apps/web/.env`. Mọi biến trong `apps/web/.env` phải bắt đầu bằng `VITE_`.
- **Invariant 4 — Service Synchronicity Invariant:**
  File dịch vụ systemd `/etc/systemd/system/verischolar-api.service` luôn trỏ trực tiếp đến `EnvironmentFile=/home/VeriScholar/Workspace/VeriScholar/.env`. Khi cập nhật biến môi trường cốt lõi, Agent phải thực hiện `sudo systemctl restart verischolar-api` để nạp cấu hình mới.

### 11.3. Bảng Kiểm Tra Nhanh Dành Cho AI Agent (Pre-Commit Environment Checklist)
- [ ] Biến môi trường mới của backend đã được thêm vào root `/home/VeriScholar/Workspace/VeriScholar/.env`?
- [ ] Đã thêm biến mẫu tương ứng (ẩn key thật) vào `.env.example` để chia sẻ cho team?
- [ ] File `apps/api/.env` vẫn giữ nguyên trạng thái relative symlink (`apps/api/.env -> ../../.env`)?
- [ ] Không có API Key hoặc Secret nào bị rò rỉ vào `apps/web/.env` hoặc git commit?
- [ ] Service `verischolar-api` đã được restart và phản hồi `200 OK` tại `/health`?

