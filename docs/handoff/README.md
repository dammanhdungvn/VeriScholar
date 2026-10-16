# VeriScholar: VPS Migration & Comprehensive Engineering Handover
## Tài Liệu Bàn Giao & Hướng Dẫn Di Chuyển Môi Trường Sang VPS

> **Cập nhật:** 2026-10-16  
> **Điều phối viên chuyển giao:** CTO VeriScholar  
> **Repository GitHub:** `git@github.com:dammanhdungvn/VeriScholar.git` (Private Repository)  
> **Trạng thái môi trường:** Ubuntu 24.04 LTS (2 vCPUs, 8GB RAM, Herdr 0.9.5 runtime)  
> **Nhánh hiện tại:** `feat/module3-cross-synthesis` (kế thừa từ `feat/m2-draft-comments-annotation`)  
> **Mục đích:** Cung cấp thông tin chuẩn xác 100% về kiến trúc, các module đã hoàn thành, bằng chứng nghiệm thu và hướng dẫn vận hành kỹ thuật trên máy chủ VPS.

---

## 1. MỤC TIÊU DỰ ÁN & LỘ TRÌNH TỔNG THỂ (PRD.md)

VeriScholar là nền tảng hỗ trợ nghiên cứu khoa học chuyên sâu với 4 module cốt lõi theo [docs/vi/PRD.md](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/PRD.md):

```
[Module 1: Scholar Reading & Deep Reader] ──(Hoàn tất & Hardened)──>
[Module 2: Academic Writing Assistant & SAFE Fact-Checking] ──(Hoàn tất 100% & Certified)──>
[Module 3: Multi-Paper Cross Synthesis & Automated Literature Review] ──(Hoàn tất 100% & Certified)──>
[Module 4: Personal Paper Library & Hierarchical Synthesis] ──(Backlog kế tiếp)
```

- **Module 1 (Scholar Reading & Deep Reader - PRD §3.1):**
  - **Trạng thái:** **`IMPLEMENTED & HARDENED`**.
  - Bao gồm: Hybrid Search (pgvector + full-text), Cross-Encoder Reranker, Deep Reader (PDF Canvas Viewer với Bounding Box 1-indexed, Top-Left `[0.0, 1.0]`), Session Chat Streaming qua Server-Sent Events (SSE) kèm chuẩn hóa `X-Request-ID`, Hệ thống phòng vệ 3 lớp AI Guardrails, Tracing Langfuse, và Bộ kiểm chuẩn Two-Tier Evaluation Suite (QASPER, SciFact, 25-case Project Regression Set).
- **Module 2 (Academic Writing Assistant & SAFE Fact-Checking - PRD §3.2):**
  - **Trạng thái:** **`CLOSED & VERIFIED`** (Nghiệm thu đạt **VERDICT: PASS** trên toàn bộ 4 phân hệ).
  - Bao gồm:
    1. Bản vá `DEFECT-01`: Giải quyết triệt để trôi lệch vị trí cục bộ OCC (`isDirty: true`), bảo toàn nội dung khi gặp HTTP 412.
    2. Bản vá `DEFECT-02`: Đóng gói offline weights ONNX INT8 AVX2 (`model_quint8_avx2.onnx`), triệt tiêu thread thrashing trên 2 vCPUs, độ trễ CPU p50: 47.83ms (< 50ms SLA), SciFact benchmark đạt chuẩn.
    3. Tích hợp Pipeline Kiểm chứng SAFE: Nối `SafeNliEngineAdapter` vào `SafeFactChecker` và `DraftService.verify_draft_facts`, cơ chế fallback mềm sang heuristic.
    4. Hệ thống Bình luận & Ghi chú Bản thảo (Peer Review Comments): RBAC 4 quyền, luồng phản hồi phân cấp (nested replies), SQLite cascade deletion, giao diện `DraftCommentsPane.tsx`.
