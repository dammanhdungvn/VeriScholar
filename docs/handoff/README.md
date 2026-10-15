# VeriScholar: VPS Migration & Comprehensive Engineering Handover
## Tài Liệu Bàn Giao & Hướng Dẫn Di Chuyển Môi Trường Sang VPS

> **Cập nhật:** 2026-10-15  
> **Điều phối viên chuyển giao:** Antigravity Coordinator (`term_ecd5fad9`)  
> **Repository GitHub:** `git@github.com:dammanhdungvn/VeriScholar.git` (Private Repository)  
> **Commit Cơ sở (origin/main):** [`fca342cd3f34129560d101b89a95d764561f264b`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar)  
> **Commit Mã Nguồn Đóng Gói (Module 2 WIP):** [`6156c91eef3550b07b3beba43fa0f4fe617da9fe`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar)  
> **Bối Cảnh Snapshot Thẩm Định:** Reviewer thực hiện đánh giá trên dirty working tree snapshot (trên nền commit `fca342c`). Toàn bộ thay đổi sau đó được đóng gói nguyên trạng vào commit `6156c91`. Trạng thái đối chiếu chéo post-commit: PENDING verification on VPS.  
> **Mục đích:** Đóng gói toàn bộ mã nguồn, cấu hình, dữ liệu kiểm thử, bằng chứng nghiệm thu và trạng thái công việc để tiếp tục phát triển trên máy chủ VPS mà không phải khảo sát hoặc lập kế hoạch lại từ đầu.

---

## 1. MỤC TIÊU DỰ ÁN & LỘ TRÌNH TỔNG THỂ (PRD.md)

VeriScholar là nền tảng hỗ trợ nghiên cứu khoa học chuyên sâu với 3 module cốt lõi:

```
[Module 1: Scholar Reading & Deep Reader] ──(Hoàn tất & Hardened)──>
[Module 2: Academic Writing Assistant & SAFE Fact-Checking] ──(Đang triển khai / Milestone 1 Reviewed)──>
[Module 3: Multi-Paper Cross Synthesis & Automated Literature Review] ──(Chưa bắt đầu)
```

- **Module 1 (Scholar Reading & Deep Reader):**
  - **Trạng thái:** **`IMPLEMENTED & HARDENED`**.
  - Bao gồm: Hybrid Search (pgvector + full-text), Cross-Encoder Reranker, Deep Reader (PDF Canvas Viewer với Bounding Box 1-indexed, Top-Left `[0.0, 1.0]`), Session Chat Streaming qua Server-Sent Events (SSE) kèm chuẩn hóa `X-Request-ID`, Hệ thống phòng vệ 3 lớp AI Guardrails, Tracing Langfuse, và Bộ kiểm chuẩn Two-Tier Evaluation Suite (QASPER, SciFact, 25-case Project Regression Set).
- **Module 2 (Academic Writing Assistant & SAFE Fact-Checking - PRD §3.2):**
  - **Trạng thái:** **`MILESTONE 1 IMPLEMENTED - CONDITIONAL REVIEW`** (Chi tiết ở Mục 2).
  - Tạm dừng mở rộng tính năng mới theo yêu cầu chuyển giao môi trường sang VPS.
- **Module 3 (Multi-Paper Cross Synthesis & Literature Review):**
  - **Trạng thái:** **`CHƯA BẮT ĐẦU (0% CODE)`**.
  - Tuyệt đối chưa kích hoạt mã nguồn hay schema của Module 3 cho tới khi Module 2 được nghiệm thu trọn vẹn trên VPS.

---

## 2. TRẠNG THÁI CHI TIẾT MODULE 2 THEO TỪNG YÊU CẦU PRD §3.2

