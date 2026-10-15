# Kế Hoạch Hoàn Thiện & Nghiệm Thu Module 2 (Bản Cập Nhật Chuẩn Hóa Kỹ Thuật)
## Academic Writing Assistant & SAFE Fact-Checking (PRD §3.2)

> **Cập nhật:** 2026-10-15  
> **Điều phối viên:** Antigravity Coordinator (`term_ecd5fad9`)  
> **Đơn vị thực thi:** Backend + AI Specialist (`term_48dcdcf9`), Frontend Specialist (`term_4b8241e6`), Lead Quality Reviewer `gg16` (`term_c3228535`)  
> **Snapshot Milestone 1 Audited:** [`fca342cd3f34129560d101b89a95d764561f264b`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar)  
> **Báo cáo nghiệm thu độc lập:** [`module2-milestone1-review.md`](file:///home/dammanhdungvn/Downloads/Workspace/Profile_Antigravity/dungdamgg16/.gemini/antigravity-cli/brain/22e8ad62-c5a8-4174-917b-06ea83ade426/module2-milestone1-review.md)  
> **Phán quyết Gate 1:** **`CONDITIONAL ACCEPTANCE / PENDING REMEDIATION`** (Chưa công bố PASS hoàn toàn)

---

## 1. MA TRẬN ĐỐI CHUẨN NGHIỆM THU GATE 1 (PRD §3.2)

| STT | Hạng mục kiểm định | Implementation Thực tế | Phương thức & Bằng chứng Khách quan | Trạng thái (Reviewer Verdict) |
| :---: | :--- | :--- | :--- | :---: |
| **1.1** | **Sandbox Capability Probe (Fail-Closed)** | `packages/core/src/core/services/sandbox_probe.py` | Kiểm tra Linux host thực tế: phát hiện 5 rào cản bảo mật, trả về `BLOCKED_INFRASTRUCTURE`, raises `SandboxInfrastructureUnavailableError` | **PASS** |
| **1.2** | **Containerized LaTeX Compilation & SLA** | `packages/core/src/core/services/latex_compiler.py` | Host chặn unprivileged user namespace (`apparmor_restrict_unprivileged_userns=1`), `docker.sock` denied | **BLOCKED**<br>*(SLA: `NOT_MEASURED`)* |
| **2.1** | **SAFE NLI Contract Compliance** | `packages/core/src/core/services/safe_nli_adapter.py` | 8/8 unit tests pass trên adapter contract: 3 nhãn Option A, premise=evidence, hypothesis=claim, explanation $\le 2$ câu, cấm CoT | **PASS** |
| **2.2** | **SAFE NLI Real Neural Inference & Accuracy** | `packages/core/src/core/services/safe_nli_adapter.py` | Trọng số mạng nơ-ron chưa đóng gói offline; `classify()` hiện dùng heuristic/regex rule-engine | **PENDING**<br>*(SLA/Acc: `NOT_MEASURED`)* |
| **3.1** | **Non-destructive AI Staging Panel** | `apps/web/src/features/writing/components/SuggestionReviewPanel.tsx` | Vitest 8/8 pass: Đề xuất AI đưa vào review modal độc lập, so sánh diff LCS trực quan, không stream đè lên editor | **PASS** |
| **3.2** | **OCC & Local Unpersisted Edits** | `apps/web/src/features/writing/components/WritingWorkspace.tsx` | Kịch bản người dùng gõ thêm chưa autosave: ETag server vẫn khớp (v1) $\rightarrow$ HTTP 200 làm chèn đè/cắt lệch offset văn bản vừa gõ | **FAIL / DEFECT-01** |
| **4.1** | **Toàn vẹn Bộ kiểm thử Đơn vị & Tích hợp** | `packages/core/tests/domain/`<br>`apps/web/src/features/writing/` | `pytest`: 21/21 passed, `vitest`: 74/74 passed (12 test suites) | **PASS** |
| **4.2** | **Kiểm tra Biên dịch Frontend TypeScript** | `apps/web` | `pnpm --prefix apps/web exec tsc -b`: 0 errors | **PASS** |

---

## 2. DANH SÁCH KHIẾM KHUYẾT & ĐIỀU KIỆN ĐÓNG LỖI (DEFECT REMEDIATION)

### DEFECT-01: Lỗ hổng Trôi lệch Offset khi Chấp nhận Đề xuất Cũ (OCC Local Drift)
- **Mức độ:** `HIGH`
- **Owner phân công:** Frontend Specialist (`term_4b8241e6`)
- **Tệp mã nguồn:** [`apps/web/src/features/writing/components/WritingWorkspace.tsx`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/apps/web/src/features/writing/components/WritingWorkspace.tsx#L212-L257)
- **Cơ chế lỗi:** Header `If-Match: "v{version}"` chỉ phát hiện xung đột khi server version đã tăng. Nếu người dùng gõ thêm ký tự cục bộ (`isDirty: true`) mà chưa kích hoạt autosave, `draft.version` trên server vẫn là cũ. Khi bấm Accept, server trả về `HTTP 200 OK`, nhưng việc thay thế theo `cursor_start` cũ sẽ chèn đè làm mất hoặc cắt lệch các ký tự người dùng vừa gõ mới.
- **Điều kiện đóng lỗi (Closure Criteria):**
  1. Kiểm tra trạng thái `isDirty`: Tính toán độ lệch offset dời (`offset delta`) nếu vùng gõ nằm trước vị trí đề xuất, hoặc yêu cầu rebase trước khi chèn.
  2. Bắt lỗi `HTTP 412 Precondition Failed` (khi autosave đã chạy xong): Hiển thị thông báo xung đột trực quan và giữ nguyên suggestion + local edits, không nuốt lỗi vào console.

### DEFECT-02: Chưa Đóng Gói Trọng Số Mô Hình NLI Ngoại Tuyến (Missing Real NLI Checkpoint)
- **Mức độ:** `MEDIUM`
- **Owner phân công:** Backend Specialist (`term_48dcdcf9`)
- **Tệp mã nguồn:** [`packages/core/src/core/services/safe_nli_adapter.py`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/packages/core/src/core/services/safe_nli_adapter.py)
- **Cơ chế lỗi:** Adapter đã hoàn thành hợp đồng I/O và rule-based heuristic, nhưng chưa tích hợp weights ONNX/PyTorch thực tế của `cross-encoder/nli-deberta-v3-small` để suy diễn nơ-ron ngoại tuyến.
- **Điều kiện đóng lỗi (Closure Criteria):**
  1. Đóng gói mô hình ONNX INT8 quantized vào thư mục `models/` phục vụ inference độc lập không cần internet.
  2. Xây dựng smoke test kiểm tra inference nơ-ron thực tế trên 3 nhãn logic và chuẩn bị harness đo benchmark SciFact.

### DEFECT-03: Rào Cản Hạ Tầng Host Sandbox
- **Mức độ:** `LOW` (Hệ thống đã Fail-Closed an toàn, không rò rỉ bảo mật)
- **Mô tả:** Nhân Linux máy chủ host bật `apparmor_restrict_unprivileged_userns=1` và không có quyền Docker socket.
- **Biện pháp:** Giữ nguyên trạng thái `BLOCKED_INFRASTRUCTURE`, raises `SandboxInfrastructureUnavailableError`. SLA biên dịch container đánh dấu `NOT_MEASURED`.

---

## 3. LỘ TRÌNH TIẾP TỤC & PHÂN CÔNG ĐỘI NGŨ

- **Phát triển song song có điều kiện:**
  - **Backend Specialist (`term_48dcdcf9`):** Tiếp tục `task_0cc346c3c8b9` (Assets CRUD safe extraction & Sharing RBAC), đồng thời chuẩn bị phương án đóng gói weights NLI (Defect-02).
  - **Frontend Specialist (`term_4b8241e6`):** Hoàn tất `task_c528d15a5b60` (Assets Panel & Share Modal UI), sau đó ưu tiên vá dứt điểm **DEFECT-01** (OCC Local Drift) trước khi tái thẩm định Gate 1.
  - **Lead Quality Reviewer (`term_c3228535`):** Đã hoàn tất báo cáo [`module2-milestone1-review.md`](file:///home/dammanhdungvn/Downloads/Workspace/Profile_Antigravity/dungdamgg16/.gemini/antigravity-cli/brain/22e8ad62-c5a8-4174-917b-06ea83ade426/module2-milestone1-review.md) và sẵn sàng kiểm tra bản vá lỗi Defect-01 của Frontend.