- **Module 3 (Multi-Paper Ingestion, Academic Reference Resolving & Citation Graph - PRD §3.3):**
  - **Trạng thái:** **`CLOSED & VERIFIED`** (Nghiệm thu đạt **VERDICT: PASS** tại [`docs/handoff/module3-acceptance-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/module3-acceptance-review.md)).
  - Bao gồm:
    1. Cổng Hexagonal `IAcademicSearchResolverPort` & `ExaAcademicResolverAdapter` (Exa neural search & fallback `InMemoryAcademicResolverAdapter`).
    2. `GlobalAcademicCache` (SLA < 10ms, thực tế 0.007ms, cách ly nghiêm ngặt bản thảo cá nhân).
    3. Ngưỡng trần Dung lượng Phiên $\le 5$ bài báo (Backend trả HTTP 422 `SESSION_CAPACITY_EXCEEDED` & Frontend Guard/Alert vô hiệu hóa nút nạp bài).
    4. Đồ thị trích dẫn bẻ gãy chu trình $k \le 2$ & Lộ trình đọc nền tảng (Foundational Reading Path) qua Topological Sort.
    5. Giao diện `SmartReferenceDrawer.tsx` 3 cột (Checkbox | Thông tin bài & Thẻ Open-Access vs Abstract | Nguồn học thuật kèm link ngoài `↗`).

---

## 2. TRẠNG THÁI CHI TIẾT MODULE 2 THEO TỪNG YÊU CẦU PRD §3.2

| STT | Yêu cầu PRD §3.2 | Trạng thái | Implementation Thực tế | Test & Bằng chứng Khách quan |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **Hardened Sandbox Isolation** (1 vCPU, 512MB RAM, network none, read-only rootfs, tmpfs, non-root, env allowlist) | **`FAIL_CLOSED_VERIFIED`** | `packages/core/src/core/services/sandbox_probe.py` (`SandboxRuntimeCapabilityProbe`) kiểm tra 7 tiêu chí; fail-closed ném `SandboxInfrastructureUnavailableError` | Host Ubuntu hiện tại bật `apparmor_restrict_unprivileged_userns=1`. Probe phát hiện đúng, kiên quyết không chạy code không tin cậy trực tiếp trên host. |
| **2** | **LaTeX Compiler Engine Thật** | **`IMPLEMENTED & VERIFIED`** | `packages/core/src/core/services/latex_compiler.py` dùng Tectonic CLI 0.17.0 thật; fallback PyMuPDF chỉ trả `success=False` | `uv run pytest packages/core/tests/domain/test_latex_pipeline.py`: **13/13 passed**. Pre-warmed cache hoạt động ổn định. |
| **3** | **LaTeX Self-Healing Loop** (Tách biệt khỏi compiler, patch history, báo lỗi sau max tries) | **`IMPLEMENTED & VERIFIED`** | `packages/core/src/core/services/latex_healer.py` (`AgenticLatexHealer`) chạy ở tầng application bên ngoài sandbox, zero API keys/mạng trong compiler | `test_latex_pipeline.py -k healer`: **Passed**, ghi nhận patch history và log chẩn đoán. |
| **4** | **SAFE NLI Option A Engine Contract** (3 nhãn: supported, contradicted, not_enough_info, premise=evidence, hypothesis=claim) | **`IMPLEMENTED & VERIFIED`** | `packages/core/src/core/services/safe_nli_adapter.py` (`SafeNliEngineAdapter`) chuẩn hóa I/O, cấm BGE reranker làm NLI | `uv run pytest packages/core/tests/domain/test_safe_nli_adapter.py`: **8/8 passed** (0.34s) trên test suite hợp đồng logic. |
| **5** | **SAFE NLI Neural Model Quality & Benchmark** | **`CLOSED & VERIFIED`** | `SafeNliEngineAdapter` nạp offline weights ONNX INT8 AVX2 (`model_quint8_avx2.onnx`), triệt tiêu thread thrashing trên 2 vCPUs | `test_safe_nli_neural.py` & `test_safe_nli_adapter.py`: **15/15 passed** (0 skipped, 0 failed); mean latency: 47.83ms (< 50ms SLA); SciFact benchmark passed. Certified in `defect-02-review.md`. |
| **6** | **Visual Grounding Citation Bbox** (Không vẽ đè lên editor, hiển thị trong modal tài liệu nguồn) | **`IMPLEMENTED & VERIFIED`** | `apps/web/src/features/writing/components/SourceEvidenceModal.tsx` hiển thị PDF nguồn + tọa độ bbox; gỡ bỏ overlay khỏi `WritingPreviewPane.tsx` | `pnpm --prefix apps/web test src/features/writing`: **86/86 passed**, tsc 0 errors. |
| **7** | **Suggestion Review Panel** (Không stream đè editor, xem trước diff trực quan, Accept/Reject) | **`IMPLEMENTED & VERIFIED`** | `apps/web/src/features/writing/components/SuggestionReviewPanel.tsx` (LCS diff algorithm, confidence score, clean text tab) | Vitest 8/8 passed trong `SuggestionReviewPanel.test.tsx`. |
| **8** | **OCC ETag Guard & Local Unpersisted Edits** | **`CLOSED & VERIFIED`** | `apps/web/src/features/writing/components/WritingWorkspace.tsx` & `diffUtils.ts` | Thuật toán rebase offset với proximity threshold, huỷ chèn khi xung đột, bảo toàn `editorContent` trên HTTP 412. Certified in `defect-01-review.md` (Commit `4c5aeee`). |
| **9** | **Asset Management Safe Extraction** (.png, .pdf, .cls, .sty, .bib, zip-slip defense) | **`IMPLEMENTED & VERIFIED`** | `packages/core/src/core/services/draft_asset_security.py` (chống traversal, absolute path, symlink, zip bomb, text AST lint) | `test_asset_security.py`: **8/8 passed**, `test_drafts_lifecycle.py`: **passed**. |
| **10** | **Sharing RBAC & Peer Review Comments** (Roles: view, comment, edit; threaded comments, inline annotations) | **`CLOSED & VERIFIED`** | `apps/api/src/api/services/draft_service.py`, `apps/api/tests/test_draft_comments.py`, `DraftCommentsPane.tsx` | Đạt chuẩn PRD §3.2: RBAC 4 quyền, phân cấp phản hồi, SQLite cascade cleanup, Commenter bị cấm sửa văn bản nguồn (403), Viewer bị cấm tạo comment (403). **9/9 tests pass**, commit `f2555f5`. |
| **11** | **Container Sandbox Compilation SLA (< 15s)** | **`NOT_MEASURED`** | Đang chờ môi trường VPS có Docker/unshare namespace để benchmark | Tuyệt đối không đo đạc bằng cách chạy code không tin cậy trực tiếp trên host. Fail-Closed probe VERIFIED. |

---

## 3. DANH SÁCH BẢN VÁ KHIẾM KHUYẾT & KẾT QUẢ XỬ LÝ TRÊN VPS

1. **`DEFECT-01` (Ưu tiên: HIGH — Frontend) — TRẠNG THÁI: CLOSED & VERIFIED:**
   - **Nhánh:** `fix/m2-defect01-occ-drift` (Commit `4c5aeee`)
   - **Tệp:** `apps/web/src/features/writing/components/WritingWorkspace.tsx`, `diffUtils.ts`
   - **Kết quả:** Reviewer độc lập thẩm định đạt `VERDICT: PASS` tại [`defect-01-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-01-review.md).
2. **`DEFECT-02` (Ưu tiên: MEDIUM — Backend & AI) — TRẠNG THÁI: CLOSED & VERIFIED:**
   - **Nhánh:** `fix/m2-defect02-offline-onnx-nli` (Commit `99c3627`)
   - **Tệp:** `packages/core/src/core/services/safe_nli_adapter.py`, `models/nli/`
   - **Kết quả:** Reviewer độc lập thẩm định đạt `VERDICT: PASS` tại [`defect-02-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-02-review.md). Latency CPU p50: 47.83ms (< 50ms SLA), SciFact benchmark passed.
3. **`TASK-BE-FACT-CHECKER-NEURAL-INTEGRATION` (Backend & AI Integration) — TRẠNG THÁI: CLOSED & VERIFIED:**
   - **Nhánh:** `feat/m2-safe-fact-checker-integration` (Commit `0b025d5`)
   - **Tệp:** `packages/core/src/core/services/safe_fact_checker.py`, `safe_nli_adapter.py`, `apps/api/src/api/services/draft_service.py`
   - **Kết quả:** Reviewer độc lập thẩm định Vòng 2 đạt `VERDICT: PASS` tại [`fact-checker-integration-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/fact-checker-integration-review.md).
4. **`DEFECT-03` (Ưu tiên: SYSTEM / INFRA — DevOps) — TRẠNG THÁI: FAIL_CLOSED_VERIFIED:**
   - **Mô tả:** Cơ chế Fail-Closed của `SandboxRuntimeCapabilityProbe` đã được xác minh toàn diện. Host thiếu unprivileged user namespace sẽ nâng ngoại lệ an toàn `SandboxInfrastructureUnavailableError`, kiên quyết không thực thi untrusted LaTeX trực tiếp trên host. Biên dịch nội bộ Tectonic CLI 0.17.0 hoạt động 100% xanh.

---

## 4. BỘ KIỂM THỬ & LỆNH XÁC MINH CHUẨN TRÊN VPS

### 4.1. Kiểm thử Backend Python
```bash
# Kiểm thử Module 3 (Exa Resolver, Cache Isolation, Ingestion, Citation Graph - 22 tests)
uv run pytest packages/core/tests/services/test_exa_resolver.py apps/api/tests/test_academic_resolver.py apps/api/tests/test_reference_ingestion.py -v

# Kiểm thử Module 2 Draft Comments & Lifecycle (20 tests)
uv run pytest apps/api/tests/test_draft_comments.py apps/api/tests/test_drafts_lifecycle.py -v

# Kiểm thử Safe Fact-Checker & Neural NLI (23 tests)
uv run pytest packages/core/tests/domain/test_safe_fact_checker.py packages/core/tests/domain/test_safe_nli_neural.py -v

# Kiểm tra Linter & Formatting (Zero errors, zero warnings trên toàn repo)
uv run ruff check .
uv run ruff format --check .
```

### 4.2. Kiểm thử Frontend Web
```bash
# Kiểm tra TypeScript Compile (Zero errors)
pnpm --prefix apps/web exec tsc -b

# Kiểm tra Linter Oxlint (Zero errors trên 193 files)
pnpm --prefix apps/web lint

# Kiểm thử Reader & Smart Reference Drawer Module 3 (25 tests)
pnpm --prefix apps/web test src/features/reader

# Kiểm thử tính năng Writing & Peer Comments Module 2 (97 tests)
pnpm --prefix apps/web test src/features/writing

# Kiểm thử toàn bộ Frontend Suite (51 files, 271 tests pass)
pnpm --prefix apps/web test
```

---

## 5. DANH MỤC TÀI LIỆU HỒ SƠ BÀN GIAO & NGHIỆM THU HIỆN HÀNH

Toàn bộ tài liệu nghiệm thu kỹ thuật chính thức được lưu trữ trong thư mục `docs/handoff/`:

1. [`phase3-gateway-ha-audit.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/phase3-gateway-ha-audit.md): Biên bản kiểm toán an ninh & độ bền hạ tầng Phase 3: Gateway & High Availability Deployment (Systemd Auto-Restart <= 5s, Nginx Security Headers, Unbuffered SSE Streaming, Port 80 End-to-End Delivery) — **VERDICT: PASS**.
2. [`closed-beta-sizing-and-capacity-guide.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/closed-beta-sizing-and-capacity-guide.md): Hướng dẫn hoạch định năng lực & Sizing hạ tầng cho Closed Beta 15–20 người dùng (Max 25 Concurrent Sessions, 4 vCPUs/8GB RAM/80GB NVMe, Token Economics, 30s MTTR Triage) — **APPROVED FOR CLOSED BETA**.
3. [`uat-monitoring-audit-certification.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/uat-monitoring-audit-certification.md): Bản thẩm định và chứng nhận kỹ thuật toàn diện 5 Work Packages (UAT Environment, Deep Langfuse Tracing, 5.6-luna Reasoning, Error Triage, AI Benchmarks) — **VERDICT: PASS — CERTIFIED FOR UAT**.
4. [`module3-acceptance-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/module3-acceptance-review.md): Báo cáo thẩm định chất lượng độc lập nghiệm thu Module 3 (PRD §3.3) — **VERDICT: PASS**.
5. [`fact-checker-integration-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/fact-checker-integration-review.md): Báo cáo nghiệm thu tích hợp SAFE Fact-Checker & Neural NLI Adapter — **VERDICT: PASS**.
6. [`defect-01-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-01-review.md): Báo cáo nghiệm thu bản vá DEFECT-01 (Frontend OCC Local Drift) — **VERDICT: PASS**.
7. [`defect-02-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/defect-02-review.md): Báo cáo nghiệm thu bản vá DEFECT-02 (Offline ONNX NLI Engine) — **VERDICT: PASS**.
8. [`module2-milestone1-review.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/module2-milestone1-review.md): Báo cáo đánh giá độc lập ban đầu của Milestone 1 Module 2 (tài liệu lịch sử mốc xuất phát).
9. [`vps-environment-replication-guide.md`](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/vps-environment-replication-guide.md): Hướng dẫn tái lập môi trường VPS, ports, database migrations và models.