| STT | Yêu cầu PRD §3.2 | Trạng thái | Implementation Thực tế | Test & Bằng chứng Khách quan |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **Hardened Sandbox Isolation** (1 vCPU, 512MB RAM, network none, read-only rootfs, tmpfs, non-root, env allowlist) | **`BLOCKED`** (Hạ tầng host)<br/>Logic probe: **`PASS`** | `packages/core/src/core/services/sandbox_probe.py` (`SandboxRuntimeCapabilityProbe`) kiểm tra 7 tiêu chí; fail-closed ném `SandboxInfrastructureUnavailableError` | Host Ubuntu hiện tại bật `apparmor_restrict_unprivileged_userns=1` và chặn `docker.sock`. Probe phát hiện đúng, không âm thầm fallback sang host. |
| **2** | **LaTeX Compiler Engine Thật** | **`IMPLEMENTED`** | `packages/core/src/core/services/latex_compiler.py` dùng Tectonic CLI thật; fallback PyMuPDF chỉ trả `success=False` | `uv run pytest packages/core/tests/domain/test_latex_pipeline.py`: **9/9 passed** (1.27s). |
| **3** | **LaTeX Self-Healing Loop** (Tách biệt khỏi compiler, patch history, báo lỗi sau max tries) | **`IMPLEMENTED`** | `packages/core/src/core/services/latex_healer.py` (`AgenticLatexHealer`) chạy ở tầng application bên ngoài sandbox, zero API keys/mạng trong compiler | `test_latex_pipeline.py -k healer`: **Passed**, ghi nhận patch history và log chẩn đoán. |
| **4** | **SAFE NLI Option A Engine Contract** (3 nhãn: supported, contradicted, not_enough_info, premise=evidence, hypothesis=claim) | **`IMPLEMENTED`** | `packages/core/src/core/services/safe_nli_adapter.py` (`SafeNliEngineAdapter`) chuẩn hóa I/O, cấm BGE reranker làm NLI | `uv run pytest packages/core/tests/domain/test_safe_nli_adapter.py`: **8/8 passed** (0.34s) trên test suite hợp đồng logic. |
| **5** | **SAFE NLI Neural Model Quality & Benchmark** | **`PENDING`**<br/>*(SLA/Acc: `NOT_MEASURED`)*<br/>**`DEFECT-02 OPEN`** | `SafeNliEngineAdapter` hoàn thành hợp đồng Option A (rule-engine/heuristic); mô hình suy diễn nơ-ron thực tế qua ONNX offline **CHƯA KIỂM CHỨNG** do chưa tải và đóng gói weights | 8/8 tests hợp đồng logic pass; benchmark chất lượng thực tế & SLA độ trễ suy diễn: `NOT_MEASURED` (chờ đóng gói weights ONNX INT8 trên VPS). |
| **6** | **Visual Grounding Citation Bbox** (Không vẽ đè lên editor, hiển thị trong modal tài liệu nguồn) | **`IMPLEMENTED`** | `apps/web/src/features/writing/components/SourceEvidenceModal.tsx` hiển thị PDF nguồn + tọa độ bbox; gỡ bỏ overlay khỏi `WritingPreviewPane.tsx` | `pnpm --prefix apps/web test src/features/writing`: **74/74 passed**, tsc 0 errors. |
| **7** | **Suggestion Review Panel** (Không stream đè editor, xem trước diff trực quan, Accept/Reject) | **`IMPLEMENTED`** | `apps/web/src/features/writing/components/SuggestionReviewPanel.tsx` (LCS diff algorithm, confidence score, clean text tab) | Vitest 8/8 passed trong `SuggestionReviewPanel.test.tsx`. |
| **8** | **OCC ETag Guard & Local Unpersisted Edits** | **`DEFECT-01 OPEN`** (Cần vá trên VPS) | `apps/web/src/features/writing/components/WritingWorkspace.tsx` (`If-Match: "v{version}"`) | Reviewer phát hiện: nếu người dùng gõ thêm chưa autosave, server ETag vẫn khớp (v1) $\rightarrow$ HTTP 200 làm chèn lệch offset (cắt đè văn bản mới gõ). |
| **9** | **Asset Management Safe Extraction** (.png, .pdf, .cls, .sty, .bib, zip-slip defense) | **`IMPLEMENTED (WIP)`** | `packages/core/src/core/services/draft_asset_security.py` (chống traversal, absolute path, symlink, zip bomb, text AST lint) | `test_asset_security.py`: **8/8 passed**, `test_drafts_lifecycle.py`: **passed**. |
| **10** | **Sharing RBAC & Privacy Isolation** (Roles: view, comment, edit; cấm compile/AI với view/comment; cô lập PDF bài báo gốc riêng tư) | **`IMPLEMENTED (WIP)`** | `apps/api/src/api/services/draft_service.py` & `apps/web/src/features/writing/components/DraftSharingModal.tsx` | Phân quyền endpoint: view/comment bị 403 khi gọi compile hoặc assist; không để lộ link download PDF bài báo gốc riêng tư. |
| **11** | **Container Sandbox Compilation SLA (< 15s)** | **`NOT_MEASURED`** | Đang chờ môi trường VPS có Docker/unshare namespace để benchmark | Tuyệt đối không đo đạc bằng cách chạy code không tin cậy trực tiếp trên host. |

---

## 3. DANH SÁCH KHIẾM KHUYẾT MỞ CẦN XỬ LÝ ĐẦU TIÊN TRÊN VPS

1. **`DEFECT-01` (Ưu tiên: HIGH — Frontend) — TRẠNG THÁI: OPEN:**
   - **Tệp:** `apps/web/src/features/writing/components/WritingWorkspace.tsx`
   - **Mô tả:** Khắc phục trôi lệch offset khi Accept đề xuất AI cũ trong lúc người dùng đã gõ thêm ký tự chưa autosave (ETag server vẫn khớp phiên bản cũ dẫn tới HTTP 200 cắt đè nội dung mới).
   - **Giải pháp:** Kiểm tra `isDirty`, tính toán delta dời vùng chèn, hoặc kích hoạt autosave sync trước khi mở panel đề xuất; bắt lỗi HTTP 412 hiển thị thông báo thay vì nuốt lỗi.
2. **`DEFECT-02` (Ưu tiên: MEDIUM — Backend & AI) — TRẠNG THÁI: OPEN:**
   - **Tệp:** `packages/core/src/core/services/safe_nli_adapter.py`
   - **Mô tả:** `SafeNliEngineAdapter` hiện mới chỉ hoàn tất tầng hợp đồng (Option A contract: 3 labels, premise=evidence, hypothesis=claim, heuristic rule-engine). Việc suy diễn thực tế bằng mạng nơ-ron qua ONNX offline **HOÀN TOÀN CHƯA KIỂM CHỨNG** do chưa tải và đóng gói trọng số (weights) của `cross-encoder/nli-deberta-v3-small`. Toàn bộ chỉ số độ chính xác (Accuracy/F1) và độ trễ suy diễn (Inference SLA) hiện ghi nhận là `NOT_MEASURED`.
   - **Giải pháp:** Tải weights checkpoint từ HuggingFace, export sang ONNX INT8 trong thư mục `models/nli/`, và xây dựng test suite suy diễn ngoại tuyến độc lập trên VPS.
3. **`DEFECT-03` (Ưu tiên: SYSTEM / INFRA — DevOps) — TRẠNG THÁI: BLOCKED (Hạ tầng):**
   - **Mô tả:** Cấu hình Docker daemon và quyền unprivileged user namespace trên VPS để kích hoạt compiler container sandbox thật sự đạt chuẩn PRD §3.2 (1 vCPU, 512MB RAM, `--network none`, `--read-only rootfs`, tmpfs).

---

## 4. BỘ KIỂM THỬ & LỆNH XÁC MINH CHUẨN TRÊN VPS

Sau khi kéo mã nguồn về VPS, chạy tuần tự các lệnh sau để xác nhận trạng thái toàn vẹn (Baseline Check):

### 4.1. Cài đặt Dependencies
```bash
# Python Workspace
uv sync --all-packages

# Frontend Web Workspace
pnpm --prefix apps/web install
```

### 4.2. Kiểm thử Backend Python
```bash
# Toàn bộ test suite backend (570 tests pass)
uv run pytest

# Chỉ kiểm thử Module 2 Core Domain (21 tests pass)
uv run pytest packages/core/tests/domain/test_safe_nli_adapter.py packages/core/tests/domain/test_latex_pipeline.py packages/core/tests/domain/test_asset_security.py

# Chỉ kiểm thử Module 2 Drafts Lifecycle (13 tests pass)
uv run pytest apps/api/tests/test_drafts_lifecycle.py

# Kiểm tra Linter & Formatting (Zero errors, zero warnings)
uv run ruff check .
uv run ruff format --check .
```

### 4.3. Kiểm thử Frontend Web
```bash
# Kiểm tra TypeScript Compile (Zero errors)
pnpm --prefix apps/web exec tsc -b

# Kiểm tra Linter Oxlint (Zero errors)
pnpm --prefix apps/web lint

# Kiểm thử tính năng Writing Module 2 (74 tests pass)
pnpm --prefix apps/web test src/features/writing

# Kiểm tra Production Build
pnpm --prefix apps/web build
```

---

## 5. DANH MỤC TÀI LIỆU HỒ SƠ BÀN GIAO ĐÍNH KÈM TRONG REPO

Toàn bộ tài liệu hỗ trợ đã được chuyển vào thư mục `docs/handoff/` để VPS có thể đọc ngoại tuyến:

1. [`vps-environment-replication-guide.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/handoff/vps-environment-replication-guide.md): Hướng dẫn chi tiết thiết lập môi trường VPS, ports, database migrations, Tectonic binary, models, và kế hoạch chuyển dữ liệu ngoài Git.
2. [`vps-ai-bootstrapping-prompt.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/handoff/vps-ai-bootstrapping-prompt.md): Prompt chuẩn hóa dành cho AI Assistant kế nhiệm trên VPS để tiếp quản tức thì.
3. [`module2-remediation-backlog-and-plan.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/handoff/module2-remediation-backlog-and-plan.md): Kế hoạch backlog chi tiết Module 2.
4. [`module2-milestone1-review.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/handoff/module2-milestone1-review.md): Báo cáo đánh giá độc lập đầy đủ của Lead Quality Reviewer `gg16` trên dirty working tree snapshot (trên nền commit base `fca342c`, tương ứng với mã nguồn đóng gói `6156c91`).
5. [`quota-aware-teamwork-and-handover-protocol.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/handoff/quota-aware-teamwork-and-handover-protocol.md): Quy trình điều phối đa tác tử và quản trị rủi ro hạn ngạch.
6. [`orchestration-state-snapshot.json`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/handoff/orchestration-state-snapshot.json): Bản sao lưu trạng thái điều phối lịch sử (đã khử sạch thông tin nhạy cảm và đường dẫn cục bộ).

---

## 6. BÁO CÁO RÀ SOÁT BẢO MẬT & XÁC MINH CÁC TỆP BỊ IGNORE

- **Kết quả rà soát Secrets:** Không phát hiện secrets trong phạm vi và bộ quy tắc đã quét (đã thực hiện quét regex đối với API keys, JWT secrets, private keys, certificates và tokens nhạy cảm trên toàn bộ git diff `fca342c..HEAD` và các file tài liệu). Không khẳng định an toàn tuyệt đối 100% ngoài phạm vi và bộ quy tắc đã quét.
- **Xác minh các tệp nhạy cảm và ignore không bị Git track đồng thời:**
  - Tệp cấu hình môi trường `.env`, `.env.*` (ngoại trừ `.env.example` đã khử toàn bộ giá trị bí mật): **Không bị Git track**.
  - Cơ sở dữ liệu SQLite/PostgreSQL `storage/verischolar.db`, `*.db`, `*.sqlite`, `*.sqlite3`: **Không bị Git track** (được bỏ qua bởi `.gitignore`).
  - Gói dữ liệu chuyển giao ngoài Git `verischolar_runtime_data.tar.gz` và `verischolar_runtime_data.tar.gz.sha256`: **Không bị Git track** (được bỏ qua bởi `.gitignore`).
  - Thư mục runtime agent `.agents/runtime/`: **Không bị Git track** (được bỏ qua bởi `.gitignore`).
  - Toàn bộ 29 kỹ năng (`.agents/skills/`) và tài liệu phân công (`.agents/teamwork/`): **Được Git track đầy đủ** theo đúng chỉ đạo.
  - Các tệp nhật ký `*.log`: **Không bị Git track**.
